"""Wako movie-only add-on routes for authorized Xtream and Stalker accounts.

Configuration is encrypted with Fernet. Set WAKO_CONFIG_SECRET to a stable
Fernet key before deployment; never commit that key or provider credentials.
"""
import base64
import json
import os
import re
from urllib.parse import urlencode, urljoin

import requests
from cryptography.fernet import Fernet, InvalidToken
from flask import Blueprint, abort, current_app, jsonify, redirect, request

wako_bp = Blueprint("wako_addon", __name__)
TIMEOUT = (5, 18)
USER_AGENT = "FluxStream-WakoAddon/1.0"

def _fernet():
    key = os.environ.get("WAKO_CONFIG_SECRET", "").strip()
    if not key:
        raise RuntimeError("WAKO_CONFIG_SECRET is not configured")
    try:
        return Fernet(key.encode("ascii"))
    except Exception as exc:
        raise RuntimeError("WAKO_CONFIG_SECRET must be a valid Fernet key") from exc

def _encrypt_config(config):
    raw = json.dumps(config, separators=(",", ":")).encode("utf-8")
    return _fernet().encrypt(raw).decode("ascii")

def _decrypt_config(token):
    try:
        raw = _fernet().decrypt(token.encode("ascii"))
        config = json.loads(raw.decode("utf-8"))
        return config if isinstance(config, dict) else None
    except (InvalidToken, ValueError, UnicodeError, json.JSONDecodeError):
        return None

def _clean_base(value):
    value = (value or "").strip()
    if not value:
        return ""
    if not re.match(r"^https?://", value, re.I):
        value = "https://" + value
    return value.rstrip("/")

def _valid_config(form):
    config = {
        "xtream_url": _clean_base(form.get("xtream_url")),
        "xtream_user": (form.get("xtream_user") or "").strip(),
        "xtream_pass": (form.get("xtream_pass") or "").strip(),
        "stalker_url": _clean_base(form.get("stalker_url")),
        "stalker_mac": (form.get("stalker_mac") or "").strip(),
    }
    if not ((config["xtream_url"] and config["xtream_user"] and config["xtream_pass"]) or
            (config["stalker_url"] and config["stalker_mac"])):
        raise ValueError("Enter a complete Xtream login or an authorized Stalker portal and MAC.")
    if config["stalker_mac"] and not re.fullmatch(r"[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}", config["stalker_mac"]):
        raise ValueError("Stalker MAC must use format AA:BB:CC:DD:EE:FF.")
    return config

def _json_get(url, headers=None, params=None):
    response = requests.get(url, headers=headers or {"User-Agent": USER_AGENT},
                            params=params, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()

def _movie_names(imdb_id):
    """Resolve an IMDb ID to a public movie title."""
    try:
        data = _json_get("https://v3-cinemeta.strem.io/meta/movie/" + imdb_id + ".json")
        meta = data.get("meta", {}) if isinstance(data, dict) else {}
        names = [meta.get("name", "")]
        if isinstance(meta.get("aliases"), list):
            names.extend(meta["aliases"])
        return [name for name in names if isinstance(name, str) and name.strip()]
    except Exception:
        return []

def _norm_title(value):
    value = str(value or "").lower()
    value = re.sub(r"\\(.*?\\)", " ", value)
    return re.sub(r"[^a-z0-9]+", "", value)

def _xtream_movies(config, imdb_id):
    base = config["xtream_url"]
    common = {"username": config["xtream_user"], "password": config["xtream_pass"]}
    params = dict(common, action="get_vod_streams")
    data = _json_get(base + "/player_api.php", params=params)
    if not isinstance(data, list):
        return []
    matches = []
    target = imdb_id.lower()
    names = [_norm_title(name) for name in _movie_names(imdb_id)]
    for item in data:
        if not isinstance(item, dict):
            continue
        ids = [str(item.get(k, "")).strip().lower() for k in
               ("stream_id", "imdb", "imdb_id", "tmdb", "tmdb_id")]
        # Match only explicit IMDb metadata; never guess by title.
        item_name = _norm_title(item.get("name", ""))
        imdb_match = target in [str(item.get(k, "")).strip().lower() for k in ("imdb", "imdb_id")]
        title_match = bool(item_name and any(name and (item_name == name or item_name.startswith(name) or name.startswith(item_name)) for name in names))
        if not (imdb_match or title_match):
            continue
        stream_id = item.get("stream_id")
        if not stream_id:
            continue
        ext = str(item.get("container_extension") or "mp4").lstrip(".")
        url = base + "/movie/" + requests.utils.quote(config["xtream_user"], safe="") + "/" + requests.utils.quote(config["xtream_pass"], safe="") + "/" + str(stream_id) + "." + ext
        matches.append({
            "url": url,
            "title": str(item.get("name") or "Movie") + " — " + ext.upper(),
            "source": "Xtream",
            "name": "FluxStream"
        })
    return matches

def _stalker_headers(config, token=""):
    headers = {
        "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 MAG200 stbapp",
        "X-User-Agent": "Model: MAG250; Link: WiFi",
        "Cookie": "mac=" + config["stalker_mac"] + "; stb_lang=en; timezone=UTC",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    return headers

def _stalker_request(base, config, token, params):
    params = dict(params)
    params.setdefault("JsHttpRequest", "1-xml")
    response = requests.get(base + "/portal.php", params=params,
                            headers=_stalker_headers(config, token), timeout=TIMEOUT)
    if response.status_code == 404:
        response = requests.get(base + "/server/load.php", params=params,
                                headers=_stalker_headers(config, token), timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    return data.get("js", data) if isinstance(data, dict) else data

def _stalker_token(config):
    base = config["stalker_url"]
    data = _stalker_request(base, config, "", {"type": "stb", "action": "handshake"})
    token = data.get("token") if isinstance(data, dict) else None
    if not token:
        raise ValueError("Stalker portal did not return a session token. Check your authorized portal and MAC.")
    return str(token)

def _stalker_movies(config, imdb_id):
    base = config["stalker_url"]
    token = _stalker_token(config)
    target = imdb_id.lower()
    names = [_norm_title(name) for name in _movie_names(imdb_id)]
    movies = []
    categories = _stalker_request(base, config, token, {"type": "vod", "action": "get_categories"})
    if not isinstance(categories, list):
        categories = []
    # Use only the user-supplied MAC; no MAC generation or scanning.
    for category in categories[:150]:
        if not isinstance(category, dict):
            continue
        cat_id = str(category.get("id", ""))
        page = 1
        while page <= 10:
            data = _stalker_request(base, config, token, {
                "type": "vod", "action": "get_ordered_list",
                "genre": cat_id, "p": page, "sortby": "added"
            })
            items = data.get("data", []) if isinstance(data, dict) else []
            if not isinstance(items, list) or not items:
                break
            for item in items:
                if not isinstance(item, dict):
                    continue
                item_imdb = str(item.get("imdb_id") or item.get("imdb") or "").lower()
                item_name = _norm_title(item.get("name") or item.get("o_name") or "")
                imdb_match = item_imdb == target
                title_match = bool(item_name and any(name and (item_name == name or item_name.startswith(name) or name.startswith(item_name)) for name in names))
                if not (imdb_match or title_match):
                    continue
                cmd = item.get("cmd") or item.get("id")
                if not cmd:
                    continue
                link_data = _stalker_request(base, config, token, {
                    "type": "vod", "action": "create_link", "cmd": str(cmd),
                    "series": "0", "forced_storage": "undefined", "disable_ad": "0"
                })
                link = link_data.get("cmd") if isinstance(link_data, dict) else None
                if not link:
                    continue
                link = str(link).replace("ffmpeg ", "").replace("ffrt ", "").strip()
                if link.startswith("http://") or link.startswith("https://"):
                    movies.append({
                        "url": link,
                        "title": str(item.get("name") or item.get("o_name") or "Movie"),
                        "source": "Stalker",
                        "name": "FluxStream"
                    })
            if len(items) < 20:
                break
            page += 1
    return movies

def _language_rank(stream):
    title = (stream.get("title") or "").lower()
    if any(x in title for x in ("hindi", "hin", "हिंदी")):
        return 0
    if any(x in title for x in ("multi", "dual audio", "multi-audio")):
        return 1
    if "english" in title or "eng" in title:
        return 2
    return 3

def _manifest():
    return {
        "id": "com.fluxstream.wako.movies",
        "name": "FluxStream Movies",
        "description": "Movie streams from your own authorized Xtream and Stalker services. Hindi audio is prioritized.",
        "version": "1.0.0",
        "resources": [{"name": "stream", "types": ["movie"], "idPrefixes": ["tt"]}],
        "types": ["movie"],
        "catalogs": [],
        "idPrefixes": ["tt"],
        "behaviorHints": {"configurable": True, "configurationRequired": True, "p2p": False}
    }

def _base_path(token=None):
    root = request.url_root.rstrip("/")
    return root + ("/c/" + token if token else "")

@wako_bp.get("/manifest.json")
@wako_bp.get("/c/<token>/manifest.json")
def wako_manifest(token=None):
    if token and not _decrypt_config(token):
        return jsonify({"error": "Invalid or expired add-on configuration"}), 400
    response = jsonify(_manifest())
    response.headers["Cache-Control"] = "no-store"
    return response

@wako_bp.route("/configure", methods=["GET", "POST"])
@wako_bp.route("/c/<token>/configure", methods=["GET", "POST"])
def wako_configure(token=None):
    existing = _decrypt_config(token) if token else {}
    if request.method == "POST":
        try:
            config = _valid_config(request.form)
            encrypted = _encrypt_config(config)
            install_url = _base_path(encrypted) + "/manifest.json"
            return (
                "<!doctype html><meta name='viewport' content='width=device-width,initial-scale=1'>"
                "<title>FluxStream Wako Setup</title><main style='font:16px system-ui;max-width:650px;margin:40px auto;padding:20px'>"
                "<h2>FluxStream Movies is configured</h2><p>Copy this HTTPS manifest URL into Wako → Settings → Extensions → Install an add-on.</p>"
                "<input id='u' style='width:100%;padding:12px' readonly value='" + install_url + "'>"
                "<p><button onclick=\"navigator.clipboard.writeText(document.getElementById('u').value)\">Copy manifest URL</button></p>"
                "<p>Credentials are encrypted in the configuration token. Keep this URL private; it grants access to the configured provider account.</p></main>"
            )
        except (ValueError, RuntimeError) as exc:
            error = str(exc)
    else:
        error = ""
    def val(key):
        return (existing or {}).get(key, "")
    html = """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>FluxStream Wako Setup</title><style>body{font:16px system-ui;background:#10131d;color:#eee;margin:0;padding:20px}
    main{max-width:620px;margin:20px auto;background:#1b2030;padding:24px;border-radius:16px}
    input{box-sizing:border-box;width:100%;padding:12px;margin:6px 0 16px;border:1px solid #596078;border-radius:8px;background:#0e1220;color:white}
    button{padding:13px 20px;border:0;border-radius:8px;background:#28a36a;color:white;font-weight:700}
    small{color:#b9c1d4}.err{color:#ff8c8c}</style></head><body><main>
    <h2>FluxStream Movies — Wako Setup</h2><p>Enter at least one service that you own or are authorized to use. Hindi audio is ranked first when provider metadata identifies it.</p>
    <form method="post"><h3>Xtream Codes (optional)</h3>
    <label>Server URL</label><input name="xtream_url" placeholder="https://provider.example:8080" value="__XURL__">
    <label>Username</label><input name="xtream_user" value="__XUSER__">
    <label>Password</label><input type="password" name="xtream_pass" value="__XPASS__">
    <h3>Stalker Portal (optional)</h3><label>Portal URL</label><input name="stalker_url" placeholder="https://portal.example/c/" value="__SURL__">
    <label>Your authorized STB MAC</label><input name="stalker_mac" placeholder="AA:BB:CC:DD:EE:FF" value="__SMAC__">
    <p class="err">__ERROR__</p><button type="submit">Generate Wako manifest URL</button></form>
    <p><small>Do not enter credentials for services you are not authorized to access. The generated URL contains an encrypted configuration; keep it private. The Wako stream protocol may expose direct provider playback URLs to your player.</small></p>
    </main></body></html>"""
    values = {"__XURL__":val("xtream_url"),"__XUSER__":val("xtream_user"),"__XPASS__":val("xtream_pass"),
              "__SURL__":val("stalker_url"),"__SMAC__":val("stalker_mac"),"__ERROR__":error}
    from html import escape
    for key, value in values.items():
        html = html.replace(key, escape(str(value), quote=True))
    return html

@wako_bp.get("/stream/movie/<movie_id>.json")
@wako_bp.get("/c/<token>/stream/movie/<movie_id>.json")
def wako_movie_streams(movie_id, token=None):
    if not re.fullmatch(r"tt[0-9]+", movie_id or ""):
        return jsonify({"streams": []})
    config = _decrypt_config(token) if token else None
    if not config:
        return jsonify({"streams": [], "error": "Configure this add-on first."})
    streams, errors = [], []
    if config.get("xtream_url"):
        try:
            streams.extend(_xtream_movies(config, movie_id))
        except Exception as exc:
            current_app.logger.warning("Xtream movie lookup failed: %s", type(exc).__name__)
            errors.append("Xtream unavailable")
    if config.get("stalker_url"):
        try:
            streams.extend(_stalker_movies(config, movie_id))
        except Exception as exc:
            current_app.logger.warning("Stalker movie lookup failed: %s", type(exc).__name__)
            errors.append("Stalker unavailable")
    unique, seen = [], set()
    for stream in streams:
        key = stream.get("url")
        if key and key not in seen:
            seen.add(key)
            unique.append(stream)
    unique.sort(key=_language_rank)
    result = []
    for stream in unique[:30]:
        result.append({
            "url": stream["url"],
            "title": stream["title"] + " — " + stream["source"],
            "name": "FluxStream Movies"
        })
    response = jsonify({"streams": result})
    response.headers["Cache-Control"] = "no-store"
    return response

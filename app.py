from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import threading
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import re

app = Flask(__name__, static_folder='static')
CORS(app)

stop_checking = False
valid_mac_found = None

def generate_random_mac():
    prefix = "00:1A:79"
    suffix = ":".join([f"{random.randint(0, 255):02X}" for _ in range(3)])
    return f"{prefix}:{suffix}"

def parse_proxy(proxy_string):
    parts = proxy_string.strip().split(':')
    if len(parts) == 2:
        return {
            'http': f'http://{parts[0]}:{parts[1]}',
            'https': f'http://{parts[0]}:{parts[1]}'
        }
    elif len(parts) == 4:
        return {
            'http': f'http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}',
            'https': f'http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}'
        }
    return None

def check_stalker_mac(url, mac, proxy=None):
    try:
        base_url = url.rstrip('/')
        
        endpoints = [
            '/portal.php?type=account_info&action=get_main_info',
            '/portal.php?action=handshake&type=stb&token=',
            '/server/load.php?type=stb&action=handshake',
            '/stalker_portal/server/load.php?type=stb&action=handshake',
            '/portal.php?type=stb&action=handshake'
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3',
            'X-User-Agent': 'Model: MAG250; Link: WiFi',
            'Cookie': f'mac={mac}; stb_lang=en; timezone=Europe/Kiev'
        }
        
        timeout = 3
        proxies = proxy if proxy else None
        
        def try_endpoint(endpoint):
            try:
                full_url = base_url + endpoint
                response = requests.get(
                    full_url,
                    headers=headers,
                    timeout=timeout,
                    proxies=proxies,
                    verify=True
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        if 'js' in data:
                            js_data = data['js']
                            if isinstance(js_data, dict) and ('token' in js_data or 'mac' in js_data or 'phone' in js_data or 'status' in js_data):
                                return (True, endpoint, response, data)
                        elif 'token' in data or 'id' in data:
                            return (True, endpoint, response, data)
                    except:
                        text_lower = response.text.lower()
                        if ('account' in text_lower and 'expire' in text_lower) or ('token' in text_lower and 'mac' in text_lower):
                            return (True, endpoint, response, None)
            except:
                pass
            return (False, endpoint, None, None)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(try_endpoint, ep) for ep in endpoints]
            
            for future in as_completed(futures):
                valid, endpoint, response, data = future.result()
                if valid:
                    if data:
                        token = data.get('js', {}).get('token', '') if 'js' in data else data.get('token', '')
                        account_info = get_account_info(base_url, mac, token, proxies)
                        channels_info = get_channels_info(base_url, mac, token, proxies)
                        
                        has_channels = bool(channels_info and channels_info.get('total_channels', 0) > 0)
                        
                        return {
                            'valid': has_channels,
                            'mac': mac,
                            'url': url,
                            'response': data,
                            'account_info': account_info,
                            'channels_info': channels_info,
                            'endpoint': endpoint,
                            'status_code': response.status_code,
                            'reason': 'Has channel access' if has_channels else 'No channel access'
                        }
                    else:
                        return {
                            'valid': False,
                            'mac': mac,
                            'url': url,
                            'response': response.text[:500],
                            'endpoint': endpoint,
                            'status_code': response.status_code,
                            'reason': 'No channel data available'
                        }
        
        return {
            'valid': False,
            'mac': mac,
            'url': url,
            'response': 'No valid response from any endpoint'
        }
        
    except Exception as e:
        return {
            'valid': False,
            'mac': mac,
            'url': url,
            'error': str(e)
        }

def get_account_info(base_url, mac, token, proxies=None):
    try:
        info_endpoints = [
            f'/portal.php?type=account_info&action=get_main_info&JsHttpRequest=1-xml',
            f'/portal.php?type=account_info&action=get_profile&JsHttpRequest=1-xml',
            f'/server/load.php?type=account_info&action=get_main_info'
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3',
            'X-User-Agent': 'Model: MAG250; Link: WiFi',
            'Cookie': f'mac={mac}; stb_lang=en; timezone=Europe/Kiev',
            'Authorization': f'Bearer {token}' if token else ''
        }
        
        def try_endpoint_parallel(endpoint):
            try:
                response = requests.get(
                    base_url + endpoint,
                    headers=headers,
                    timeout=5,
                    proxies=proxies,
                    verify=True
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'js' in data and data['js']:
                            return data['js']
                        elif data:
                            return data
                    except:
                        pass
            except:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(try_endpoint_parallel, ep) for ep in info_endpoints]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    return result
                
        return None
    except:
        return None

def get_channels_info(base_url, mac, token, proxies=None):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3',
            'X-User-Agent': 'Model: MAG250; Link: WiFi',
            'Cookie': f'mac={mac}; stb_lang=en; timezone=Europe/Kiev',
            'Authorization': f'Bearer {token}' if token else ''
        }
        
        channels_info = {
            'total_channels': 0,
            'total_categories': 0,
            'total_vod': 0,
            'categories': []
        }
        
        channel_endpoints = [
            '/portal.php?type=itv&action=get_all_channels',
            '/portal.php?type=itv&action=get_ordered_list',
            '/server/load.php?type=itv&action=get_all_channels'
        ]
        
        def try_channel_endpoint(endpoint):
            try:
                response = requests.get(
                    base_url + endpoint,
                    headers=headers,
                    timeout=5,
                    proxies=proxies,
                    verify=True
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'js' in data and 'data' in data['js']:
                            return len(data['js']['data'])
                        elif 'data' in data:
                            return len(data['data'])
                    except:
                        pass
            except:
                pass
            return 0
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(try_channel_endpoint, ep) for ep in channel_endpoints]
            counts = []
            for future in as_completed(futures):
                count = future.result()
                if count > 0:
                    counts.append(count)
            if counts:
                channels_info['total_channels'] = max(counts)
        
        genre_endpoints = [
            '/portal.php?type=itv&action=get_genres',
            '/server/load.php?type=itv&action=get_genres'
        ]
        
        for endpoint in genre_endpoints:
            try:
                response = requests.get(
                    base_url + endpoint,
                    headers=headers,
                    timeout=5,
                    proxies=proxies,
                    verify=True
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'js' in data:
                            categories = data['js']
                            if isinstance(categories, list):
                                channels_info['total_categories'] = len(categories)
                                channels_info['categories'] = categories
                                break
                        elif isinstance(data, list):
                            channels_info['total_categories'] = len(data)
                            channels_info['categories'] = data
                            break
                    except:
                        pass
            except:
                continue
        
        vod_endpoints = [
            '/portal.php?type=vod&action=get_categories',
            '/server/load.php?type=vod&action=get_categories'
        ]
        
        for endpoint in vod_endpoints:
            try:
                response = requests.get(
                    base_url + endpoint,
                    headers=headers,
                    timeout=5,
                    proxies=proxies,
                    verify=True
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'js' in data:
                            vod_cats = data['js']
                            if isinstance(vod_cats, list):
                                channels_info['total_vod'] = sum(cat.get('count', 0) for cat in vod_cats if isinstance(cat, dict))
                                break
                        elif isinstance(data, list):
                            channels_info['total_vod'] = sum(cat.get('count', 0) for cat in data if isinstance(cat, dict))
                            break
                    except:
                        pass
            except:
                continue
        
        return channels_info if channels_info['total_channels'] > 0 or channels_info['total_categories'] > 0 else None
    except:
        return None

def get_stalker_channels(base_url, mac, token, proxies=None):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3',
            'X-User-Agent': 'Model: MAG250; Link: WiFi',
            'Cookie': f'mac={mac}; stb_lang=en; timezone=Europe/Kiev',
            'Authorization': f'Bearer {token}' if token else ''
        }
        
        channels = []
        channel_endpoints = [
            '/portal.php?type=itv&action=get_all_channels',
            '/portal.php?type=itv&action=get_ordered_list',
            '/server/load.php?type=itv&action=get_all_channels'
        ]
        
        for endpoint in channel_endpoints:
            try:
                response = requests.get(
                    base_url + endpoint,
                    headers=headers,
                    timeout=10,
                    proxies=proxies,
                    verify=True
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'js' in data and 'data' in data['js']:
                        channels = data['js']['data']
                        break
                    elif 'data' in data:
                        channels = data['data']
                        break
            except:
                continue
        
        return channels
    except:
        return []

def stalker_to_m3u(url, mac):
    try:
        base_url = url.rstrip('/')
        
        result = check_stalker_mac(url, mac)
        
        if not result.get('valid'):
            return None
        
        token = result.get('response', {}).get('js', {}).get('token', '') if 'js' in result.get('response', {}) else result.get('response', {}).get('token', '')
        
        channels = get_stalker_channels(base_url, mac, token)
        
        if not channels:
            return None
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3',
            'X-User-Agent': 'Model: MAG250; Link: WiFi',
            'Cookie': f'mac={mac}; stb_lang=en; timezone=Europe/Kiev',
            'Authorization': f'Bearer {token}' if token else ''
        }
        
        genre_map = {}
        genre_endpoints = [
            '/portal.php?type=itv&action=get_genres',
            '/server/load.php?type=itv&action=get_genres'
        ]
        
        for endpoint in genre_endpoints:
            try:
                response = requests.get(base_url + endpoint, headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    genres = data.get('js', data) if 'js' in data else data
                    if isinstance(genres, list):
                        for genre in genres:
                            genre_id = str(genre.get('id', ''))
                            genre_name = genre.get('title', genre.get('name', 'Unknown'))
                            genre_map[genre_id] = genre_name
                        break
            except:
                continue
        
        m3u_content = "#EXTM3U\n"
        
        for channel in channels:
            name = channel.get('name', 'Unknown')
            cmd = channel.get('cmd', '')
            logo = channel.get('logo', '')
            number = channel.get('number', '')
            tv_genre_id = str(channel.get('tv_genre_id', ''))
            category_name = genre_map.get(tv_genre_id, 'Uncategorized')
            
            if cmd:
                m3u_content += f'#EXTINF:-1 tvg-logo="{logo}" tvg-id="{number}" group-title="{category_name}",{name}\n'
                
                if cmd.startswith('ffrt'):
                    stream_url = cmd.replace('ffrt ', '').replace('ffrt', '')
                elif cmd.startswith('http'):
                    stream_url = cmd
                else:
                    stream_url = f"{base_url}/play/{cmd}"
                
                m3u_content += f"{stream_url}\n"
        
        return m3u_content
    except Exception as e:
        return None

def xtream_to_m3u(server_url, username, password):
    try:
        base_url = server_url.rstrip('/')
        
        if not base_url.startswith('http'):
            base_url = 'http://' + base_url
        
        auth_url = f"{base_url}/player_api.php?username={username}&password={password}"
        
        response = requests.get(auth_url, timeout=10)
        
        if response.status_code != 200:
            return None
        
        auth_data = response.json()
        
        if 'user_info' not in auth_data:
            return None
        
        categories_url = f"{base_url}/player_api.php?username={username}&password={password}&action=get_live_categories"
        categories_response = requests.get(categories_url, timeout=10)
        
        category_map = {}
        if categories_response.status_code == 200:
            categories = categories_response.json()
            for cat in categories:
                category_map[str(cat.get('category_id', ''))] = cat.get('category_name', 'Unknown')
        
        streams_url = f"{base_url}/player_api.php?username={username}&password={password}&action=get_live_streams"
        streams_response = requests.get(streams_url, timeout=15)
        
        if streams_response.status_code != 200:
            return None
        
        streams = streams_response.json()
        
        if not streams:
            return None
        
        m3u_content = "#EXTM3U\n"
        
        for stream in streams:
            stream_id = stream.get('stream_id', '')
            name = stream.get('name', 'Unknown')
            icon = stream.get('stream_icon', '')
            category_id = str(stream.get('category_id', ''))
            category_name = category_map.get(category_id, 'Uncategorized')
            container_extension = stream.get('container_extension', 'm3u8')
            
            stream_url = f"{base_url}/live/{username}/{password}/{stream_id}.{container_extension}"
            
            m3u_content += f'#EXTINF:-1 tvg-logo="{icon}" group-title="{category_name}",{name}\n'
            m3u_content += f"{stream_url}\n"
        
        return m3u_content
    except Exception as e:
        return None

def parse_m3u_content(content):
    try:
        lines = content.strip().split('\n')
        channels = []
        current_info = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXTINF:'):
                current_info = line
            elif line and not line.startswith('#'):
                if current_info:
                    channels.append({
                        'info': current_info,
                        'url': line
                    })
                    current_info = None
        
        m3u_content = "#EXTM3U\n"
        for channel in channels:
            m3u_content += f"{channel['info']}\n{channel['url']}\n"
        
        return {
            'total_channels': len(channels),
            'm3u_content': m3u_content,
            'channels': channels
        }
    except Exception as e:
        return None

def check_proxy(proxy_string):
    try:
        proxy_dict = parse_proxy(proxy_string)
        if not proxy_dict:
            return {'proxy': proxy_string, 'working': False, 'error': 'Invalid format'}
        
        test_urls = [
            'http://www.bing.com',
            'http://www.duckduckgo.com',
            'http://www.google.com',
            'http://www.yahoo.com',
            'http://www.ask.com',
            'http://www.cloudflare.com',
            'http://www.wikipedia.org'
        ]
        
        for test_url in test_urls:
            try:
                response = requests.get(
                    test_url,
                    proxies=proxy_dict,
                    timeout=10,
                    verify=True
                )
                
                if response.status_code == 200:
                    return {
                        'proxy': proxy_string,
                        'working': True,
                        'response_time': response.elapsed.total_seconds()
                    }
            except:
                continue
        
        return {
            'proxy': proxy_string,
            'working': False,
            'error': 'Not working'
        }
            
    except Exception as e:
        return {
            'proxy': proxy_string,
            'working': False,
            'error': str(e)
        }

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/check_mac', methods=['POST'])
def check_mac():
    global stop_checking, valid_mac_found
    
    data = request.json
    url = data.get('url')
    mac = data.get('mac')
    proxy_string = data.get('proxy')
    
    if not url or not mac:
        return jsonify({'error': 'URL and MAC are required'}), 400
    
    proxy_dict = None
    if proxy_string:
        proxy_dict = parse_proxy(proxy_string)
    
    result = check_stalker_mac(url, mac, proxy_dict)
    return jsonify(result)

@app.route('/check_mac_multiple_urls', methods=['POST'])
def check_mac_multiple_urls():
    data = request.json
    urls = data.get('urls', [])
    mac = data.get('mac')
    proxies = data.get('proxies', [])
    
    if not urls or not mac:
        return jsonify({'error': 'URLs and MAC are required'}), 400
    
    results = []
    valid_result = None
    
    def check_url(url):
        proxy_dict = None
        if proxies:
            proxy_string = random.choice(proxies)
            proxy_dict = parse_proxy(proxy_string)
        
        return check_stalker_mac(url, mac, proxy_dict)
    
    with ThreadPoolExecutor(max_workers=min(len(urls), 20)) as executor:
        futures = [executor.submit(check_url, url) for url in urls]
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            if result.get('valid') and not valid_result:
                valid_result = result
    
    return jsonify({
        'results': results,
        'valid_result': valid_result
    })

@app.route('/check_macs_from_list', methods=['POST'])
def check_macs_from_list():
    global stop_checking, valid_mac_found
    
    data = request.json
    urls = data.get('urls', [data.get('url')]) if data.get('url') else data.get('urls', [])
    macs = data.get('macs', [])
    threads = data.get('threads', 10)
    proxies = data.get('proxies', [])
    
    if not urls or not macs:
        return jsonify({'error': 'URL(s) and MAC list are required'}), 400
    
    if not isinstance(urls, list):
        urls = [urls]
    
    valid_macs = []
    invalid_macs = []
    
    def check_mac_against_urls(mac):
        for url in urls:
            proxy_dict = None
            if proxies:
                proxy_string = random.choice(proxies)
                proxy_dict = parse_proxy(proxy_string)
            
            result = check_stalker_mac(url, mac, proxy_dict)
            
            if result.get('valid'):
                return result
        
        return None
    
    with ThreadPoolExecutor(max_workers=min(threads, 100)) as executor:
        futures = {executor.submit(check_mac_against_urls, mac): mac for mac in macs}
        
        for future in as_completed(futures):
            mac = futures[future]
            result = future.result()
            if result:
                valid_macs.append(result)
            else:
                invalid_macs.append(mac)
    
    return jsonify({
        'valid_macs': valid_macs,
        'invalid_macs': invalid_macs,
        'total_checked': len(macs)
    })

@app.route('/system_check', methods=['POST'])
def system_check():
    global stop_checking
    
    data = request.json
    urls = data.get('urls', [data.get('url')]) if data.get('url') else data.get('urls', [])
    threads = data.get('threads', 10)
    max_attempts = data.get('max_attempts', 1000)
    proxies = data.get('proxies', [])
    stop_on_first = data.get('stop_on_first', True)
    
    if not urls or (isinstance(urls, list) and len(urls) == 0):
        return jsonify({'error': 'URL(s) are required'}), 400
    
    if not isinstance(urls, list):
        urls = [urls]
    
    stop_checking = False
    checked_macs = []
    valid_macs = []
    
    def check_random_mac():
        global stop_checking
        
        if stop_checking:
            return None
            
        mac = generate_random_mac()
        
        for url in urls:
            if stop_checking:
                break
                
            proxy_dict = None
            if proxies:
                proxy_string = random.choice(proxies)
                proxy_dict = parse_proxy(proxy_string)
            
            result = check_stalker_mac(url, mac, proxy_dict)
            
            if result.get('valid'):
                valid_macs.append(result)
                if stop_on_first:
                    stop_checking = True
                return result
        
        return {'valid': False, 'mac': mac}
    
    with ThreadPoolExecutor(max_workers=min(threads, 100)) as executor:
        futures = []
        attempts = 0
        
        while attempts < max_attempts and not stop_checking:
            batch_size = min(threads * 2, max_attempts - attempts)
            batch_futures = [executor.submit(check_random_mac) for _ in range(batch_size)]
            futures.extend(batch_futures)
            attempts += batch_size
            
            for future in as_completed(batch_futures):
                if stop_checking:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                result = future.result()
                if result:
                    checked_macs.append(result)
            
            if stop_checking:
                break
    
    return jsonify({
        'checked_macs': checked_macs,
        'valid_macs': valid_macs,
        'total_checked': len(checked_macs),
        'total_valid': len(valid_macs)
    })

@app.route('/check_proxies', methods=['POST'])
def check_proxies():
    data = request.json
    proxies = data.get('proxies', [])
    threads = data.get('threads', 10)
    
    if not proxies:
        return jsonify({'error': 'Proxy list is required'}), 400
    
    working = []
    not_working = []
    
    def check_single_proxy(proxy):
        result = check_proxy(proxy)
        if result['working']:
            working.append(result)
        else:
            not_working.append(result)
        return result
    
    with ThreadPoolExecutor(max_workers=min(threads, 100)) as executor:
        futures = [executor.submit(check_single_proxy, proxy) for proxy in proxies]
        
        for future in as_completed(futures):
            future.result()
    
    return jsonify({
        'working': working,
        'not_working': not_working,
        'total_working': len(working),
        'total_not_working': len(not_working)
    })

@app.route('/stop_checking', methods=['POST'])
def stop_checking_route():
    global stop_checking
    stop_checking = True
    return jsonify({'message': 'Checking stopped'})

@app.route('/convert/stalker-to-m3u', methods=['POST'])
def convert_stalker():
    data = request.json
    url = data.get('url')
    mac = data.get('mac')
    
    if not url or not mac:
        return jsonify({'error': 'URL and MAC are required'}), 400
    
    m3u_content = stalker_to_m3u(url, mac)
    
    if m3u_content:
        return jsonify({
            'success': True,
            'm3u_content': m3u_content,
            'total_channels': m3u_content.count('#EXTINF:')
        })
    else:
        return jsonify({'error': 'Failed to convert. Check MAC/URL validity.'}), 400

@app.route('/convert/xtream-to-m3u', methods=['POST'])
def convert_xtream():
    data = request.json
    url = data.get('url')
    username = data.get('username')
    password = data.get('password')
    
    if not url or not username or not password:
        return jsonify({'error': 'URL, username and password are required'}), 400
    
    m3u_content = xtream_to_m3u(url, username, password)
    
    if m3u_content:
        return jsonify({
            'success': True,
            'm3u_content': m3u_content,
            'total_channels': m3u_content.count('#EXTINF:')
        })
    else:
        return jsonify({'error': 'Failed to convert. Check credentials.'}), 400

@app.route('/convert/parse-m3u', methods=['POST'])
def parse_m3u():
    data = request.json
    m3u_input = data.get('m3u_input')
    
    if not m3u_input:
        return jsonify({'error': 'M3U input is required'}), 400
    
    if m3u_input.startswith('http'):
        try:
            response = requests.get(m3u_input, timeout=15)
            m3u_content = response.text
        except:
            return jsonify({'error': 'Failed to fetch M3U from URL'}), 400
    else:
        m3u_content = m3u_input
    
    result = parse_m3u_content(m3u_content)
    
    if result:
        return jsonify({
            'success': True,
            'm3u_content': result['m3u_content'],
            'total_channels': result['total_channels'],
            'channels': result['channels']
        })
    else:
        return jsonify({'error': 'Failed to parse M3U content'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

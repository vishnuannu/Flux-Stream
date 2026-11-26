# 🌊 FluxStream - Universal Streaming Toolkit

<div align="center">


[![Live Preview](https://img.shields.io/badge/Live%20Preview-7289da?logo=vercel&logoColor=white&style=for-the-badge)](https://fluxstream-app.vercel.app)
[![GitHub](https://img.shields.io/badge/GitHub-walterwhite--69-181717?style=for-the-badge&logo=github)](https://github.com/walterwhite-69/Flux-Stream)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

*Transform, validate & convert streaming formats in real-time with a sleek cyberpunk interface*

[Features](#-features) • [Quick Start](#-quick-start) • [Usage](#-usage) • [API](#-api-endpoints) • [Deploy](#-deployment) • [Discord](https://discord.gg/rgWcEw5G8a)

</div>

---

**Key Capabilities:**
- 🔍 **MAC Address Validation** - Validate single or bulk MAC addresses against Stalker portals with multi-threaded checking
- 🎲 **System MAC Generator** - Brute-force valid MAC addresses with customizable ranges (00:1A:79:XX:XX:XX)
- 🔄 **Format Conversion** - Convert between Stalker, Xtream Codes, and M3U playlist formats seamlessly
- 🌐 **Proxy Checker** - Real-time proxy validation with response time metrics and concurrent testing
- 🎨 **Theme Cycling** - 7 smooth-transitioning neon themes (Red, Green, Purple, Sky, Orange, Pink, Yellow)

Whether you're managing IPTV services, testing streaming infrastructure, or converting playlist formats, FluxStream provides the tools you need with a beautiful, responsive interface that works on any device.

---

## ✨ Features

### 🔐 MAC Address Tools
- **Single MAC Check** - Validate MAC addresses against Stalker portals
- **Bulk MAC Validation** - Check multiple MAC addresses with configurable threads (1-100)
- **Multi-URL Support** - Test MACs across multiple portal URLs simultaneously
- **System Generator** - Auto-generate and validate MAC addresses in the 00:1A:79 range
- **Proxy Rotation** - Optional proxy support for all validation requests
- **Real-time Updates** - Live display of currently checking MAC addresses

### 🔄 Format Converters
- **Stalker to M3U** - Convert Stalker portal + MAC to standard M3U8 playlists
- **Xtream Codes to M3U** - Transform Xtream login credentials to M3U format
- **M3U Parser & Cleaner** - Parse, validate and clean existing M3U playlists
- **Channel Analysis** - View total channels, categories, and VOD content
- **One-Click Download** - Export converted playlists instantly

### 🌐 Proxy Validator
- **Real-time Checking** - See working proxies appear instantly as they're validated
- **Multi-threaded Testing** - Concurrent proxy validation (1-100 threads)
- **Response Time Metrics** - Measure proxy speed in milliseconds
- **Format Support** - IP:PORT and IP:PORT:USER:PASS formats
- **Separated Results** - Working and non-working proxies displayed separately

### 🎨 UI/UX Features
- **7 Neon Themes** - Smooth-cycling color schemes with unique icons
- **Glitch Effects** - Cyberpunk-style animations and obfuscated text
- **Responsive Design** - Mobile-friendly interface that works everywhere
- **Dark Mode** - Eye-friendly dark theme with neon accents
- **Zero Cache** - Always see the latest updates with smart cache control

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/walterwhite-69/Flux-Stream.git
cd Flux-Stream
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Access the interface**
```
Open your browser and navigate to http://localhost:5000
```

---

## 💻 Usage

### MAC Address Validation

1. Navigate to the **MAC Checker** tab
2. Enter a Stalker portal URL (e.g., `http://example.com:80/c/`)
3. Input MAC address in format `00:1A:79:XX:XX:XX`
4. Click **Check MAC** to validate
5. View account info, expiry, channels, and categories

**Bulk Checking:**
- Enable "Use Multiple URLs" for multi-portal testing
- Enter one MAC per line in "MAC List" section
- Adjust threads (1-100) for optimal performance
- Enable proxy rotation for distributed requests

### Format Conversion

**Stalker to M3U:**
1. Go to **Converter** tab
2. Enter Stalker portal URL and MAC address
3. Click **Convert to M3U**
4. Download the generated playlist

**Xtream Codes to M3U:**
1. Input Xtream server URL (e.g., `http://server.com:8080`)
2. Enter username and password
3. Click **Convert to M3U**
4. Export your playlist

### Proxy Validation

1. Open **Proxy Checker** tab
2. Paste proxy list (one per line)
3. Set thread count for concurrent testing
4. Click **Check Proxies**
5. Working proxies appear in real-time with response times

---

## 🔌 API Endpoints

### MAC Validation
```http
POST /check_mac
Content-Type: application/json

{
  "url": "http://portal.com:80/c/",
  "mac": "00:1A:79:XX:XX:XX",
  "proxy": "ip:port" (optional)
}
```

### Format Conversion
```http
POST /convert/stalker-to-m3u
Content-Type: application/json

{
  "url": "http://portal.com:80/c/",
  "mac": "00:1A:79:XX:XX:XX"
}
```

```http
POST /convert/xtream-to-m3u
Content-Type: application/json

{
  "url": "http://server.com:8080",
  "username": "user123",
  "password": "pass123"
}
```

### Proxy Validation
```http
POST /check_proxies
Content-Type: application/json

{
  "proxies": ["ip:port", "ip:port:user:pass"],
  "threads": 10
}
```

---

## 🌍 Deployment

### Deploy to Vercel

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Deploy**
```bash
vercel --prod
```

### Deploy to Heroku

1. **Create Procfile**
```bash
echo "web: python app.py" > Procfile
```

2. **Deploy**
```bash
heroku create fluxstream
git push heroku main
```

### Deploy to Railway/Render
- Connect your GitHub repository
- Set build command: `pip install -r requirements.txt`
- Set start command: `python app.py`

---

## 🛠️ Tech Stack

- **Backend:** Python 3.8+, Flask, Flask-CORS
- **Frontend:** Vanilla JavaScript, HTML5, CSS3
- **Styling:** Custom CSS with cyberpunk theme
- **Requests:** Python Requests library
- **Concurrency:** ThreadPoolExecutor for multi-threading

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

Join our [Discord community](https://discord.gg/rgWcEw5G8a) to discuss ideas and get support!

---

## 📞 Support & Community

- 💬 **Discord:** [Join our server](https://discord.gg/rgWcEw5G8a)
- 🐙 **GitHub:** [@walterwhite-69](https://github.com/walterwhite-69)
- 📧 **Issues:** [Report bugs](https://github.com/walterwhite-69/Flux-Stream/issues)

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is for educational and testing purposes only. Users are responsible for ensuring their usage complies with applicable laws and service terms. The developers assume no liability for misuse.

---

<div align="center">

**Made with 💜 by [Walter](https://github.com/walterwhite-69)**

*Transform your streaming workflow with FluxStream*

[![Star on GitHub](https://img.shields.io/github/stars/walterwhite-69/Flux-Stream?style=social)](https://github.com/walterwhite-69/Flux-Stream)

</div>
---

## 🎬 Wako Movies Add-on

This branch adds a separate movie-only Wako add-on. Existing FluxStream tools and routes remain in place.

### Features
- Wako manifest and IMDb movie stream endpoint
- User-configured Xtream Codes VOD and Stalker VOD sources
- Hindi-first stream ordering when language is identifiable from provider movie titles
- Duplicate stream URL removal
- Encrypted, per-install provider configuration

### Deploy
1. Deploy this repository/branch to a Python host that supports the existing Flask app and provides HTTPS.
2. Install dependencies from `requirements.txt`.
3. Generate a Fernet key locally:
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
4. Set the generated value as the private environment variable `WAKO_CONFIG_SECRET` on the hosting provider. Do not commit it or share it.
5. Deploy/redeploy, then open `https://YOUR-HOST/configure`.
6. Enter only credentials and portal details for services you own or are authorized to use. Copy the generated manifest URL into Wako: Settings → Extensions → Install an add-on.

### Wako endpoints
- `GET /manifest.json`
- `GET /configure`
- `GET /c/<encrypted-config>/manifest.json`
- `GET /c/<encrypted-config>/stream/movie/<IMDb-ID>.json`

The configured manifest URL contains an encrypted configuration token and must be treated as private. The provider stream URLs returned to Wako may include provider authentication details depending on the provider's playback URL format. Install and use only with services you are authorized to access. No MAC generation, guessing, or portal enumeration is used by this add-on.

### Limitations
Provider APIs differ. IMDb-to-title matching depends on public movie metadata and provider titles; unmatched titles or providers that do not expose VOD links will return no stream. Test with one known movie and your own account before relying on it.


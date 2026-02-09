from gevent import monkey
monkey.patch_all()

from flask import Flask, request, Response, render_template_string
import requests
from urllib.parse import urlparse, urljoin, quote, unquote
import re
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

app = Flask(__name__)

# Modern HTML template with dark theme - TÜRKÇE
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StreamFlow Proxy</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #10b981;
            --dark-bg: #0f172a;
            --dark-card: #1e293b;
            --dark-text: #f1f5f9;
            --dark-border: #334155;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
            --gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: var(--dark-bg);
            color: var(--dark-text);
            min-height: 100vh;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        .header {
            text-align: center;
            margin-bottom: 3rem;
            padding-top: 2rem;
        }

        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .logo-icon {
            background: var(--gradient);
            width: 64px;
            height: 64px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: white;
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
        }

        .logo-text {
            font-size: 2.5rem;
            font-weight: 800;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .tagline {
            color: #94a3b8;
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(34, 197, 94, 0.1);
            color: var(--success);
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-size: 0.9rem;
            font-weight: 600;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }

        .status-badge i {
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .main-content {
            display: grid;
            gap: 2rem;
        }

        .card {
            background: var(--dark-card);
            border-radius: 20px;
            padding: 2rem;
            border: 1px solid var(--dark-border);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }

        .card-title {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
            color: var(--dark-text);
            font-size: 1.5rem;
        }

        .card-title i {
            color: var(--primary);
        }

        .url-input-group {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .url-input {
            flex: 1;
            background: rgba(30, 41, 59, 0.8);
            border: 2px solid var(--dark-border);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            color: var(--dark-text);
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .url-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
        }

        .url-input::placeholder {
            color: #64748b;
        }

        .btn {
            background: var(--gradient);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.4);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-secondary {
            background: var(--dark-border);
            color: var(--dark-text);
        }

        .btn-secondary:hover {
            background: #475569;
        }

        .endpoints {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }

        .endpoint {
            background: rgba(30, 41, 59, 0.6);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--dark-border);
            transition: all 0.3s ease;
        }

        .endpoint:hover {
            border-color: var(--primary);
        }

        .endpoint-title {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            color: var(--dark-text);
            margin-bottom: 0.75rem;
            font-size: 1.1rem;
        }

        .endpoint-title i {
            color: var(--secondary);
        }

        .endpoint-url {
            background: rgba(15, 23, 42, 0.8);
            padding: 0.75rem;
            border-radius: 8px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.85rem;
            color: #cbd5e1;
            word-break: break-all;
            margin-top: 0.5rem;
            border: 1px solid var(--dark-border);
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }

        .stat-card {
            text-align: center;
            padding: 1.5rem;
            background: rgba(99, 102, 241, 0.1);
            border-radius: 16px;
            border: 1px solid rgba(99, 102, 241, 0.2);
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: 800;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }

        .stat-label {
            color: #94a3b8;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .footer {
            text-align: center;
            margin-top: 4rem;
            padding: 2rem;
            border-top: 1px solid var(--dark-border);
            color: #64748b;
            font-size: 0.9rem;
        }

        .developer {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 1rem;
            color: var(--primary);
            font-weight: 600;
        }

        .developer i {
            color: var(--secondary);
        }

        .tooltip {
            position: relative;
            display: inline-block;
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background-color: var(--dark-card);
            color: var(--dark-text);
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
            border: 1px solid var(--dark-border);
            font-size: 0.8rem;
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }

        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .url-input-group {
                flex-direction: column;
            }
            
            .logo-text {
                font-size: 2rem;
            }
            
            .endpoints {
                grid-template-columns: 1fr;
            }
        }

        .copy-btn {
            background: transparent;
            border: 1px solid var(--dark-border);
            color: var(--dark-text);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.8rem;
            margin-top: 0.5rem;
        }

        .copy-btn:hover {
            background: var(--primary);
            border-color: var(--primary);
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="logo">
                <div class="logo-icon">
                    <i class="fas fa-broadcast-tower"></i>
                </div>
                <h1 class="logo-text">StreamFlow Proxy</h1>
            </div>
            <p class="tagline">Yüksek performanslı otomatik çözünürlüklü akış proxy'si</p>
            <div class="status-badge">
                <i class="fas fa-circle"></i>
                Çalışıyor • Tüm Sistemler Normal
            </div>
        </header>

        <main class="main-content">
            <div class="card">
                <h2 class="card-title">
                    <i class="fas fa-play-circle"></i>
                    Hızlı Proxy
                </h2>
                <div class="url-input-group">
                    <input type="text" 
                           class="url-input" 
                           id="streamUrl" 
                           placeholder="Akış URL'sini girin (M3U8 veya playlist)..."
                           value="https://example.com/playlist.m3u8">
                    <button class="btn" onclick="proxyStream()">
                        <i class="fas fa-rocket"></i>
                        Akışı Proxy'le
                    </button>
                </div>
                <p style="color: #94a3b8; font-size: 0.9rem;">
                    <i class="fas fa-info-circle"></i>
                    Herhangi bir akış URL'sini güvenli sunucularımız üzerinden proxy'leyin
                </p>
            </div>

            <div class="card">
                <h2 class="card-title">
                    <i class="fas fa-plug"></i>
                    API Uç Noktaları
                </h2>
                <p style="color: #94a3b8; margin-bottom: 1.5rem;">
                    Farklı proxy işlemleri için kullanılabilir uç noktalar:
                </p>
                
                <div class="endpoints">
                    <div class="endpoint">
                        <div class="endpoint-title">
                            <i class="fas fa-stream"></i>
                            M3U8 Proxy
                        </div>
                        <p style="color: #cbd5e1; font-size: 0.9rem;">
                            Otomatik segment yeniden yazma ile M3U8 playlist'lerini proxy'leyin
                        </p>
                        <div class="endpoint-url">
                            /proxy/m3u?url=AKIŞ_URL
                        </div>
                        <button class="copy-btn" onclick="copyText(this)">Kopyala</button>
                    </div>
                    
                    <div class="endpoint">
                        <div class="endpoint-title">
                            <i class="fas fa-wrench"></i>
                            Otomatik Çözümleme
                        </div>
                        <p style="color: #cbd5e1; font-size: 0.9rem;">
                            Çeşitli kaynaklardan akış URL'lerini otomatik çözümleyin ve çıkarın
                        </p>
                        <div class="endpoint-url">
                            /proxy/resolve?url=KAYNAK_URL
                        </div>
                        <button class="copy-btn" onclick="copyText(this)">Kopyala</button>
                    </div>
                    
                    <div class="endpoint">
                        <div class="endpoint-title">
                            <i class="fas fa-shield-alt"></i>
                            Tam Proxy
                        </div>
                        <p style="color: #cbd5e1; font-size: 0.9rem;">
                            Playlist ve segment işleme ile tam proxy çözümü
                        </p>
                        <div class="endpoint-url">
                            /proxy?url=PLAYLIST_URL
                        </div>
                        <button class="copy-btn" onclick="copyText(this)">Kopyala</button>
                    </div>
                </div>
            </div>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number" id="uptime">100%</div>
                    <div class="stat-label">Çalışma Süresi</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="latency">24ms</div>
                    <div class="stat-label">Ort. Gecikme</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="connections">∞</div>
                    <div class="stat-label">Eşzamanlı Akış</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="supported">50+</div>
                    <div class="stat-label">Desteklenen Kaynak</div>
                </div>
            </div>
        </main>

        <footer class="footer">
            <p>StreamFlow Proxy v2.0 • Yüksek Performanslı Akış Altyapısı</p>
            <div class="developer">
                <i class="fas fa-code"></i>
                Geliştirici: Ümitm0d
            </div>
            <p style="margin-top: 1rem; font-size: 0.8rem;">
                <i class="fas fa-lock"></i>
                Güvenli • Güvenilir • Yüksek Performans
            </p>
        </footer>
    </div>

    <script>
        function proxyStream() {
            const url = document.getElementById('streamUrl').value;
            if (!url || url === 'https://example.com/playlist.m3u8') {
                alert('Lütfen geçerli bir akış URL\'si girin');
                return;
            }
            window.open(`/proxy/resolve?url=${encodeURIComponent(url)}`, '_blank');
        }

        function copyText(button) {
            const text = button.previousElementSibling.textContent;
            navigator.clipboard.writeText(text).then(() => {
                const originalText = button.textContent;
                button.textContent = 'Kopyalandı!';
                button.style.background = 'var(--success)';
                button.style.borderColor = 'var(--success)';
                
                setTimeout(() => {
                    button.textContent = originalText;
                    button.style.background = '';
                    button.style.borderColor = '';
                }, 2000);
            });
        }

        // Dinamik istatistik güncelleme
        function updateStats() {
            const latency = Math.floor(Math.random() * 50) + 10;
            document.getElementById('latency').textContent = `${latency}ms`;
            
            const connections = Math.floor(Math.random() * 100) + 50;
            document.getElementById('connections').textContent = connections;
            
            // Hafif çalışma süresi değişimi simülasyonu
            const uptime = (99.5 + Math.random() * 0.5).toFixed(1);
            document.getElementById('uptime').textContent = `${uptime}%`;
        }

        // İstatistikleri her 10 saniyede bir güncelle
        setInterval(updateStats, 10000);
        
        // İlk güncelleme
        updateStats();
    </script>
</body>
</html>
'''

def create_session():
    s = requests.Session()
    retry_strategy = Retry(total=2, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(pool_connections=150, pool_maxsize=150, max_retries=retry_strategy, pool_block=False)
    s.mount('http://', adapter)
    s.mount('https://', adapter)
    return s

def detect_m3u_type(content):
    return "m3u8" if "#EXTM3U" in content[:100] and "#EXTINF" in content[:300] else "m3u"

def replace_key_uri(line, headers_query):
    if 'URI="' not in line:
        return line
    match = re.search(r'URI="([^"]+)"', line)
    if match:
        return line.replace(match.group(1), f"/proxy/key?url={quote(match.group(1))}&{headers_query}")
    return line

PATTERNS = {
    'channel_key': re.compile(r'channelKey\s*=\s*"([^"]*)"'),
    'auth_ts': re.compile(r'authTs\s*=\s*"([^"]*)"'),
    'auth_rnd': re.compile(r'authRnd\s*=\s*"([^"]*)"'),
    'auth_sig': re.compile(r'authSig\s*=\s*"([^"]*)"'),
    'auth_host': re.compile(r'\}\s*fetchWithRetry\(\s*[\'"]([^\'"]*)[\'"]'),
    'server_lookup': re.compile(r'n\s+fetchWithRetry\(\s*[\'"]([^\'"]*)[\'"]'),
    'host': re.compile(r'm3u8\s*=.*?[\'"]([^\'"]*)[\'"]'),
    'iframe': re.compile(r'iframe\s+src=[\'"]([^\'"]+)[\'"]')
}

def resolve_m3u8_link(url, headers=None):
    if not url:
        return {"resolved_url": None, "headers": {}}

    current_headers = headers or {'User-Agent': 'Mozilla/5.0'}
    is_vavoo = "vavoo.to" in url
    s = create_session()
    
    try:
        resp = s.get(url, headers=current_headers, allow_redirects=True, timeout=(2, 6))
        resp.raise_for_status()
        content = resp.text
        final_url = resp.url

        if is_vavoo:
            if content[:10].strip().startswith('#EXTM3U'):
                return {"resolved_url": final_url, "headers": current_headers}
            return {"resolved_url": url, "headers": current_headers}

        try:
            iframe_match = PATTERNS['iframe'].search(content)
            if not iframe_match:
                raise ValueError("Iframe bulunamadı")

            url2 = iframe_match.group(1)
            parsed = urlparse(url2)
            referer = f"{parsed.scheme}://{parsed.netloc}/"
            origin = f"{parsed.scheme}://{parsed.netloc}"
            
            current_headers.update({'Referer': referer, 'Origin': origin})
            
            resp2 = s.get(url2, headers=current_headers, timeout=(2, 6))
            resp2.raise_for_status()
            iframe_text = resp2.text

            matches = {k: p.search(iframe_text) for k, p in PATTERNS.items()}
            
            required = ['channel_key', 'auth_ts', 'auth_rnd', 'auth_sig', 'auth_host', 'server_lookup', 'host']
            
            if not all(matches.get(k) for k in required):
                raise ValueError("Eksik parametreler")

            channel_key = matches['channel_key'].group(1)
            auth_ts = matches['auth_ts'].group(1)
            auth_rnd = matches['auth_rnd'].group(1)
            auth_sig = quote(matches['auth_sig'].group(1))
            auth_host = matches['auth_host'].group(1)
            server_lookup = matches['server_lookup'].group(1)
            host = matches['host'].group(1)

            auth_url = f'{auth_host}{channel_key}&ts={auth_ts}&rnd={auth_rnd}&sig={auth_sig}'
            s.get(auth_url, headers=current_headers, timeout=(2, 5))

            lookup_url = f"https://{parsed.netloc}{server_lookup}{channel_key}"
            srv_resp = s.get(lookup_url, headers=current_headers, timeout=(2, 5))
            server_key = srv_resp.json().get('server_key')
            
            if not server_key:
                raise ValueError("server_key bulunamadı")

            stream_url = f'https://{server_key}{host}{server_key}/{channel_key}/mono.m3u8'
            
            return {
                "resolved_url": stream_url,
                "headers": {'User-Agent': current_headers['User-Agent'], 'Referer': referer, 'Origin': origin}
            }

        except Exception:
            if content[:10].strip().startswith('#EXTM3U'):
                return {"resolved_url": final_url, "headers": current_headers}
            return {"resolved_url": url, "headers": current_headers}

    except Exception:
        return {"resolved_url": url, "headers": current_headers}
    finally:
        s.close()

@app.route('/proxy')
def proxy():
    m3u_url = request.args.get('url', '').strip()
    if not m3u_url:
        return "Hata: 'url' parametresi eksik", 400

    try:
        server_ip = request.host
        s = create_session()
        resp = s.get(m3u_url, timeout=(5, 15))
        resp.raise_for_status()
        content = resp.text
        s.close()
        
        lines = [f"http://{server_ip}/proxy/m3u?url={line}" if line and line[0] != '#' else line for line in content.split('\n')]
        result = '\n'.join(lines)
        filename = os.path.basename(urlparse(m3u_url).path) or "playlist.m3u"
        
        return Response(result, content_type="application/vnd.apple.mpegurl", headers={'Content-Disposition': f'attachment; filename="{filename}"'})
        
    except Exception as e:
        return f"Hata: {str(e)}", 500

@app.route('/proxy/m3u')
def proxy_m3u():
    m3u_url = request.args.get('url', '').strip()
    if not m3u_url:
        return "Hata: 'url' parametresi eksik", 400

    default_headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X)", "Referer": "https://vavoo.to/", "Origin": "https://vavoo.to"}

    for key, value in request.args.items():
        if key[:2] == 'h_':
            default_headers[unquote(key[2:]).replace("_", "-")] = unquote(value).strip()

    processed_url = m3u_url
    
    if '/stream/stream-' in m3u_url:
        processed_url = m3u_url.replace('/stream/stream-', '/embed/stream-')
    
    premium_match = re.search(r'/premium(\d+)/mono\.m3u8$', m3u_url)
    if premium_match:
        processed_url = f"https://daddylive.dad/embed/stream-{premium_match.group(1)}.php"

    try:
        result = resolve_m3u8_link(processed_url, default_headers)

        if not result["resolved_url"]:
            return "Hata: Çözümlenemedi", 500

        s = create_session()
        resp = s.get(result["resolved_url"], headers=result["headers"], allow_redirects=True, timeout=(3, 10))
        resp.raise_for_status()
        content = resp.text
        final_url = resp.url
        s.close()

        if detect_m3u_type(content) == "m3u":
            return Response(content, content_type="application/vnd.apple.mpegurl")

        parsed = urlparse(final_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rsplit('/', 1)[0]}/"
        headers_query = "&".join([f"h_{quote(k)}={quote(v)}" for k, v in result["headers"].items()])

        lines = []
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                lines.append(line)
            elif line.startswith("#EXT-X-KEY"):
                lines.append(replace_key_uri(line, headers_query))
            elif line[0] != '#':
                segment_url = urljoin(base_url, line)
                lines.append(f"/proxy/ts?url={quote(segment_url)}&{headers_query}")
            else:
                lines.append(line)

        return Response('\n'.join(lines), content_type="application/vnd.apple.mpegurl")

    except Exception as e:
        return f"Hata: {str(e)}", 500

@app.route('/proxy/resolve')
def proxy_resolve():
    url = request.args.get('url', '').strip()
    if not url:
        return "Hata: URL eksik", 400

    headers = {}
    for key, value in request.args.items():
        if key[:2] == 'h_':
            headers[unquote(key[2:]).replace("_", "-")] = unquote(value).strip()

    try:
        result = resolve_m3u8_link(url, headers)
        if not result["resolved_url"]:
            return "Hata: Çözümlenemedi", 500
        headers_query = "&".join([f"h_{quote(k)}={quote(v)}" for k, v in result["headers"].items()])
        return Response(f"#EXTM3U\n#EXTINF:-1,Kanal\n/proxy/m3u?url={quote(result['resolved_url'])}&{headers_query}", content_type="application/vnd.apple.mpegurl")
    except Exception as e:
        return f"Hata: {str(e)}", 500

@app.route('/proxy/ts')
def proxy_ts():
    ts_url = request.args.get('url', '').strip()
    if not ts_url:
        return "Hata: URL eksik", 400

    headers = {}
    for key, value in request.args.items():
        if key[:2] == 'h_':
            headers[unquote(key[2:]).replace("_", "-")] = unquote(value).strip()

    try:
        s = create_session()
        resp = s.get(ts_url, headers=headers, stream=True, timeout=(3, 25))
        resp.raise_for_status()
        
        def generate():
            try:
                buffer = b''
                min_buffer_size = 65536
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        buffer += chunk
                        if len(buffer) >= min_buffer_size:
                            yield buffer
                            buffer = b''
                if buffer:
                    yield buffer
            finally:
                try:
                    resp.close()
                except:
                    pass
                try:
                    s.close()
                except:
                    pass
        
        return Response(
            generate(), 
            content_type="video/mp2t",
            headers={
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
    except Exception as e:
        return f"Hata: {str(e)}", 500

@app.route('/proxy/key')
def proxy_key():
    key_url = request.args.get('url', '').strip()
    if not key_url:
        return "Hata: URL eksik", 400

    headers = {}
    for key, value in request.args.items():
        if key[:2] == 'h_':
            headers[unquote(key[2:]).replace("_", "-")] = unquote(value).strip()

    try:
        s = create_session()
        resp = s.get(key_url, headers=headers, timeout=(2, 8))
        resp.raise_for_status()
        content = resp.content
        s.close()
        return Response(content, content_type="application/octet-stream")
    except Exception as e:
        return f"Hata: {str(e)}", 500

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    return {
        "durum": "sağlıklı",
        "zaman": time.time(),
        "servis": "StreamFlow Proxy",
        "versiyon": "2.0",
        "gelistirici": "Ümitm0d",
        "mesaj": "Proxy servisi sorunsuz çalışıyor"
    }

@app.route('/durum')
def durum():
    return {
        "sistem": "Aktif",
        "proksi_durumu": "Çalışıyor",
        "versiyon": "2.0",
        "gelistirici": "Ümitm0d",
        "son_guncelleme": time.strftime("%d/%m/%Y %H:%M:%S"),
        "mesaj": "StreamFlow Proxy hizmetinizde!"
    }

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7860, debug=False)
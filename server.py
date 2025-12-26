#!/usr/bin/env python3
"""
🍎 Mac File Share - Share files across devices
Made with ❤️ by Phong Tran
Email: mr.yutran@gmail.com
"""

import http.server
import socketserver
import os
import sys
import socket
import urllib.parse
import html
import io
import base64
from datetime import datetime

# Port mặc định
PORT = 8888

# Thư mục chia sẻ (mặc định là thư mục Downloads)
SHARE_DIR = os.path.expanduser("~/Downloads")

def get_local_ip():
    """Lấy địa chỉ IP local của máy Mac (ưu tiên IP WiFi 192.168.x.x)"""
    import subprocess
    try:
        # Lấy tất cả IP
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        ips = []
        for line in lines:
            if 'inet ' in line and '127.0.0.1' not in line:
                parts = line.strip().split()
                if len(parts) >= 2:
                    ip = parts[1]
                    ips.append(ip)
        
        # Ưu tiên IP 192.168.x.x (WiFi thường dùng)
        for ip in ips:
            if ip.startswith('192.168.'):
                return ip
        
        # Rồi đến 10.x.x.x
        for ip in ips:
            if ip.startswith('10.'):
                return ip
        
        # Trả về IP đầu tiên nếu có
        if ips:
            return ips[0]
        
        # Fallback
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def format_size(size):
    """Format kích thước file cho dễ đọc"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def get_file_icon(filename):
    """Trả về emoji icon dựa trên loại file"""
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    icons = {
        # Images
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'webp': '🖼️', 'svg': '🖼️', 'ico': '🖼️',
        # Videos
        'mp4': '🎬', 'mov': '🎬', 'avi': '🎬', 'mkv': '🎬', 'wmv': '🎬', 'flv': '🎬',
        # Audio
        'mp3': '🎵', 'wav': '🎵', 'flac': '🎵', 'aac': '🎵', 'm4a': '🎵', 'ogg': '🎵',
        # Documents
        'pdf': '📕', 'doc': '📘', 'docx': '📘', 'xls': '📗', 'xlsx': '📗', 'ppt': '📙', 'pptx': '📙',
        'txt': '📄', 'rtf': '📄', 'md': '📝',
        # Code
        'py': '🐍', 'js': '💛', 'html': '🌐', 'css': '🎨', 'json': '📋', 'xml': '📋',
        'java': '☕', 'cpp': '⚡', 'c': '⚡', 'swift': '🍎', 'go': '🔵',
        # Archives
        'zip': '📦', 'rar': '📦', 'tar': '📦', 'gz': '📦', '7z': '📦', 'dmg': '💿',
        # Others
        'exe': '⚙️', 'app': '📱', 'apk': '🤖',
    }
    return icons.get(ext, '📄')

class FileShareHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SHARE_DIR, **kwargs)
    
    def do_GET(self):
        """Xử lý GET request"""
        # Parse URL
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        
        # Trang chủ hoặc browse thư mục
        if path == '/' or path == '':
            self.send_directory_listing('/')
            return
        
        # Kiểm tra đường dẫn file/folder
        full_path = os.path.join(SHARE_DIR, path.lstrip('/'))
        
        if os.path.isdir(full_path):
            self.send_directory_listing(path)
        elif os.path.isfile(full_path):
            # Download file
            super().do_GET()
        else:
            self.send_error(404, "File not found")
    
    def do_POST(self):
        """Handle file upload from any device"""
        try:
            content_type = self.headers.get('Content-Type', '')
            
            if 'multipart/form-data' in content_type:
                # Parse boundary more robustly
                if 'boundary=' not in content_type:
                    self.send_error(400, "Invalid multipart data")
                    return
                
                boundary = content_type.split('boundary=')[1]
                if boundary.startswith('"') and boundary.endswith('"'):
                    boundary = boundary[1:-1]
                boundary = boundary.encode('utf-8')
                
                # Read content
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                
                # Parse multipart data more robustly
                parts = body.split(b'--' + boundary)
                
                files_uploaded = 0
                for part in parts:
                    if b'Content-Disposition: form-data; name="file"' in part:
                        # Find filename
                        filename = None
                        lines = part.split(b'\r\n')
                        for line in lines:
                            line_str = line.decode('utf-8', errors='ignore')
                            if 'filename="' in line_str:
                                filename_start = line_str.find('filename="') + 10
                                filename_end = line_str.find('"', filename_start)
                                if filename_end > filename_start:
                                    filename = line_str[filename_start:filename_end]
                                break
                        
                        if filename:
                            # Find start position of file content
                            header_end = part.find(b'\r\n\r\n')
                            if header_end != -1:
                                file_content = part[header_end + 4:]
                                # Remove trailing \r\n if present
                                if file_content.endswith(b'\r\n'):
                                    file_content = file_content[:-2]
                                
                                # Sanitize filename
                                filename = os.path.basename(filename)  # Prevent directory traversal
                                
                                # Save file
                                save_path = os.path.join(SHARE_DIR, filename)
                                try:
                                    with open(save_path, 'wb') as f:
                                        f.write(file_content)
                                    print(f"📥 Received file: {filename} ({len(file_content)} bytes)")
                                    files_uploaded += 1
                                except PermissionError:
                                    print(f"❌ Cannot save file: {filename} (no permission)")
                                    self.send_error(403, f"Cannot save file: {filename}")
                                    return
                                except Exception as e:
                                    print(f"❌ Error saving file: {filename} ({e})")
                                    self.send_error(500, f"Error saving file: {filename}")
                                    return
                
                if files_uploaded > 0:
                    print(f"✅ Upload successful: {files_uploaded} file(s)")
                    # Redirect to home page
                    self.send_response(303)
                    self.send_header('Location', '/')
                    self.end_headers()
                else:
                    self.send_error(400, "No files found to upload")
            else:
                self.send_error(400, "Invalid request")
        except Exception as e:
            print(f"❌ Upload error: {e}")
            self.send_error(500, "Server error during upload")
    
    def send_directory_listing(self, path):
        """Send HTML page displaying file list"""
        full_path = os.path.join(SHARE_DIR, path.lstrip('/'))
        
        try:
            entries = os.listdir(full_path)
        except OSError:
            self.send_error(404, "Cannot read directory")
            return
        
        # Sắp xếp: thư mục trước, rồi đến file
        dirs = []
        files = []
        
        for entry in entries:
            if entry.startswith('.'):
                continue
            entry_path = os.path.join(full_path, entry)
            if os.path.isdir(entry_path):
                dirs.append(entry)
            else:
                files.append(entry)
        
        dirs.sort(key=str.lower)
        files.sort(key=str.lower)
        
        # Tạo HTML
        local_ip = get_local_ip()
        server_url = f"http://{local_ip}:{PORT}"
        
        html_content = f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>🍎 Mac File Share</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --bg-gradient-1: #1a1a2e;
            --bg-gradient-2: #16213e;
            --bg-gradient-3: #0f3460;
            --card-bg: rgba(255, 255, 255, 0.08);
            --card-border: rgba(255, 255, 255, 0.12);
            --text-primary: #ffffff;
            --text-secondary: rgba(255, 255, 255, 0.7);
            --accent: #e94560;
            --accent-glow: rgba(233, 69, 96, 0.4);
            --success: #00d9a5;
            --folder-color: #ffd93d;
        }}
        
        body {{
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--bg-gradient-1) 0%, var(--bg-gradient-2) 50%, var(--bg-gradient-3) 100%);
            min-height: 100vh;
            color: var(--text-primary);
            padding: 20px;
            padding-bottom: 100px;
        }}
        
        /* Animated background */
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 80%, rgba(233, 69, 96, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(0, 217, 165, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(255, 217, 61, 0.08) 0%, transparent 40%);
            pointer-events: none;
            z-index: -1;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        /* Header */
        .header {{
            text-align: center;
            padding: 30px 20px;
            margin-bottom: 30px;
            background: var(--card-bg);
            border-radius: 24px;
            border: 1px solid var(--card-border);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }}
        
        .header h1 {{
            font-size: 2.2em;
            font-weight: 700;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #fff 0%, #e94560 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header p {{
            color: var(--text-secondary);
            font-size: 1em;
        }}
        
        .server-info {{
            margin-top: 20px;
            padding: 15px;
            background: rgba(0, 217, 165, 0.1);
            border-radius: 12px;
            border: 1px solid rgba(0, 217, 165, 0.3);
        }}
        
        .server-info code {{
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 1.1em;
            color: var(--success);
            font-weight: 600;
        }}
        
        /* Breadcrumb */
        .breadcrumb {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            padding: 15px 20px;
            background: var(--card-bg);
            border-radius: 16px;
            margin-bottom: 20px;
            border: 1px solid var(--card-border);
        }}
        
        .breadcrumb a {{
            color: var(--accent);
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s;
        }}
        
        .breadcrumb a:hover {{
            text-shadow: 0 0 10px var(--accent-glow);
        }}
        
        .breadcrumb .current-path {{
            color: var(--text-primary);
            font-weight: 600;
            text-decoration: none;
        }}
        
        .breadcrumb span {{
            color: var(--text-secondary);
        }}
        
        /* File List */
        .file-list {{
            background: var(--card-bg);
            border-radius: 20px;
            border: 1px solid var(--card-border);
            overflow: hidden;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }}
        
        .file-item {{
            display: flex;
            align-items: center;
            padding: 16px 20px;
            border-bottom: 1px solid var(--card-border);
            transition: all 0.3s ease;
            text-decoration: none;
            color: inherit;
        }}
        
        .file-item:last-child {{
            border-bottom: none;
        }}
        
        .file-item:hover {{
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(5px);
        }}
        
        .file-item:active {{
            transform: scale(0.98);
        }}
        
        .file-icon {{
            font-size: 2em;
            margin-right: 15px;
            min-width: 45px;
            text-align: center;
        }}
        
        .file-info {{
            flex: 1;
            min-width: 0;
        }}
        
        .file-name {{
            font-weight: 600;
            font-size: 1.05em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 4px;
        }}
        
        .file-meta {{
            font-size: 0.85em;
            color: var(--text-secondary);
        }}
        
        .file-action {{
            padding: 10px 18px;
            background: linear-gradient(135deg, var(--accent), #ff6b6b);
            color: white;
            border-radius: 25px;
            font-size: 0.85em;
            font-weight: 600;
            box-shadow: 0 4px 15px var(--accent-glow);
            transition: all 0.3s;
        }}
        
        .file-item:hover .file-action {{
            transform: scale(1.05);
            box-shadow: 0 6px 20px var(--accent-glow);
        }}
        
        .folder-icon {{
            color: var(--folder-color);
        }}
        
        /* Upload Section */
        .upload-section {{
            margin-top: 30px;
            padding: 30px;
            background: var(--card-bg);
            border-radius: 20px;
            border: 2px dashed var(--card-border);
            text-align: center;
            transition: all 0.3s;
        }}
        
        .upload-section:hover {{
            border-color: var(--accent);
            background: rgba(233, 69, 96, 0.05);
        }}
        
        .upload-section h3 {{
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .upload-form {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }}
        
        .file-input-wrapper {{
            position: relative;
            overflow: hidden;
            display: inline-block;
        }}
        
        .file-input-wrapper input[type=file] {{
            font-size: 100px;
            position: absolute;
            left: 0;
            top: 0;
            opacity: 0;
            cursor: pointer;
        }}
        
        .file-input-btn {{
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 30px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s;
        }}
        
        .file-input-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
        }}
        
        .upload-btn {{
            padding: 15px 40px;
            background: linear-gradient(135deg, var(--success), #00b894);
            color: white;
            border: none;
            border-radius: 30px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0, 217, 165, 0.4);
            transition: all 0.3s;
        }}
        
        .upload-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 217, 165, 0.5);
        }}
        
        #file-name-display {{
            color: var(--text-secondary);
            font-size: 0.9em;
        }}
        
        /* Empty State */
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: var(--text-secondary);
        }}
        
        .empty-state .icon {{
            font-size: 4em;
            margin-bottom: 20px;
            opacity: 0.5;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: var(--text-secondary);
            font-size: 0.9em;
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .file-item {{
            animation: fadeIn 0.4s ease forwards;
        }}
        
        .file-item:nth-child(1) {{ animation-delay: 0.05s; }}
        .file-item:nth-child(2) {{ animation-delay: 0.1s; }}
        .file-item:nth-child(3) {{ animation-delay: 0.15s; }}
        .file-item:nth-child(4) {{ animation-delay: 0.2s; }}
        .file-item:nth-child(5) {{ animation-delay: 0.25s; }}
        
        /* Responsive */
        @media (max-width: 600px) {{
            body {{
                padding: 15px;
            }}
            
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .file-action {{
                padding: 8px 14px;
                font-size: 0.8em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🍎 Mac File Share</h1>
            <p>Chia sẻ file dễ dàng giữa các thiết bị qua WiFi</p>
            
            <div class="server-info">
                <p>📡 Truy cập từ bất kỳ thiết bị:</p>
                <code>{server_url}</code>
            </div>
        </header>
        
        <nav class="breadcrumb">
            <span>📍</span>
            {self.generate_breadcrumb(path)}
        </nav>
        
        <div class="file-list">
'''
        
        # Nút quay lại
        if path != '/':
            parent = os.path.dirname(path.rstrip('/'))
            if not parent:
                parent = '/'
            html_content += f'''
            <a href="{parent}" class="file-item">
                <span class="file-icon">⬆️</span>
                <div class="file-info">
                    <div class="file-name">..</div>
                    <div class="file-meta">Quay lại thư mục trước</div>
                </div>
            </a>
'''
        
        # Liệt kê thư mục
        for d in dirs:
            dir_path = os.path.join(path, d)
            html_content += f'''
            <a href="{urllib.parse.quote(dir_path)}" class="file-item">
                <span class="file-icon folder-icon">📁</span>
                <div class="file-info">
                    <div class="file-name">{html.escape(d)}</div>
                    <div class="file-meta">Thư mục</div>
                </div>
                <span class="file-action">Mở</span>
            </a>
'''
        
        # Liệt kê file
        for f in files:
            file_path = os.path.join(full_path, f)
            file_size = os.path.getsize(file_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%d/%m/%Y %H:%M')
            download_path = os.path.join(path, f)
            icon = get_file_icon(f)
            
            html_content += f'''
            <a href="{urllib.parse.quote(download_path)}" class="file-item" download>
                <span class="file-icon">{icon}</span>
                <div class="file-info">
                    <div class="file-name">{html.escape(f)}</div>
                    <div class="file-meta">{format_size(file_size)} • {mod_time}</div>
                </div>
                <span class="file-action">Tải ⬇️</span>
            </a>
'''
        
        # Trường hợp thư mục rỗng
        if not dirs and not files:
            html_content += '''
            <div class="empty-state">
                <div class="icon">📭</div>
                <p>Thư mục này đang trống</p>
            </div>
'''
        
        html_content += '''
        </div>
        
        <div class="upload-section">
            <h3>📤 Upload file từ thiết bị lên Mac</h3>
            <form class="upload-form" method="POST" enctype="multipart/form-data">
                <div class="file-input-wrapper">
                    <span class="file-input-btn">📎 Chọn file</span>
                    <input type="file" name="file" id="file-input" onchange="updateFileName(this)">
                </div>
                <p id="file-name-display">Chưa chọn file nào</p>
                <button type="submit" class="upload-btn">🚀 Upload</button>
            </form>
        </div>
        
        <footer class="footer">
            <p>💡 Đảm bảo Mac và thiết bị khác cùng kết nối WiFi</p>
            <p>Made with ❤️ by Phong Tran | <a href="mailto:mr.yutran@gmail.com" style="color: #00d9a5;">mr.yutran@gmail.com</a></p>
        </footer>
    </div>
    
    <script>
        function updateFileName(input) {
            const display = document.getElementById('file-name-display');
            if (input.files.length > 0) {
                display.textContent = '📄 ' + input.files[0].name;
                display.style.color = '#00d9a5';
            } else {
                display.textContent = 'Chưa chọn file nào';
                display.style.color = 'rgba(255, 255, 255, 0.7)';
            }
        }
        
        function copyToClipboard(text) {
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(text).then(function() {
                    alert('✅ Đã sao chép URL vào clipboard!');
                }, function(err) {
                    fallbackCopyTextToClipboard(text);
                });
            } else {
                fallbackCopyTextToClipboard(text);
            }
        }
        
        function fallbackCopyTextToClipboard(text) {
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            textArea.style.left = "-999999px";
            textArea.style.top = "-999999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
                alert('✅ Đã sao chép URL vào clipboard!');
            } catch (err) {
                alert('❌ Không thể sao chép. Vui lòng chọn và copy thủ công: ' + text);
            }
            document.body.removeChild(textArea);
        }
    </script>
</body>
</html>
'''
        
        # Gửi response
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(html_content.encode()))
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def generate_breadcrumb(self, path):
        """Tạo breadcrumb navigation"""
        if path == '/' or path == '':
            return '<span class="current-path">Home</span>'
        
        parts = path.strip('/').split('/')
        breadcrumb = '<a href="/">Home</a>'
        current_path = ''
        
        for part in parts:
            current_path += '/' + part
            if current_path == path:
                # Last item - current location
                breadcrumb += f' <span>›</span> <span class="current-path">{html.escape(part)}</span>'
            else:
                breadcrumb += f' <span>›</span> <a href="{current_path}">{html.escape(part)}</a>'
        
        return breadcrumb
    
    def send_error(self, code, message=None, explain=None):
        """Override send_error to handle UTF-8 encoding properly"""
        import html
        
        # Keep the original message for the body
        original_message = message
        
        # Set default message if none provided
        if message is None:
            if code in self.responses:
                message = self.responses[code][0]
            else:
                message = ''
        
        # For status line, use ASCII version
        ascii_message = message
        try:
            message.encode('ascii')
        except UnicodeEncodeError:
            ascii_message = 'Error'  # Fallback to ASCII
        
        # Send response line with ASCII message
        self.send_response_only(code, ascii_message)
        
        # Send headers
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Connection', 'close')
        self.end_headers()
        
        # Send HTML body with proper encoding
        content = f'''<!DOCTYPE html>
<html>
<head>
    <title>{code} {html.escape(original_message or message)}</title>
    <meta charset="utf-8">
</head>
<body>
    <h1>{code} {html.escape(original_message or message)}</h1>
    {f"<p>{html.escape(explain)}</p>" if explain else ""}
    <hr>
    <address>{self.version_string()}</address>
</body>
</html>'''
        
        self.wfile.write(content.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")


def generate_simple_qr_ascii(url):
    """Generate simple ASCII QR code for terminal"""
    # Create simple text art for QR code
    qr_art = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    📱 MAC FILE SHARE                         ║
║                                                              ║
║  🌐 URL: {url:<50} ║
║                                                              ║
║  📋 How to access:                                           ║
║     1. Open browser on any device                          ║
║     2. Type the URL above into browser address bar          ║
║                                                              ║
║  💡 Or copy and paste the URL: {url:<29} ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    return qr_art

def main():
    global SHARE_DIR, PORT
    
    # Process arguments
    if len(sys.argv) > 1:
        custom_dir = os.path.expanduser(sys.argv[1])
        if os.path.isdir(custom_dir):
            SHARE_DIR = custom_dir
        else:
            print(f"❌ Directory does not exist: {sys.argv[1]}")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            PORT = int(sys.argv[2])
        except ValueError:
            print("❌ Invalid port")
            sys.exit(1)
    
    # Get IP
    local_ip = get_local_ip()
    server_url = f"http://{local_ip}:{PORT}"
    
    # Banner
    print("\n" + "="*70)
    print("  🍎 MAC FILE SHARE - Share files across devices")
    print("="*70)
    print(f"\n  📁 Share directory: {SHARE_DIR}")
    print(f"\n  🌐 Access URL: {server_url}")
    
    # Display QR code ASCII
    print(f"\n{generate_simple_qr_ascii(server_url)}")
    
    print(f"  💡 Open browser on any device and enter the URL above")
    print(f"\n  ⏹️  Press Ctrl+C to stop server")
    print("\n" + "="*70 + "\n")
    
    # Start server
    with socketserver.TCPServer(("", PORT), FileShareHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()


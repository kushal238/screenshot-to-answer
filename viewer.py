#!/usr/bin/env python3
"""
Simple web server to view markdown files in browser
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import markdown2
from pathlib import Path
import json

PORT = 8080

class MarkdownHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/answers':
            self.serve_markdown('answers.md', 'Screenshot Answers (Live)')
        elif self.path == '/readme':
            self.serve_markdown('README.md', 'README')
        elif self.path == '/status.json':
            self.serve_file('status.json', 'application/json')
        else:
            self.send_error(404)
            
    def serve_file(self, filename, content_type):
        try:
            filepath = Path(__file__).parent / filename
            if not filepath.exists():
                self.wfile.write(b'{}')
                return
                
            with open(filepath, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)
        except Exception:
            self.wfile.write(b'{}')
    
    def serve_markdown(self, filename, title):
        try:
            filepath = Path(__file__).parent / filename
            with open(filepath, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            html_content = markdown2.markdown(markdown_content, extras=['tables', 'fenced-code-blocks'])
            
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
            display: flex;
            gap: 20px;
        }}
        
        .main-content {{
            flex: 3;
        }}
        
        .sidebar {{
            flex: 1;
            min-width: 250px;
        }}
        
        .exam-card {{
            background: white;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
            overflow: hidden;
            position: sticky;
            top: 20px;
        }}
        
        .exam-header {{
            background-color: #6c757d; /* Gray */
            color: white;
            padding: 10px 15px;
            font-weight: 600;
            font-size: 14px;
        }}
        
        .exam-body {{
            padding: 15px;
        }}
        
        .exam-stat {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 13px;
            color: #555;
        }}
        
        .exam-stat strong {{
            color: #333;
        }}
        
        .status-badge {{
            background-color: #28a745;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
        }}
        
        /* Hide main H1 since we have headers */
        h1 {{
            display: none;
        }}
        
        /* Question Card Style */
        h2 {{
            background: white;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            padding: 0;
            overflow: hidden;
            border: 1px solid #e0e0e0;
            font-size: 16px;
            display: flex;
            flex-direction: column;
        }}
        
        /* The "Screenshot: ..." part becomes the card header */
        h2::before {{
            content: "Question Analysis";
            display: block;
            background-color: #007bff; /* PrairieLearn Blue */
            color: white;
            padding: 10px 15px;
            font-weight: 600;
            font-size: 14px;
        }}
        
        /* Hide the actual "Screenshot: ..." text but keep it accessible if needed */
        h2 {{
            font-size: 0; /* Hide the text */
        }}
        h2::after {{
            content: attr(data-original-text); /* Restore text nicely */
            font-size: 12px;
            color: #666;
            padding: 8px 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #eee;
            display: block;
        }}

        /* Content inside the card */
        p, ul, ol {{
            font-size: 14px;
            line-height: 1.5;
            margin: 0;
            padding: 0 15px;
            background: white;
        }}
        
        /* Add spacing between paragraphs */
        p {{
            padding-bottom: 10px;
        }}
        
        /* Time stamp styling */
        strong {{
            font-weight: 600;
            color: #555;
        }}
        
        /* Answer section highlighting */
        p:nth-of-type(2), p:nth-of-type(3) {{
            padding-left: 15px;
            padding-right: 15px;
        }}

        /* Divider styling */
        hr {{
            border: 0;
            margin: 30px 0;
            height: 0;
        }}
        
        /* Badge for confidence */
        .confidence-high {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            background-color: #d4edda;
            color: #155724;
            font-size: 12px;
            font-weight: 600;
            margin-left: 5px;
        }}

        /* Navbar */
        .nav {{
            background: #343a40;
            padding: 10px 20px;
            border-radius: 6px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .nav a {{
            color: white;
            text-decoration: none;
            font-weight: 500;
            font-size: 14px;
        }}
        .refresh-info {{
            color: #adb5bd;
            font-size: 12px;
        }}
    </style>
    <script>
        // Auto-refresh every 3 seconds for answers page
        if (window.location.pathname === '/answers' || window.location.pathname === '/') {{
            setTimeout(() => location.reload(), 3000);
            
            // Poll status immediately
            fetch('/status.json')
                .then(response => response.json())
                .then(data => {{
                    if (data.status) {{
                        document.getElementById('status-text').innerText = data.status;
                        document.getElementById('status-details').innerText = data.details || '';
                        document.getElementById('status-time').innerText = data.time || '';
                        
                        const badge = document.getElementById('status-badge');
                        if (data.status === 'Processing') {{
                            badge.style.backgroundColor = '#ffc107';
                            badge.style.color = '#212529';
                            badge.innerText = 'Processing...';
                        }} else if (data.status === 'Completed') {{
                            badge.style.backgroundColor = '#28a745';
                            badge.style.color = 'white';
                            badge.innerText = 'Ready';
                        }} else if (data.status === 'Error') {{
                            badge.style.backgroundColor = '#dc3545';
                            badge.style.color = 'white';
                            badge.innerText = 'Error';
                        }}
                    }}
                }})
                .catch(e => console.log(e));
        }}
        
        // Post-processing to clean up the Markdown HTML structure
        document.addEventListener('DOMContentLoaded', function() {{
            // Add data attribute to h2 for the CSS trick
            document.querySelectorAll('h2').forEach(h2 => {{
                h2.setAttribute('data-original-text', h2.innerText);
                
                // Group content following h2 into a div card-body
                let next = h2.nextElementSibling;
                const cardBody = document.createElement('div');
                cardBody.className = 'card-body';
                cardBody.style.backgroundColor = 'white';
                cardBody.style.padding = '15px';
                cardBody.style.border = '1px solid #e0e0e0';
                cardBody.style.borderTop = 'none';
                cardBody.style.borderRadius = '0 0 6px 6px';
                cardBody.style.marginTop = '-20px'; // Overlap header margin
                cardBody.style.marginBottom = '30px';
                
                h2.parentNode.insertBefore(cardBody, next);
                
                while (next && next.tagName !== 'H2' && next.tagName !== 'HR') {{
                    const current = next;
                    next = next.nextElementSibling;
                    cardBody.appendChild(current);
                }}
            }});
            
            // Remove HRs as we use cards now
            document.querySelectorAll('hr').forEach(hr => hr.remove());
        }});
    </script>
</head>
<body>
    <div class="nav">
        <div style="display: flex; align-items: center;">
            <a href="/answers">📊 Answers (Live)</a>
            <a href="/readme">📖 README</a>
        </div>
        <span class="refresh-info">Auto-refreshing</span>
    </div>
    
    <div class="container">
        <div class="main-content">
            {html_content}
        </div>
        
        <div class="sidebar">
            <div class="exam-card">
                <div class="exam-header">
                    Assessment Overview
                </div>
                <div class="exam-body">
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                        Final Exam
                    </div>
                    <div class="exam-stat">
                        <span>Status:</span>
                        <span id="status-badge" class="status-badge">Idle</span>
                    </div>
                    <div class="exam-stat" style="display: block; margin-top: 5px;">
                        <div id="status-text" style="font-weight: bold; color: #007bff; margin-bottom: 2px;">Waiting...</div>
                        <div id="status-details" style="font-size: 11px; color: #666;"></div>
                        <div id="status-time" style="font-size: 10px; color: #999; margin-top: 2px;"></div>
                    </div>
                    <div style="margin: 10px 0; border-bottom: 1px solid #eee;"></div>
                    <div class="exam-stat">
                        <span>Course:</span>
                        <strong>CS 470</strong>
                    </div>
                    <div class="exam-stat">
                        <span>Total Questions:</span>
                        <strong>35</strong>
                    </div>
                    <div class="exam-stat">
                        <span>Time Remaining:</span>
                        <strong>--:--</strong>
                    </div>
                    <div style="margin-top: 15px; font-size: 12px; color: #888;">
                        Screenshots are processed automatically.
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error: {str(e)}")
    
    def log_message(self, format, *args):
        # Suppress log messages
        pass

if __name__ == '__main__':
    server = HTTPServer(('localhost', PORT), MarkdownHandler)
    print(f"""
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║            Markdown Viewer Server                     ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

🌐 Server running at:

   📊 Answers (Live):  http://localhost:{PORT}/answers
   📖 README:          http://localhost:{PORT}/readme

🔄 Answers page auto-refreshes every 3 seconds
🛑 Press Ctrl+C to stop

""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")

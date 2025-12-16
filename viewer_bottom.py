#!/usr/bin/env python3
"""
Secondary web server: Shows answers with NEWEST AT BOTTOM (Chronological)
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import markdown2
from pathlib import Path
import re

PORT = 8081  # Different port from main viewer

class MarkdownHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/answers':
            self.serve_markdown('answers.md', 'Screenshot Answers (Chronological)')
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
                content = f.read()
            
            # REVERSE THE ORDER for this viewer
            # Content structure: Header + Newest + Older + ...
            # We want: Header + Oldest + Newer + ... + Newest
            
            # Split header and body
            parts = content.split('---\n', 1)
            header = parts[0] + '---\n'
            body = parts[1] if len(parts) > 1 else ""
            
            # Split questions (they are separated by ---)
            questions = body.split('---\n')
            
            # Filter out empty strings and reverse
            questions = [q for q in questions if q.strip()]
            questions.reverse()
            
            # Reassemble
            reversed_content = header + '\n---\n'.join(questions)
            
            html_content = markdown2.markdown(reversed_content, extras=['tables', 'fenced-code-blocks'])
            
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
            padding-bottom: 50px; /* Space for auto-scroll */
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
        
        /* Status Card at Bottom */
        .status-card {{
            background: white;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
            margin-top: 20px;
            overflow: hidden;
            border-left: 4px solid #6c757d; /* Default Gray */
        }}
        
        .status-header {{
            padding: 10px 15px;
            font-weight: 600;
            font-size: 14px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .status-body {{
            padding: 15px;
            font-size: 13px;
            color: #555;
        }}
        
        .exam-header {{
            background-color: #6c757d; /* Gray (Matches Main Viewer) */
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
        
        h2::before {{
            content: "Question Analysis";
            display: block;
            background-color: #007bff; /* PrairieLearn Blue (Matches Main Viewer) */
            color: white;
            padding: 10px 15px;
            font-weight: 600;
            font-size: 14px;
        }}
        
        h2 {{ font-size: 0; }}
        h2::after {{
            content: attr(data-original-text);
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
        
        p {{ padding-bottom: 10px; }}
        strong {{ font-weight: 600; color: #555; }}
        
        p:nth-of-type(2), p:nth-of-type(3) {{
            padding-left: 15px;
            padding-right: 15px;
        }}

        hr {{ border: 0; margin: 30px 0; height: 0; }}
        
        .nav {{
            background: #343a40;
            padding: 10px 20px;
            border-radius: 6px;
            margin-bottom: 20px;
            color: white;
            font-size: 14px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
        }}
        
        /* Hide main H1 */
        h1 {{
            display: none;
        }}
    </style>
    <script>
        // Auto-refresh every 3 seconds
        setTimeout(() => {{
            location.reload();
        }}, 3000);
        
        // Poll status immediately
        fetch('/status.json')
            .then(response => response.json())
            .then(data => {{
                if (data.status) {{
                    // Update Sidebar (if keeping it)
                    // ... existing sidebar updates ...
                    
                    // Update Bottom Status Card
                    const statusCard = document.getElementById('bottom-status-card');
                    const statusBadge = document.getElementById('bottom-status-badge');
                    const statusText = document.getElementById('bottom-status-text');
                    const statusDetails = document.getElementById('bottom-status-details');
                    
                    if (data.status === 'Processing') {{
                        statusCard.style.borderLeftColor = '#ffc107'; // Yellow
                        statusBadge.style.backgroundColor = '#ffc107';
                        statusBadge.style.color = '#212529';
                        statusBadge.innerText = 'Processing';
                        statusText.innerText = 'Analyzing Screenshot...';
                        statusText.style.color = '#856404';
                    }} else if (data.status === 'Completed') {{
                        statusCard.style.borderLeftColor = '#28a745'; // Green
                        statusBadge.style.backgroundColor = '#28a745';
                        statusBadge.style.color = 'white';
                        statusBadge.innerText = 'Ready';
                        statusText.innerText = 'Waiting for next screenshot';
                        statusText.style.color = '#155724';
                    }} else if (data.status === 'Error') {{
                        statusCard.style.borderLeftColor = '#dc3545'; // Red
                        statusBadge.style.backgroundColor = '#dc3545';
                        statusBadge.style.color = 'white';
                        statusBadge.innerText = 'Error';
                        statusText.innerText = 'Something went wrong';
                        statusText.style.color = '#721c24';
                    }}
                    
                    statusDetails.innerText = (data.details || '') + ' (' + (data.time || '') + ')';
                }}
            }})
            .catch(e => console.log(e));
        
        // Auto-scroll to bottom
        window.onload = function() {{
            window.scrollTo(0, document.body.scrollHeight);
        }};
        
        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelectorAll('h2').forEach(h2 => {{
                h2.setAttribute('data-original-text', h2.innerText);
                let next = h2.nextElementSibling;
                const cardBody = document.createElement('div');
                cardBody.className = 'card-body';
                cardBody.style.backgroundColor = 'white';
                cardBody.style.padding = '15px';
                cardBody.style.border = '1px solid #e0e0e0';
                cardBody.style.borderTop = 'none';
                cardBody.style.borderRadius = '0 0 6px 6px';
                cardBody.style.marginTop = '-20px';
                cardBody.style.marginBottom = '30px';
                h2.parentNode.insertBefore(cardBody, next);
                while (next && next.tagName !== 'H2' && next.tagName !== 'HR') {{
                    const current = next;
                    next = next.nextElementSibling;
                    cardBody.appendChild(current);
                }}
            }});
            document.querySelectorAll('hr').forEach(hr => hr.remove());
        }});
    </script>
</head>
<body>
    <div class="nav">
        <span>📊 Answers Viewer (Chronological)</span>
        <span style="font-size: 12px; color: #adb5bd;">Newest at Bottom ⬇️</span>
    </div>
    
    <div class="container">
        <div class="main-content">
            {html_content}
            
            <!-- New Status Card at Bottom -->
            <div id="bottom-status-card" class="status-card">
                <div class="status-header">
                    <span id="bottom-status-text">System Status</span>
                    <span id="bottom-status-badge" class="status-badge">Checking...</span>
                </div>
                <div id="bottom-status-details" class="status-body">
                    Connecting to watcher...
                </div>
            </div>
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
                        <span class="status-badge">In Progress</span>
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
        pass

if __name__ == '__main__':
    server = HTTPServer(('localhost', PORT), MarkdownHandler)
    print(f"""
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║        Secondary Viewer (Chronological Mode)          ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

🌐 Running at: http://localhost:{PORT}/answers

⬇️  Shows answers with NEWEST AT THE BOTTOM
🔄 Auto-refreshes and auto-scrolls to bottom
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")


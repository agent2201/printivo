import http.server
import socketserver
import os
import json
import sys
import subprocess

PORT = 8085
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "READY_TO_PRINT", "nesting_data.json")

class NestingDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/nesting_data':
            if os.path.exists(DATA_PATH):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(DATA_PATH, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Nesting data not found. Run START_WORK.bat first.")
        elif self.path.startswith('/api/rebuild'):
            import urllib.parse
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            margin = params.get('margin', ['5'])[0]
            
            print(f"[REBUILD] Re-Calculated roll with margin: {margin}mm")
            # Run nesting with new margin
            cmd = [sys.executable, os.path.join(PROJECT_ROOT, "core", "nesting.py"), "--margin", margin]
            subprocess.run(cmd)
            
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        elif self.path.startswith('/api/qc_decision'):
            import urllib.parse
            import requests # We'll assume requests is available or use urllib
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            job_id = params.get('id', ['0'])[0]
            name = params.get('name', [''])[0]
            decision = params.get('decision', ['pending'])[0]
            
            print(f"[QC] Decision for Job {job_id} ({name}): {decision}")
            
            # 1. Update Main API (if ID is valid)
            if job_id != '0':
                new_status = 'return' if decision == 'rework' else 'nesting' # approved means it stays in nesting
                try:
                    # Sync with main nexus_api on port 8000
                    import urllib.request
                    api_url = f"http://localhost:8000/api/job/{job_id}/status/{new_status}"
                    req = urllib.request.Request(api_url, method='POST')
                    with urllib.request.urlopen(req) as response:
                        print(f"[QC] API Sync status: {response.status}")
                except Exception as e:
                    print(f"[QC] API Sync failed: {e}")

            # 2. Persist/Remove in nesting_data.json
            if os.path.exists(DATA_PATH):
                with open(DATA_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if decision == 'rework':
                    # Remove from nesting if it needs rework
                    data['items'] = [item for item in data.get('items', []) if item.get('name') != name]
                else:
                    # Just update status locally
                    for item in data.get('items', []):
                        if item.get('name') == name:
                            item['status'] = decision
                
                with open(DATA_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
        elif self.path.startswith('/RAW/'):
            # Serve files from the RAW folder
            rel_path = self.path[5:] # Remove '/RAW/'
            raw_file_path = os.path.join(PROJECT_ROOT, "RAW", rel_path)
            if os.path.exists(raw_file_path):
                self.send_response(200)
                # Simple type detection
                if raw_file_path.endswith('.jpg'): self.send_header('Content-type', 'image/jpeg')
                elif raw_file_path.endswith('.png'): self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open(raw_file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Raw file not found")
        else:
            # Change directory to serve static files from www
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            super().do_GET()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.TCPServer(("", PORT), NestingDashboardHandler) as httpd:
        print(f"==================================================")
        print(f"  NEXUS DASHBOARD LIVE AT: http://localhost:{PORT}")
        print(f"==================================================")
        httpd.serve_forever()

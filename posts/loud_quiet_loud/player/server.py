import http.server
import socketserver
import json
import os
import sys

PORT = 8080
DIRECTORY = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data)
                track_id = data.get('trackId')
                regions = data.get('regions')
                
                if not track_id:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'Missing trackId')
                    return

                # Ensure directory exists
                os.makedirs('golden_data', exist_ok=True)
                
                # Save to file
                filename = f"golden_data/{track_id}.json"
                with open(filename, 'w') as f:
                    json.dump(regions, f, indent=2)
                
                print(f"Saved golden data for {track_id}")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "success"}')
                
            except Exception as e:
                print(f"Error saving data: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_error(404)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    # Change directory to the player directory if not already there
    if os.path.exists('index.html') and os.path.exists('manifest.json'):
        pass # We are in the right place
    elif os.path.exists('player/index.html'):
        os.chdir('player')
    
    print(f"Serving at port {PORT}")
    print(f"Make sure you are running this from posts/loud_quiet_loud/player/ or valid root")
    
    # Allow address reuse
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")
            httpd.server_close()

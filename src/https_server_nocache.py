#!/usr/bin/env python3

"""
https_server_nocache.py - HTTP/HTTPS server disables browser caching for sensitive data security.

Synopsis:
    Temporary HTTP/HTTPS server for LAN file sharing with:
    - No browser caching
    - Optional HTTPS
    - Optional Basic Authentication

Purpose:
    Safely share sensitive files (e.g., personal or financial) within a trusted
    LAN environment. Designed for temporary use; not recommended for internet exposure.

HTTPS Self-Signed Certificate:
    To enable HTTPS, you need a certificate and private key.
    Use OpenSSL to create them:

      $ openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout key.pem

    Place cert.pem and key.pem in the same directory as this script.
    Then launch the server with:

      $ python secure_nocache_http_server.py --port 8443 \
          --directory "/path/to/files" --username user --password pass \
          --certfile cert.pem --keyfile key.pem
"""

import argparse
import base64
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import ssl
import sys

class SecureNoCacheHandler(SimpleHTTPRequestHandler):
    """
    HTTP handler with:
    - Cache disabled
    - Basic authentication
    """

    def __init__(self, *args, username=None, password=None, **kwargs):
        self.auth_username = username
        self.auth_password = password
        super().__init__(*args, **kwargs)

    def end_headers(self):
        """Insert cache-control headers before finishing headers"""
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_AUTHHEAD(self):
        """Send 401 Unauthorized response for failed authentication"""
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="LAN Secure Server"')
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def authenticate(self):
        """Verify Authorization header matches username/password"""
        auth_header = self.headers.get('Authorization')
        if auth_header is None or not auth_header.startswith('Basic '):
            return False
        encoded = auth_header.split(' ')[1]
        decoded = base64.b64decode(encoded).decode('utf-8')
        user, passwd = decoded.split(':', 1)
        return user == self.auth_username and passwd == self.auth_password

    def do_GET(self):
        """Handle GET requests with authentication check"""
        if self.auth_username and self.auth_password:
            if not self.authenticate():
                self.do_AUTHHEAD()
                self.wfile.write(b'Authentication required')
                return
        super().do_GET()

    def do_HEAD(self):
        """Handle HEAD requests with authentication check"""
        if self.auth_username and self.auth_password:
            if not self.authenticate():
                self.do_AUTHHEAD()
                return
        super().do_HEAD()


def parse_args():
    """Parse command-line arguments"""
    example_text = '''\
Example usage:

  # Simple LAN HTTP server with authentication
  python secure_nocache_http_server.py --directory "/path/to/files" --port 8080 --username user --password pass

  # HTTPS server with authentication
  python secure_nocache_http_server.py --directory "/path/to/files" --port 8443 \\
      --username user --password pass --certfile cert.pem --keyfile key.pem
'''
    parser = argparse.ArgumentParser(
        description="Secure no-cache HTTP/HTTPS server for LAN.",
        epilog=example_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("-d", "--directory", type=str, default=os.getcwd(), help="Directory to serve")
    parser.add_argument("-u", "--username", type=str, default=None, help="Basic Auth username")
    parser.add_argument("-p", "--password", type=str, default=None, help="Basic Auth password")
    parser.add_argument("-c", "--certfile", type=str, default=None, help="SSL certificate file for HTTPS")
    parser.add_argument("-k", "--keyfile", type=str, default=None, help="SSL private key file for HTTPS")
    return parser.parse_args()


def main():
    """Set up and run the HTTPS/HTTP server"""
    args = parse_args()

    os.chdir(args.directory)
    server_address = ("0.0.0.0", args.port)
    handler = lambda *a, **kw: SecureNoCacheHandler(*a, username=args.username, password=args.password, **kw)
    httpd = HTTPServer(server_address, handler)

    # Enable SSL if certfile and keyfile are provided
    if args.certfile and args.keyfile:
        if not os.path.exists(args.certfile) or not os.path.exists(args.keyfile):
            print("SSL certificate or key file not found.")
            sys.exit(1)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=args.certfile, keyfile=args.keyfile)
        
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        protocol = "https"
    else:
        protocol = "http"

    print(f"Serving directory: {args.directory}")
    print(f"{protocol.upper()} server listening on port {args.port}")
    if args.username:
        print(f"Basic Auth enabled: user={args.username}")
    else:
        print("No authentication enabled")
    print("Browser caching is disabled")
    print("Press CTRL+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    finally:
        httpd.server_close()
        print("Server resources released")


if __name__ == "__main__":
    main()

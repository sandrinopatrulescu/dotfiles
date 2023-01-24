#!/usr/bin/env python
""" (c) Sun Junyi, https://gist.github.com/fxsjy/5465353 """
"""
https://yaler.net/simple-python-web-server
https://www.pythonpool.com/python-http-server/
"""
import sys
import base64
import http.server
from functools import partial

key = ""
Handler = http.server.SimpleHTTPRequestHandler


class AuthHandler(Handler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        global key
        if self.headers.get('Authorization') is None:
            self.do_AUTHHEAD()
            self.wfile.write('no auth header received'.encode())
        elif self.headers.get('Authorization') == 'Basic ' + key.decode():
            Handler.do_GET(self)
        else:
            self.do_AUTHHEAD()
            self.wfile.write(self.headers.get('Authorization').encode())
            self.wfile.write('not authenticated')


def test(HandlerClass=AuthHandler,
         ServerClass=http.server.HTTPServer):
    http.server.test(partial(HandlerClass, directory=sys.argv[1]), ServerClass, port=int(sys.argv[2]))


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("usage BasicAuthServer.py [directory] [port] [username:password]")
        sys.exit()
    key = base64.b64encode(sys.argv[3].encode())
    test()

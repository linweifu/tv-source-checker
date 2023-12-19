'''
Descripttion: tv-source-checker
version: 1.0
Author: 
Date: 2023-12-13 20:32:47
LastEditors: linweifu
LastEditTime: 2023-12-19 21:06:14
'''
from settings import *
import logging
import logging.config
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
import utils
import os
from urllib.parse import urlparse


# 加载日志配置
logging.config.dictConfig(LOGGING_CONFIG)

# 获取logger实例
# logger = logging.getLogger(__file__)
logger = logging.getLogger('http.server')

class RequestHandler(BaseHTTPRequestHandler):
    pac_context = None
    list_dir = True

    def read_pac(self):
        if self.pac_context is None:
            with open("proxy.pac", "rb") as f:
                pac_proxy_server = os.environ.get(
                    'PAC_PROXY', "PROXY localhost:7890")
                pac_str = f.read().decode()
                logger.info(f"env pac-proxy:{pac_proxy_server}")
                self.pac_context = pac_str.replace(
                    "__PROXY__", pac_proxy_server, 1).encode()
        return self.pac_context

    def proxy_url(self, forward_url):
        response = utils.web_get_clash_subscribe(forward_url)
        if response is None:
            self.response_404()
        else:
            self.send_response(200)
            self.send_header(CONTENT_TYPE, response[1])
            self.end_headers()
            self.wfile.write(response[0])

    def response_pac(self):
        self.send_response(200)
        self.send_header(CONTENT_TYPE, 'application/x-ns-proxy-autoconfig')
        self.end_headers()
        self.wfile.write(self.read_pac())

    def response_404(self):
        self.send_response(404)
        self.send_header(CONTENT_TYPE, 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Page not found')
    
    def response_403(self):
        self.send_response(403)
        self.send_header(CONTENT_TYPE, 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Forbidden')
    
    def response_dir(self, dir_path):
        ref_path = dir_path[1:]
        if dir_path != '/' and utils.is_subpath(ref_path) == False:
            self.response_403()
            return 
        if utils.folder_exists(ref_path):
            # 返回路径下的所有文件列表
            file_list = utils.list_dir(ref_path)
            dir_name = dir_path[:-1]
            if dir_path =="/":
                dir_name = "Home Directory"
            file_list_html = f'<h2>目录: {dir_name}</h2><ul>'
            
            if dir_path != '/':
                file_list_html += f'<li><a href="/">根目录</a></li>'
                file_list_html += f'<li><a href="../">上一级</a></li>'
            for file_name in file_list:
                path = dir_path + file_name
                if utils.folder_exists(path[1:]):
                    file_name +='/'
                    path = dir_path + file_name
                file_list_html += f'<li><a href="{path}">{file_name}</a></li>'
            file_list_html += '</ul>'
            self.send_response(200)
            self.send_header(CONTENT_TYPE, 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(file_list_html.encode())
        else:
            self.response_404()

    def response_file(self, file_path):
        ref_path = file_path[1:]
        if not utils.is_subpath(ref_path):
            self.response_403()
        if utils.file_exists(ref_path):
            content = utils.read_file_content(ref_path).encode()
            content_type=utils.get_content_type(file_path)
            self.send_response(200)
            self.send_header(CONTENT_TYPE, 'text/plain;charset=utf-8')
            # self.send_header(CONTENT_TYPE, content_type)
            self.send_header("Content-Disposition", "inline")
            self.end_headers()
            self.wfile.write(content)
        else:
            self.response_404()
            
    def do_GET(self):
        user_agent = self.headers.get("User-Agent")
        parsed = urlparse(self.path)
   

        if parsed.path == '/ip' or( self.list_dir == False and parsed.path == '/') :
            self.send_response(200)
            self.send_header(CONTENT_TYPE, 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.client_address[0].encode())

        elif parsed.path == '/pac':
            self.response_pac()
        elif parsed.path == '/proxy':
            forward_url = parsed.query
            self.proxy_url(forward_url)
        elif self.list_dir and parsed.path.endswith('/'):
            self.response_dir(parsed.path)
        else:
            self.response_file(parsed.path)

    def do_POST(self):
        self.send_response(200)
        self.send_header(CONTENT_TYPE, 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("this post")
        logger.info("this post")
        # user_agent = self.headers.get("User-Agent")
        # self.wfile.write(f"User-Agent: {user_agent}".encode())

def web_server_forever(host="",port=80):
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, RequestHandler)
    logger.info(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    port = HTTP_PORT
    web_server_forever ("", port)

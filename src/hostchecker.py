'''
Descripttion: tv-source-checker
version: 1.0
Author: 
Date: 2023-12-14 19:36:30
LastEditors: linweifu
LastEditTime: 2023-12-19 21:05:46
'''
import logging
import logging.config
from settings import *
import socket
import ipaddress

# 加载日志配置
logging.config.dictConfig(LOGGING_CONFIG)
# 获取logger实例
logger = logging.getLogger(__name__)

def resove_ipv6(host):
    pass

def is_localhost_ip(ip):
    localhost_ips = ['127.0.0.1', '::1']
    return ip in localhost_ips

def is_ipv6(ip):
    try:
        # 尝试将IP地址转换为IPv6地址对象
        ipaddress.IPv6Address(ip)
        return True
    except ipaddress.AddressValueError:
        # 如果转换失败，说明不是有效的IPv6地址
        return False

def is_localhost(host):
    ips = get_ip_addresses(host)
    if ips and len(ips)>0:
        for ip in ips:
            if is_ipv6(ip):
                print(f"{host} - {ip}")
                return is_localhost_ip(ip)
        return is_localhost_ip(ips[0])
    return False

def get_remote_ip(host):
    try:
        ip = socket.gethostbyname(host)
        return ip
    except socket.gaierror:
        return None
    
def get_host_ip(hostname):
    addresses = get_ip_addresses(hostname)
    for addr in addresses:
        if is_ipv6(addr):
            return addr
    if len(addresses)>0:
        return addresses[0]
    
def get_ip_addresses(hostname):
    try:
        addresses = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC)
        ip_addresses = [addr[4][0] for addr in addresses]
        return ip_addresses
    except socket.gaierror:
        return []



def port_check(host, port):
    try:
        # 创建套接字对象
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置超时时间为2秒
        sock.settimeout(2)
        # 尝试连接目标主机和端口
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"Port {port} is open on {host}.")
            return True
        else:
            print(f"Port {port} is closed on {host}.")
        sock.close()
    except socket.error as e:
        print(f"An error occurred while checking port {port} on {host}: {e}")
    return False


# def speed_check2(url, target_size=1*1024*1024):
#     import urllib.request
#     timeout_seconds = CHECK_TIMEOUT
#     start_time = time.time()
#     CHUNK_SIZE = 8*1024
#     headers = {
#         "User-Agent": USER_AGENT
#     }
#     request = urllib.request.Request(url, headers=headers)
#     try:
#         with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
#             if response.code == 200:
#                 total_bytes = 0
#                 response_time = time.time() - start_time

#                 while total_bytes < target_size:
#                     chunk = response.read(CHUNK_SIZE)
#                     if not chunk:
#                         break
#                     total_bytes += len(chunk)
#                     print(f"{total_bytes} < {target_size}")

#                 download_time = time.time() - start_time
#                 # download_speed = total_bytes / download_time / 1024  # 单位为 KB/s
#                 return response_time, download_time, total_bytes
#     except urllib.error.URLError as e:
#         if isinstance(e.reason, socket.timeout):
#             logger.info(f"URLError {url}请求超时")
#         else:
#             logger.error(f"{url} 请求发生错误： {str(e)}")
#     except socket.timeout:
#         logger.debug(f"{url} socket.timeout请求超时")
#     except ConnectionResetError:
#         print(f"{url} Connection reset by peer")
#     except http.client.RemoteDisconnected:
#         print(f"{url} Remote end closed connection without respons")
#     return 0, 0, 0


# def speed_check(url, temp_size=1*1024*1024):
#     import requests
#     timeout_seconds = CHECK_TIMEOUT
#     CHUNK_SIZE = 4*1024
#     # 发起 HTTP 请求并记录时间
#     headers = {
#         "User-Agent": USER_AGENT
#     }
#     start_time = time.time()
#     try:
#         with requests.get(url, stream=True, timeout=timeout_seconds, headers=headers) as response:
#             response.raise_for_status()
#             # 获取响应时间
#             end_time = time.time()
#             response_time = end_time - start_time
#             # 检查请求是否成功
#             if response.ok:
#                 logger.debug(
#                     f"Request successful. Response time: {response_time} seconds")
#             else:
#                 logger.debug(
#                     f"Request failed with status code: {response.status_code}")
#             total_bytes = 0
            # 以二进制方式逐块下载并计算总字节数
            # stream = BytesIO()
    #         downloaded_size = 0
    #         for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
    #             total_bytes += len(chunk)
    #             # stream.write(chunk)
    #             if total_bytes > temp_size:
    #                 logger.debug(f"读取到{total_bytes}字节，退出循环")
    #                 break
    #         end_time = time.time()
    #         downloaded_size = total_bytes
    #         # 获取下载时间和下载速度
    #         download_time = end_time - start_time
    #         download_speed = downloaded_size / download_time / 1024  # 以 KB/s 为单位

    #         # 检查请求是否成功
    #         if response.ok:
    #             logger.debug(
    #                 f"Download {downloaded_size} bytes completed. Time: {download_time} seconds, Speed: {download_speed} KB/s")
    #         else:
    #             logger.debug(
    #                 f"Download failed with status code: {response.status_code}")
    #         return response_time, download_time, downloaded_size
    # except requests.Timeout:
    #     logger.debug(f"Request {url} timed out.")
    # except requests.RequestException as e:
    #     logger.debug(f"An error occurred during the request {url}: {e}")
    # # 关闭响应
    # return 0, 0, 0


# def ping_check(host):
#     # 执行 ping 测试
#     COUNT = 3
#     try:
#         response_time = ping3.ping(
#             host, timeout=CHECK_TIMEOUT, unit="ms")
#         if response_time is not None:
#             print(f"Ping response time for {host}: {response_time} ms")
#             return response_time
#         # else:
#             # print(f"Failed to ping {host}")
#     except Exception as e:
#         print(f"Error occurred while pinging {host}: {str(e)}")
#     return
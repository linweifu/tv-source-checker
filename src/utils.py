'''
Descripttion: tv-source-checker
version: 1.0
Author: 
Date: 2023-12-17 18:27:53
LastEditors: linweifu
LastEditTime: 2023-12-19 21:06:07
'''
from settings import *
import logging
import logging.config
import inspect
import requests
import os
import time
# 加载日志配置
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

RESOUCE_DIR = "www/"

def print_all(my_obj):

    # 获取实例的所有方法和变量
    methods = [method_name for method_name,
               _ in inspect.getmembers(my_obj, inspect.ismethod)]
    variables = vars(my_obj)

    # 打印实例的所有方法和变量
    print("Methods:", methods)
    print("Variables:", variables)

def speed_check(url, temp_size=1*1024*1024):
    timeout_seconds = CHECK_TIMEOUT
    CHUNK_SIZE = 4*1024
    # 发起 HTTP 请求并记录时间
    headers = {
        "User-Agent": USER_AGENT
    }
    start_time = time.time()
    try:
        with requests.get(url, stream=True, timeout=timeout_seconds, headers=headers, allow_redirects=True) as response:
            response.raise_for_status()
            # 获取响应时间
            end_time = time.time()
            response_time = end_time - start_time
            # 检查请求是否成功
            if response.status_code!=200:
                logger.info(f"Request failed with status code: {response.status_code}")

            if response.ok:
                logger.debug(
                    f"Request successful. Response time: {response_time} seconds")
            else:
                logger.error(
                    f"Request failed with status code: {response.status_code}")
            total_bytes = 0
            downloaded_size = 0
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                total_bytes += len(chunk)
                if total_bytes > temp_size:
                    logger.debug(f"读取到{total_bytes}字节，退出循环")
                    break
            end_time = time.time()
            downloaded_size = total_bytes
            # 获取下载时间和下载速度
            download_time = end_time - start_time
            download_speed = downloaded_size / download_time / 1024  # 以 KB/s 为单位

            # 检查请求是否成功
            # if response.ok:
            #     logger.debug(
            #         f"Download {downloaded_size} bytes completed. Time: {download_time} seconds, Speed: {download_speed} KB/s")
            # else:
            #     logger.debug(
            #         f"Download failed with status code: {response.status_code}")
            return response_time, download_time, downloaded_size
    except requests.Timeout:
        logger.debug(f"Request {url} timed out.")
    except requests.RequestException as e:
        logger.debug(f"An error occurred during the request {url}: {e}")
    # 关闭响应
    return 0, 0, 0

def web_get(url, user_agent=None , headers={}, proxy=None):
    if user_agent==None:
        user_agent = USER_AGENT
    if isinstance(headers, dict):
        headers.update({'User-Agent': user_agent}) 
    proxies = None
    if proxy==True:
         proxies = {
            'http': PROXY_INFO,
            'https': PROXY_INFO
        }
    MAX_RETRIES = 3
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            response.raise_for_status()
            if response.status_code == 200:
                content_type = response.headers.get(CONTENT_TYPE)
                return (response.content, content_type)
            else:
                logger.error(f"Request {url} Respose code {response.status_code}")
                return None
        except requests.Timeout:
            logger.debug(f"Request {url} timed out.")
        except requests.RequestException as e:
            logger.debug(f"An error occurred during the request {url}: {e}")
        retries += 1
    return None

def web_get_clash_subscribe(url,proxy=True):
    # web_get_by_proxy(url,'Clash')
    return web_get(url, 'Clash', proxy=proxy)

def get_file_modified_time(file_path):
    try:
        # 获取文件的修改时间
        modified_time = os.path.getmtime(file_path)
        return modified_time
    except OSError:
        logger.error(f"无法获取文件 {file_path} 的修改时间")

def read_file_content(file_path):
    innerPath = os.path.join( RESOUCE_DIR, file_path)
    if os.path.isfile(innerPath):  # 检查路径是否为文件
        with open(innerPath, 'r') as file:
            content = file.read()
            return content
        
def get_content_type(file_path):
    import mimetypes
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type

def file_exists(file_path):
    innerPath = os.path.join( RESOUCE_DIR, file_path)
    if os.path.exists(innerPath) and os.path.isfile(innerPath):
        return True
    else:
        return False


def folder_exists(folder_path):
    innerPath = os.path.join( RESOUCE_DIR, folder_path)
    if os.path.exists(innerPath) and os.path.isdir(innerPath):
        return True
    else:
        return False
    
def is_subpath(path):

    innerPath = os.path.join(RESOUCE_DIR, path)
    base_path = os.path.join( os.getcwd(), RESOUCE_DIR)

    resolved_path = os.path.realpath(innerPath)
    return resolved_path.startswith(base_path)

def get_sub_path(file_name, dir_name):
    if not os.path.exists(RESOUCE_DIR):
        os.mkdir(RESOUCE_DIR)
    dir_path = os.path.join(RESOUCE_DIR, dir_name)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    return os.path.join(dir_path, file_name)

def list_dir(ref_path):
    innerPath = os.path.join( RESOUCE_DIR, ref_path)
    files = os.listdir(innerPath)
    sorted_files = sorted(files, key=lambda x: (0, x.lower()) if os.path.isdir(x) else (1, x.lower()))
    return sorted_files

if __name__ == "__main__":
    print(get_sub_path("list.m3u", "m3u"))
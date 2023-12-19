'''
Descripttion: tv-source-checker
version: 1.0
Author: 
Date: 2023-12-14 04:52:56
LastEditors: linweifu
LastEditTime: 2023-12-19 21:05:24
'''
import requests
from urllib.parse import quote
from settings import *
import logging
import logging.config
import json
from urllib.parse import urlparse, quote
import hostchecker
import classify
import utils
import time

# 加载日志配置
logging.config.dictConfig(LOGGING_CONFIG)
# 获取logger实例
logger = logging.getLogger(__file__.split("/")[-1])


def get_m3u8_tag(tag_name, m3u8_data):
    tag_start = tag_name+'="'
    start_index = m3u8_data.find(tag_start)
    if start_index != -1:
        start_index += len(tag_start)
        end_index = m3u8_data.find('"', start_index)
        tvg_value = m3u8_data[start_index:end_index]
        return tvg_value


def get_m3u_tag(line):
    # 提取 tvg-id
    tag = {}
    value = get_m3u8_tag("tvg-id", line)
    if value:
        tag["tvg_id"] = value
    value = get_m3u8_tag("tvg-name", line)
    if value:
        tag["tvg_name"] = value
    value = get_m3u8_tag("tvg-logo", line)
    if value:
        tag["tvg_logo"] = value
    value = get_m3u8_tag("group-title", line)
    if value:
        tag["group_title"] = value

    start_index = line.find(',') + 1
    tag["channel_name"] = line[start_index:]
    return tag

def parse_genre(lines):
    i = 0
    all_channels = []
    group_name = ""
    for line in lines:
        if ",#genre#" in line:
            group_name = line.split(",")[0].strip()
            if len(group_name)==0:
                logger.error(f"组名为空: {line}")
        else:
            if "," in line:
                tags = line.split(",")
                if len(tags)==2:
                    channel = {}
                    channel["group_title"] = group_name
                    channel["channel_name"] = tags[0].strip()
                    channel_url = tags[1].strip()
                    channel["url"] = channel_url
                    parsed_url = urlparse(channel_url)
                    channel["host"] = parsed_url.hostname
                    if parsed_url.hostname == "localhost" or \
                        parsed_url.hostname == "127.0.0.1" or \
                        hostchecker.is_localhost(channel["host"]):
                        logger.error(f"{channel_url} 发现服务器地址为localhost")
                        continue
                
                    if parsed_url.port == None:
                        channel["port"] = parsed_url.port
                    elif parsed_url.scheme == "http":
                        channel["port"] = 80
                    elif parsed_url.scheme == "https":
                        channel["port"] = 443
                    all_channels.append(channel)
                else:
                    logger.error(f"数据格式错误: {line}")
    return all_channels

def parse_mpeg(lines):
    i = 0
    all_channels = []
    declare = ""
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTM3U'):
            declare = line.strip()
        elif line.startswith('#EXTINF'):
            channel = get_m3u_tag(line)
            if channel:
                i += 1
                channel_url = lines[i].strip()
                parsed_url = urlparse(channel_url)
                channel["url"] = channel_url
                channel["host"] = parsed_url.hostname
                if parsed_url.port == None:
                        channel["port"] = parsed_url.port
                elif parsed_url.scheme == "http":
                    channel["port"] = 80
                elif parsed_url.scheme == "https":
                    channel["port"] = 443
                    
                ip = hostchecker.get_host_ip(channel["host"])
                if ip:
                    if hostchecker.is_localhost_ip(ip):
                        logger.error(f"{channel_url} 域名解析为: localhost")
                        continue
                    all_channels.append(channel)
                else:
                    logger.error(f"{channel_url} 域名解析失败!")
                # logger.info(channel)
        i += 1
    if len(declare) == 0:
        logger.error("播放列表格式错误，缺少头声明")
    return all_channels


def anys_url(url, proxies=None):
    # 代理设置
    proxy_dict = None
    # if proxies:
    #     proxy_dict = {
    #         'http': proxies,
    #         'https': proxies
    #     }

    # encoded_url = quote(url, safe=':/')
    # 替换成你想要下载内容的URL
    context_types = ["audio/x-mpegurl",
                     "application/json", "text/plain; charset=utf-8"]
    all_channels = {}
    try:
        response = requests.get(url, proxies=proxies, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            # 获取Content-Type
            content_type = response.headers.get('Content-Type')
            response_text = response.text
            logger.info(f"fetch url {url} finish!")
            lines = response_text.splitlines()
            if content_type == context_types[0] or content_type == context_types[2]:

                all_channels = parse_mpeg(lines)
            elif content_type == context_types[1]:
                # return all_channels, source_count
                lines = []
                for line in response_text.splitlines():
                    if not line.strip().startswith('//'):
                        lines.append(line)
                # 连接过滤后的行
                json_text_without_comments = '\n'.join(lines)
                with open('channles.json', 'w') as file:
                    file.write(json_text_without_comments)

                # response_text = html.unescape(response_text)
                # all_channels, source_count = parse_json(json_text_without_comments)
            else:
                logger.info(f"{url}未分析的类型{content_type}")

            logger.info(f"in url:{url} find {len(all_channels)} sources")
            return all_channels
        else:
            logger.error(
                f"Request failed with status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"An error occurred during the request: {e}")
        return None

def analysis_subscription(url):
    
    all_channels = []
    context_types = ["audio/x-mpegurl",
                     "text/plain; charset=utf-8"]
    
    response = utils.web_get(url, proxy=True)
    if response:
        response_text = response[0].decode('utf-8')
        content_type = response[1]
        logger.info(f"fetch url {url} finish!")
        lines = response_text.splitlines()

        logger.debug(f"{url}分析的类型{content_type}, {len(lines)} lines")
        if content_type == context_types[0]:
            all_channels = parse_mpeg(lines)
        elif content_type == context_types[1]:
            if lines[0].startswith("#EXTM3U"):
                all_channels = parse_mpeg(lines)
                
            elif "#genre#" in lines[0]:
                all_channels = parse_genre(lines)
        else:
            logger.warn(f"{url}未分析的类型{content_type}")
        logger.info(f"find {len(all_channels)} channels in {url}.")
        return all_channels
    return all_channels


# def anys_url2(url, proxies=None):
#     import urllib.request
#     # 代理设置
#     if proxies:
#         proxy_handler = urllib.request.ProxyHandler(proxies)
#         # 构建 Opener
#         opener = urllib.request.build_opener(proxy_handler)
#     else:
#         opener = urllib.request.build_opener(proxy_handler)
#     encoded_url = quote(url, safe=':/')
#     # 替换成你想要下载内容的URL
#     context_types = ["audio/x-mpegurl",
#                      "application/json", "text/plain; charset=utf-8"]
#     # 下载URL内容
#     all_channels = {}
#     headers = {
#         "User-Agent": USER_AGENT
#     }
#     request = urllib.request.Request(url, headers=headers)
#     with opener.open(request) as response:
#         if response.code == 200:
#             # 获取Content-Type
#             content_type = response.getheader('Content-Type')
#             response_text = response.read().decode('utf-8')
#             logger.info(f"fetch url {url} finish!")
#             if content_type == context_types[0] or content_type == context_types[2]:
#                 all_channels = parse_mpeg(response_text)
#             elif content_type == context_types[1]:
#                 # return all_channels, source_count
#                 lines = []
#                 for line in response_text.splitlines():
#                     if not line.strip().startswith('//'):
#                         lines.append(line)
#                 # 连接过滤后的行
#                 json_text_without_comments = '\n'.join(lines)
#                 with open('channles.json', 'w') as file:
#                     file.write(json_text_without_comments)

#                 # response_text = html.unescape(response_text)
#                 # all_channels, source_count = parse_json(json_text_without_comments)
#             else:
#             logger.info(f"in url:{url} find {len(all_channels)} sources")
#             return all_channels

#             # logger.info(f"Content-Type: {content_type}")
#         else:
#             logger.error(f"{url} response error.code[{response.code}]")
def check_source(channel):
    chunk_size = STREAM_CHUNK
    response_time, download_time, total_bytes = utils.speed_check(
            channel['url'], chunk_size)
    return (response_time,download_time,total_bytes)
        

def check_all_source(all_channels):
    ok_channels = []
    slow_channels = []
    failed_channels = []

    chunk_size = STREAM_CHUNK
    cnt = len(all_channels)
    start_time = time.time()
    for ch in all_channels:
        response_time, download_time, total_bytes = utils.speed_check(
            ch['url'], chunk_size)
        if response_time != 0:
            slow_channels.append(ch)
            logger.debug(
                f"slow {ch['url']} channel {ch['channel_name']} 响应: {response_time:.2f}秒,下载: {total_bytes}字节,耗时: {download_time:.2f}秒")

            if chunk_size <= total_bytes:
                ok_channels.append(ch)
                logger.debug(
                    f"ok channel {ch['channel_name']} {response_time:.2f}秒,下载{total_bytes}字节,耗时：{download_time:.2f}秒")
        else:
            failed_channels.append(ch)

    test_time = time.time()-start_time
    logger.info(f"频道总数：{cnt}"
                f"\nok:{len(ok_channels)} "
                f"\nslow:{len(slow_channels)} "
                f"\nfail:{len(failed_channels)} "
                f"\n耗时:{test_time}秒")
    return ok_channels, slow_channels


if __name__ == "__main__":
    # 打印内容

    channels = analysis_subscription(SUBSCRIP_LIST[0])
    json_text = json.dumps(channels, indent=4, ensure_ascii=False)
    with open('channles.txt', 'w') as file:
        file.write(json_text)
    if channels:
        ok, slow = check_all_source(channels)
        classify.generate_m3u("ok_all", ok)
        classify.generate_m3u("slow_all", slow)
        slow1 = classify.filter_chnannel(slow)
        classify.classify_source(slow1)

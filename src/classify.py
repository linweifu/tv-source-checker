'''
Descripttion: tv-source-checker
version: 1.0
Author: 
Date: 2023-12-15 04:21:14
LastEditors: linweifu
LastEditTime: 2023-12-19 21:05:39
'''
from settings import LOGGING_CONFIG
import logging
import logging.config
import utils
# 加载日志配置
logging.config.dictConfig(LOGGING_CONFIG)
# 获取logger实例
logger = logging.getLogger(__name__)


def generate_m3u8_item(channel):
    line_str = "#EXTINF:-1"
    if channel.get("tvg_id"):
        line_str += f' tvg-id="{channel["tvg_id"]}"'
    if channel.get("tvg_name"):
        line_str += f' tvg-name="{channel["tvg_name"]}" '
    if channel.get("tvg_logo"):
        line_str += f' tvg-logo="{channel["tvg_logo"]}" '
    if channel.get("group_title"):
        line_str += f' group-title="{channel["group_title"]}" '
    # if channel.get("channel_name"):
    line_str += f',{channel["channel_name"]}\n'
    line_str += channel["url"]+"\n"
    return line_str

def generate_m3u(list_name, all_channel):
    file_name = utils.get_sub_path(f"{list_name}.m3u", "m3u")
    with open(file_name, "w") as f:
        declare = "#EXTM3U\n"
        f.write(declare)
        for ch in all_channel:
            # if isinstance(ch, dict):
            f.write(generate_m3u8_item(ch))
            # else:
            #     # logger.info(f"ch type  mismatch {type(ch)}")
            #     print(ch)

def generate_tvbox(list_name, all_channel):
    file_name = utils.get_sub_path(f"{list_name}.txt", "tvbox")
    with open(file_name, "w") as f:
        group = ""
        for ch in all_channel:
            # if isinstance(ch,dict):
            if ch['group_title'] != group :
                group = ch['group_title']
                f.write(f"{group},#genre#\n")
            f.write(f"{ch['channel_name']},{ch['url']}\n")


def check_key_in_channels(all_channel, keyword):
    i = 0
    for channel in all_channel:
        if channel.get("group_title"):
            if keyword in channel["group_title"]:
                return i
        if channel.get("channel_name"):
            if keyword in channel["channel_name"]:
                return i
        i += 1
    return None


def filter_chnannel(all_channel):
    key_ignore = ["购物"]
    new_list = []
    for channel in all_channel:
        ignore = False
        for keyword in key_ignore:
            if channel.get("group_title"):
                if keyword in channel["group_title"]:
                    ignore = True
                    break
            if channel.get("channel_name"):
                if keyword in channel["channel_name"]:
                    ignore = True
                    break
        if ignore:
            continue
        new_list.append(channel)
    return new_list


def classify_source(all_channel):
    classify_define = [
        {
            "list_name": "zhejiang",
            "keywords": ["浙江"],
            "channels": []
        },
        {
            "list_name": "shanghai",
            "keywords": ["上海"],
            "channels": []
        },
        {
            "list_name": "child",
            "keywords": ["少儿", "科教", "文化"],
            "channels": []
        },
        {
            "list_name": "weishi",
            "keywords": ["卫视"],
            "channels": []
        }
    ]
    for channel in all_channel:
        for ch_list in classify_define:
            for keyword in ch_list["keywords"]:
                if channel.get("group_title"):
                    if keyword in channel["group_title"]:
                        ch_list["channels"].append(channel)
                        break
                if channel.get("channel_name"):
                    if keyword in channel["channel_name"]:
                        ch_list["channels"].append(channel)
                        break

    for ch_list in classify_define:
        if len(ch_list["channels"])>0:
            generate_m3u(ch_list['list_name'], ch_list["channels"])
            generate_tvbox(ch_list['list_name'], ch_list["channels"])
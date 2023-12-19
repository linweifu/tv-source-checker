'''
Descripttion: tv-source-checker
version: 1.0
Author: 
Date: 2023-12-15 04:08:11
LastEditors: linweifu
LastEditTime: 2023-12-20 06:00:03
'''

from os import environ as env


PROXY_INFO = env.get("PROXY_INFO", "http://localhost:7890")  # 使用该代理，仅下载订阅源数据
SUBSCRIP_LIST = [
    'https://raw.githubusercontent.com/YanG-1989/m3u/main/Gather.m3u',
    'https://iptv-org.github.io/iptv/index.m3u',
]


MAX_THREADS_NUM = env.get("MAX_THREADS_NUM", 5)
HTTP_PORT       = env.get("HTTP_PORT", 8085)
REQUEST_TIMEOUT = env.get("REQUEST_TIMEOUT", 15)      # 请求响应时间小于高于15秒则忽略
CHECK_TIMEOUT   = env.get("CHECK_TIMEOUT", 1)         # 检查源请求时间超过2秒则忽略
RESPONSE_LIMIT  = env.get("RESPONSE_LIMIT", 1)        # 源响应时间超过1秒的不要
STREAM_CHUNK    = env.get("STREAM_CHUNK", 512*1024)   # 用于测试的下载的流大小
USER_AGENT      = env.get("HTTP_PORT",
                          "Mozilla/5.0 (Linux; Android 7.1.2; TV BOX Build/NHG47L) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
                        )
CONTENT_TYPE = 'Content-type'
# 日志配置字典
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'myapp.log',
            'formatter': 'standard'
        }
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

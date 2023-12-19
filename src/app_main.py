'''
Descripttion: tv-source-checker
version: 1.0
Author: 
Date: 2023-12-17 18:49:18
LastEditors: linweifu
LastEditTime: 2023-12-19 21:04:30
'''
import logging
import logging.config
import schedule
import time
import downloader
import web
import classify
import threading
from settings import *
import json

import concurrent.futures


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__file__.split("/")[-1])

def my_task():
    def sort_by_group(item):
        group = item["group_title"]
        if group is None:
            group = "未分组"  # 设置默认值为0
        return group
    # 执行你的定时任务逻辑
    logger.info(f"开始抓取列表共{len(SUBSCRIP_LIST)}个")
    results = []
    num_threads = 5
    # 抓取频道
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for subscript in SUBSCRIP_LIST:
            future =  executor.submit(downloader.analysis_subscription, subscript)
            futures.append(future)
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            result = future.result()
            if len(result) == 0:
                logger.error(f'抓取{SUBSCRIP_LIST[i]}地址失败！') 
            results.extend(result)
    # 分组排序
    channels_raw = sorted(results, key=sort_by_group)
    logger.info(f"共识别到 {len(channels_raw)}个频道")
     # 过滤 购物频道等
    channels = classify.filter_chnannel(channels_raw)
    logger.info(f"过滤后还剩 {len(channels)}个频道，开始检测访问测试...")
    # print(channels[0])
    # return 
    ok_channels = []
    slow_channels = []
    fail_channels = []
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for channel in channels :
            futures.append( executor.submit(downloader.check_source, channel))
            # slow1 = classify.filter_chnannel(slow)
            # classify.classify_source(slow1)

        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            result = future.result()
            ch = channels[i]
            response_time, download_time, total_bytes = result
            if response_time != 0:
                # if not isinstance(ch,dict):
                #     print(ch)
                #     return
                slow_channels.append(ch)
                logger.debug(
                    f"slow {ch['url']} channel {ch['channel_name']} 响应: {response_time:.2f}秒,下载: {total_bytes}字节,耗时: {download_time:.2f}秒")

                if total_bytes >= STREAM_CHUNK:
                    ok_channels.append(ch)
                    logger.debug(
                        f"ok channel {ch['channel_name']} {response_time:.2f}秒,下载{total_bytes}字节,耗时：{download_time:.2f}秒")
            else:
                fail_channels.append(ch)
    elapsed_time = time.time()-start_time
    logger.info(f"\nok:{len(ok_channels)} "
                f"\nslow:{len(slow_channels)} "
                f"\nfail:{len(fail_channels)} "
                f"\n耗时:{elapsed_time}秒")
    classify.generate_m3u("slow_channels", slow_channels)
    classify.generate_m3u("ok_channels", fail_channels)
    classify.generate_m3u("fail_channels", ok_channels)

    classify.generate_tvbox("slow_channels", slow_channels)
    classify.generate_tvbox("ok_channels", fail_channels)
    classify.generate_tvbox("fail_channels", ok_channels)
    # 类型过滤
    classify.classify_source(slow_channels)
    

# 使用 schedule 模块来调度任务
    
def run_web_thread():
    thread = threading.Thread(target=web.web_server_forever, args=("",80,))
    thread.daemon = True  # 设置线程为守护线程，使得主线程退出时自动退出子线程
    thread.start()
        
if __name__ == "__main__":
    # 运行web 线程
    run_web_thread()
    schedule.every().day.at("23:00").do(my_task)
    my_task() 
    # 进入任务循环
    while True:
        schedule.run_pending()
        time.sleep(1)
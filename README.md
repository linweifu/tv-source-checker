<!--
 * @Descripttion: your project
 * @version: 1.0
 * @Author: 
 * @Date: 2023-12-19 20:57:52
 * @LastEditors: linweifu
 * @LastEditTime: 2023-12-20 05:57:47
-->
# TV Source Checker
IPTV源检测（m3u、m3u8、tvbox），过滤，分类，订阅。
ipv6、电视源测速、speedtest


## 功能
1. 电视源抓取, 根据提供的列表, 多线程同时获取电视源列表信息, 使用http proxy
2. 电视列表分析, 支持m3u格式, 和tvbox格式
3. 电视源分类, 根据配置的关键字分类, 按分类导出单独的列表
4. 电视源过滤, 按关键字过滤, 例如, 广播, 购物等
5. 域名解析过滤，无法解析的域名过滤，解析结果为localhost的过滤
6. 电视源检测, 基于线程池, 使用requests库的get方法, 打开流媒体链接, 超时的不要, 打不开的也不要。留下能打开的, 导出和分类导出
7. 电视源导出, 将多远合并, 过滤, 并导出成m3u格式和tvbox格式
8. Web访问, 使用httdserver,将导出的目录, 通过http协议展示

## 运行
1. 修改`src/settings.py`、根据实际情况修改原地址列表，web端口，web代理，最大线程数
2. 安装python依赖`pip install src/requirements.txt`
3. 运行服务`python src/app_main.py`

## Docker
使用Docker-Compose编排容器。
1. 编译命令.`docker-compose build`
2. 运行命令.`docker-compose up -d`
3. 相关参数通过environment配置修改

## 注意：
1. 容器Ipv6
2. tv源列表格式，目前就搜到两种各种，所以支持可能有限，有新的源可以在issue里提

## 问题待解决：
工具编写初衷想用来测试一下流媒体视频源的速度。  
结果发现很多流媒体链接，无法完成读取指定大小，但是有些链接可以正常播放，不卡顿。  
倒腾了许久，未能解决这个测速问题，顾分享源码，往有高人指点一下。  
测速函数：`utils.speed_check`  

## Todo
1. IPV6检测，IPV6优先
2. 重定向过滤，可能会让下载测试效率提升
<!--
 * @Descripttion: your project
 * @version: 1.0
 * @Author: 
 * @Date: 2023-12-19 20:57:52
 * @LastEditors: linweifu
 * @LastEditTime: 2023-12-19 21:01:40
-->
# TV Source Checker
IPTV源检测，过滤，分类，订阅.


## 功能
1. 电视源抓取, 根据提供的列表, 多线程同时获取电视源列表信息, 使用http proxy
2. 电视列表分析, 支持m3u格式, 和tvbox格式
3. 电视源分类, 根据配置的关键字分类, 按分类导出单独的列表
4. 电视源过滤, 按关键字过滤, 例如, 广播, 购物等
5. 域名解析过滤，无法解析的域名过滤，解析结果为localhost的过滤
6. 电视源检测, 基于线程池, 使用requests库的get方法, 打开流媒体链接, 超时的不要, 打不开的也不要。留下能打开的, 导出和分类导出
7. 电视源导出, 将多远合并, 过滤, 并导出成m3u格式和tvbox格式
8. Web访问, 使用httdserver,将导出的目录, 通过http协议展示
## Todo
1. IPV6检测，IPV6优先
2. 重定向过滤，可能会让下载测试效率提升

## Docker

## Docker-Compose

## 

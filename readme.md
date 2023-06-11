# 关于项目
本项目***暂时***是一个免费开源的项目，不收取任何费用，若发现他人非法侵权
<br>
项目作者：drank
# 使用方法
### 配置数据库
1. 访问路径/config/database
2. 创建三个文件
<br>(1)center-sql.ini
<br>(2)user-sql.ini
<br>(3)ddos.ini
3. 分别向这三个文件中写入如下数据：
```
[database]
host = yourhost
port = yourport
user = youruser
password = yourpassword
database = center-sql
charset = utf8
```
### 启动主程序
1. 运行start.bat
### API调用
- 本机调试：127.0.0.1:5000/你要调用的API
- 远程调试：你的服务器IP:5000/你要调试的API
# API列表
正在开发
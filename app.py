from flask import Flask, request
import pymysql
import requests
import os
import secrets
import string
import configparser

app = Flask(__name__)

# 全局变量区
# 当前APP版本
app_version = "1.0.0"
# 用户模式：0为从配置文件获取，1为普通用户，2为管理员，3为禁用，默认禁用（3）
app_admin = 3
#压测调试开关：0为禁止，1为开启，日常关闭（0），默认关闭，防止被他人压测
app_ddos = 0

#参数读取区
#数据库文件读取
#center-sql数据库配置文件读取
current_path = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_path, 'config', 'database', 'center-sql.ini')
config = configparser.ConfigParser()
config.read(config_file_path)
db_config = config['database']
center_host = db_config['host']
center_port = int(db_config['port'])
center_user = db_config['user']
center_password = db_config['password']
center_database = db_config['database']
center_charset = db_config['charset']
#user-sql数据库配置文件读取
current_path = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_path, 'config', 'database', 'user-sql.ini')
config = configparser.ConfigParser()
config.read(config_file_path)
db_config = config['database']
user_host = db_config['host']
user_port = int(db_config['port'])
user_user = db_config['user']
user_password = db_config['password']
user_database = db_config['database']
user_charset = db_config['charset']
#压测数据库配置文件读取
current_path = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_path, 'config', 'database', 'user-sql.ini')
config = configparser.ConfigParser()
config.read(config_file_path)
db_config = config['database']
ddos_host = db_config['host']
ddos_port = int(db_config['port'])
ddos_user = db_config['user']
ddos_password = db_config['password']
ddos_database = db_config['database']
ddos_charset = db_config['charset']
#IP地址获取源读取
current_path = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_path, 'config', 'app', 'get-ip.ini')
config = configparser.ConfigParser()
config.read(config_file_path)
get_ip = config['get-ip']
get_ip_address = get_ip['address']


@app.route('/')
def sysrun():  # put application's code here
    return 'System running!'


@app.route('/gdn')
def gdn():
    return 'Global Database Network is online!'


@app.route('/update')
def update():
    db = pymysql.connect(
        host=center_host,
        port=center_port,
        user=center_user,
        password=center_password,
        database=center_database,
        charset=center_charset
    )
    cursor = db.cursor()
    cursor.execute("SELECT value FROM app_config WHERE `key` = 'app_version';")
    result = cursor.fetchone()
    version = result[0] if result else None
    global app_version
    if version == app_version:
        return '当前是最新版本了，无需更新！'
    else:
        cursor.execute("SELECT value FROM app_config WHERE `key` = 'app_download';")
        result = cursor.fetchone()
        url = result[0]
        resource = requests.get(url)
        if resource.status_code == 200:
            with open(os.getcwd(), "wb") as file:
                file.write(resource.content)
                return '更新完成！'
        else:
            return '更新失败！'


@app.route('/admin')
def admin():
    token = request.args.get('token')
    print(token)
    if token == None or token == "":
        return '参数错误'
    else:
        db = pymysql.connect(
            host=center_host,
            port=center_port,
            user=center_user,
            password=center_password,
            database=center_database,
            charset=center_charset
        )
        cursor = db.cursor()
        cursor.execute("SELECT `value` FROM admin_token WHERE `token` = '" + token + "';")
        result = cursor.fetchone()
        key = result[0]
        global app_admin
        if key == "ok" and app_admin != 3:
            app_admin = 2
            global get_ip_address
            url = requests.get(get_ip_address)
            ip = url.text.strip()
            sql = "UPDATE admin_token SET `value` = 'used', `use_ip` = '" + ip + "' WHERE `token` = '" + token + "';"
            cursor.execute(sql)
            db.commit()
            return '已将权限设置为admin！'
        elif key == "used":
            return '密钥已被使用！'
        elif app_admin == 3:
            return 'admin模式已被关闭，请向管理员确认是否已经将app.py文件中的app_admin变量设置为除3外的数字'
        else:
            return '未知错误，请联系管理员！'


@app.route('/admin_update')
def admin_update():
    global app_admin
    if app_admin == 2:
        version = request.args.get('version')
        download = request.args.get('download')
        if version == None or download == None:
            return '参数错误'
        else:
            db = pymysql.connect(
                host=center_host,
                port=center_port,
                user=center_user,
                password=center_password,
                database=center_database,
                charset=center_charset
            )
            cursor = db.cursor()
            sql = "UPDATE app_config SET `value` = '" + version + "' WHERE `key` = 'app_version'"
            cursor.execute(sql)
            sql = "UPDATE app_config SET `value` = '" + download + "' WHERE `key` = 'app_download'"
            cursor.execute(sql)
            db.commit()
        return '内容更新成功！'
    else:
        return '权限状态异常！'


@app.route('/add_token_beat')
def add_token_beat():
    db = pymysql.connect(
        host=ddos_host,
        port=ddos_port,
        user=ddos_user,
        password=ddos_password,
        database=ddos_database,
        charset=ddos_charset
    )
    num = request.args.get('num')
    tokens = []
    for _ in range(int(num)):
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(30))
        tokens.append(token)
    cursor = db.cursor()
    for token in tokens:
        sql = "INSERT INTO admin_token (token) VALUES (%s)"
        cursor.execute(sql, (token,))
        db.commit()
    return '阻断符'.join(tokens)


@app.route('/add_token')
def add_token():
    db = pymysql.connect(
        host=center_host,
        port=center_port,
        user=center_user,
        password=center_password,
        database=center_database,
        charset=center_charset
    )
    num = request.args.get('num')
    tokens = []
    for _ in range(int(num)):
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(30))
        tokens.append(token)
    cursor = db.cursor()
    for token in tokens:
        sql = "INSERT INTO admin_token (token) VALUES (%s)"
        cursor.execute(sql, (token,))
        db.commit()
    return '阻断符'.join(tokens)


@app.route('/reg')
def reg():
    user = request.args.get('user')
    password = request.args.get('passwd')
    db = pymysql.connect(
        host=user_host,
        port=user_port,
        user=user_user,
        password=user_password,
        database=user_database,
        charset=user_charset
    )


if __name__ == '__main__':
    app.run()

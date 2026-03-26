"""
数据库配置文件
"""
from peewee import MySQLDatabase
from playhouse.db_url import connect
import os

# 从环境变量或配置中获取数据库连接信息
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'xiaohui_ai'),
}

# 创建数据库连接
db = MySQLDatabase(
    DB_CONFIG['database'],
    host=DB_CONFIG['host'],
    port=DB_CONFIG['port'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password'],
    charset='utf8mb4',
    autocommit=True,
)

def connect_db():
    """连接数据库"""
    if db.is_closed():
        db.connect()

def close_db():
    """关闭数据库连接"""
    if not db.is_closed():
        db.close()

def init_tables():
    """初始化表结构"""
    from db.models import DeviceHealthReport
    db.create_tables([DeviceHealthReport], safe=True)

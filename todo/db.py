import sqlite3
from datetime import datetime, date

import click

from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # 指定连接像字典一样返回的行数据，可以通过字段名获取字段值
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """数据库初始化操作，清除现有数据，并创建表格"""
    db = get_db()

    with current_app.open_resource('schema.sql', mode='rb') as f:
        db.executescript(f.read().decode('utf-8'))


@click.command('init-db')
def init_db_command():
    """数据库初始化命令"""
    init_db()
    click.echo('数据库初始化已完成。')


# 自定义适配器和转换器
def adapt_datetime(val):
    return val.isoformat()

def adapt_date(val):
    return val.isoformat()

def convert_datetime(val):
    return datetime.fromisoformat(val.decode())

def convert_date(val):
    return date.fromisoformat(val.decode())

# 注册适配器和转换器
sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_adapter(date, adapt_date)
sqlite3.register_converter("TIMESTAMP", convert_datetime)
sqlite3.register_converter("DATE", convert_date)

def init_app(app):
    """用于将数据库相关操作注册到应用上"""
    # 请求处理完毕，响应返回之前关闭数据库连接
    app.teardown_appcontext(close_db)
    # 注册执行数据库初始化操作的命令行命令
    app.cli.add_command(init_db_command)

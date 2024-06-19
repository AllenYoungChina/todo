import os

from flask import Flask


def create_app(test_config=None):
    """工厂函数"""
    # 创建并配置应用
    # instance_relative_config=True方便后续从instance目录读取配置文件
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'todo.sqlite'),
    )

    if test_config is None:
        # 从instance目录加载配置文件
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 加载测试配置test_config
        app.config.from_mapping(test_config)

    # 确保实例instance目录存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 测试路由
    @app.route('/hello')
    def hello_world():
        return 'Hello, World!'

    # 注册数据库相关操作
    from . import db
    db.init_app(app)

    # 注册认证相关蓝图
    from . import auth
    app.register_blueprint(auth.bp)

    # 注册待办相关蓝图

    return app

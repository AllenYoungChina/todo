import sqlite3

import pytest
from todo.db import get_db


def test_get_close_db(app):
    """测试数据库连接与关闭"""
    with app.app_context():
        db = get_db()
        # 在同一个应用上下文中，每次获取的数据库连接相同
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_init_db_command(runner, monkeypatch):
    """测试数据库初始化命令被执行"""
    class Recorder:
        called = False

    def fake_init_db():
        """伪造的init_db函数，只测试命令行调用自定义命令init-db时，init_db函数会被调用"""
        # 记录该函数被调用
        Recorder.called = True

    # 使用pytest的猴子补丁，在运行时替换掉应用的init_db函数
    monkeypatch.setattr('todo.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert '数据库初始化已完成。' in result.output
    assert Recorder.called

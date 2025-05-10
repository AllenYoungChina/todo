import datetime

import pytest
from flask import g

from todo.db import get_db


@pytest.mark.parametrize('path', (
    '/',
    '/create',
    '/update/1',
    '/delete/1'
))
def test_login_required(path, client):
    """测试登录校验"""
    # GET测试，待办事项删除接口不支持GET请求
    if path != '/delete/1':
        response = client.get(path)
        assert response.headers['Location'] == '/auth/login'

    # POST测试，主页（根路径）访问不支持POST
    if path != '/':
        response = client.post(path)
        assert response.headers['Location'] == '/auth/login'


def test_author_required(app, client, auth):
    """测试待办所有者校验"""
    with app.app_context():
        db = get_db()
        db.execute('UPDATE todo SET user_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # 当前用户无法修改或删除其他用户创建的待办事项
    assert client.post('/update/1').status_code == 403
    assert client.post('/delete/1').status_code == 403
    # 当前用户无法在主页无法对其他用户创建的待办进行操作
    assert b'/update/1' not in client.get('/').data
    assert b'/delete/1' not in client.get('/').data


def test_index(app, client, auth):
    """测试待办首页"""
    # 用户未登录时会跳转到登录页面
    response = client.get('/')
    assert response.headers['Location'] == '/auth/login'

    # 用户登录后可以看到用户名和登出按钮
    auth.login()
    data = client.get('/').get_data(as_text=True)
    assert 'test' in data
    assert '退出' in data

    # 用户可正常查看今日待办
    assert 'today' in data
    # 用户可以看到待办事项的操作按钮
    assert '/update/1' in data
    assert '/delete/1' in data

    # 用户仅能查看今日待办和昨日待办
    assert 'tomorrow' not in data

    with app.app_context():
        db = get_db()
        db.execute('UPDATE todo SET user_id = 2 WHERE id = 1')
        db.commit()

    data = client.get('/').get_data(as_text=True)
    # 用户无法查看其他用户创建的待办事项
    assert 'today' not in data


@pytest.mark.parametrize('path', (
    '/update/5',
    '/delete/5'
))
def test_exists_required(client, auth, path):
    """测试待办事项存在性校验"""
    auth.login()
    assert client.post(path).status_code == 404


def test_create(app, auth, client):
    """测试新增待办事项"""
    auth.login()
    assert client.get('/create').status_code == 200

    client.post('/create', data=dict(content='created', finished=0))
    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM todo').fetchone()[0]
        assert count == 5
        todo_create = db.execute(
            'SELECT * FROM todo WHERE id = ?', (4,)
        ).fetchone()
        assert todo_create['user_id'] == 1


def test_update(app, auth, client):
    """测试修改待办事项"""
    auth.login()
    assert client.get('/update/1').status_code == 200

    client.post('/update/1', data=dict(content='updated', finished=1))
    with app.app_context():
        todo = get_db().execute('SELECT * FROM todo WHERE id = 1').fetchone()
        assert todo['content'] == 'updated'
        assert todo['finished'] == 1


@pytest.mark.parametrize('path', (
    '/create',
    '/update/1'
))
def test_create_update_validate(auth, client, path):
    """测试创建或修改待办事项时的输入验证"""
    auth.login()
    data = client.post(path, data=dict(content='', finished=0)).get_data(as_text=True)
    assert '请输入待办事项' in data
    content = '12345678' * 4 + '0'
    data = client.post(path, data=dict(content=content, finished=0)).get_data(as_text=True)
    assert '待办事项最多输入32个字符' in data


def test_delete(app, auth, client):
    """测试删除待办事项"""
    auth.login()
    response = client.post('/delete/1')
    assert response.headers['Location'] == '/'

    with app.app_context():
        todo = get_db().execute('SELECT * FROM todo WHERE id = 1').fetchone()
        assert todo is None


def test_add(app, auth, client):
    """测试添加历史待办事项到今日待办"""
    auth.login()
    response = client.post('/add/2')
    assert response.headers['Location'] == '/'
    with app.app_context():
        todo_add = get_db().execute(
            'SELECT * FROM todo WHERE id = ?', (5,)
        ).fetchone()
        assert todo_add['content'] == 'yesterday'
        assert todo_add['created'].date() == datetime.date.today()

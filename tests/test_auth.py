import pytest
from flask import session, g

from todo.db import get_db


def test_register(client, app):
    """测试用户注册功能"""
    response = client.get('/auth/register')
    assert response.status_code == 200
    response = client.post('/auth/register', data=dict(username='hello', password='123456'))
    assert response.headers['Location'] == '/auth/login'

    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM user WHERE username = "hello"'
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '123456', '请输入用户名'),
    ('12', '123456', '用户名应为3-10个字符'),
    ('12345678901', '123456', '用户名应为3-10个字符'),
    ('hello', '', '请输入密码'),
    ('hello', '12345', '密码应为6-18个字符'),
    ('hello', '1234567890123456789', '密码应为6-18个字符'),
    ('test', '123456', '已被注册'),
))
def test_register_validate_input(client, username, password, message):
    """测试用户注册功能的参数校验"""
    response = client.post('/auth/register', data=dict(username=username, password=password))
    assert message in response.get_data(as_text=True)


def test_login(client, auth):
    """测试用户登录功能"""
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == '/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('hell_', '123456', '用户名或密码错误'),
    ('hello', '1234567', '用户名或密码错误')
))
def login_validate_input(auth, username, password, message):
    """测试登录功能"""
    response = auth.login(username=username, password=password)
    assert message in response.get_data(as_text=True)


def test_logout(client, auth):
    """测试用户登出"""
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session

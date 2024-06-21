from todo import create_app


def test_config():
    """测试工厂函数支持传入测试配置"""
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_hello(client):
    """测试工厂函数创建的应用可以通过路由正常访问"""
    response = client.get('/hello')
    assert response.status_code == 200
    assert response.data == b'Hello, World!'

# 我的待办
## 简介
基于Flask编写的待办应用。
## 功能介绍
### 用户
包含用户注册和登录功能。
### 待办
包含新增、修改和删除待办事项功能。
仅登录用户可查看待办事项列表，且只能查看自己创建的待办事项。
## 测试
使用`pytest`和`coverage`进行测试。
``` bash
# 安装依赖
pip install pytest coverage

# 运行测试
pytest

# 查看测试覆盖率
coverage run -m pytest

# 生成html格式的测试覆盖率报告
coverage html
```
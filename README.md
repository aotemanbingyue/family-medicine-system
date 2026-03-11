# 家庭药品管理与分享系统（毕业设计）

基于 Django 5.2 的家庭药品管理、分享与用药提醒系统。

## 技术栈

- Python 3 + Django 5.2
- MySQL / SQLite（可选，见 `数据库切换说明.md`）
- PyMySQL

## 快速开始

```bash
pip install -r requirements.txt
# 配置数据库后执行：
python manage.py migrate
python manage.py runserver
```

详见 **新手入门指南.md**、**Django服务说明.md**。

## 说明文档

- `新手入门指南.md` - 开发与运行说明
- `数据库切换说明.md` - MySQL / SQLite 切换
- `测试账号说明.md` - 测试账号与权限
- `角色与权限设计说明.md` - 角色与权限设计

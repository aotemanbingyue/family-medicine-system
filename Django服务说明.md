# Django 服务开启与关闭说明

## 使用前请先启动 MySQL

项目使用 **MySQL** 作为数据库。请先：
1. 启动 MySQL 服务（如 `services.msc` 中启动 MySQL）
2. 创建数据库：`CREATE DATABASE bysj CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
3. 若 root 密码不是 123456，运行前设置：`$env:DJANGO_DB_PASSWORD="你的密码"`

## 需要每次手动启动吗？

**是的。** 使用 `python manage.py runserver` 启动的是 Django 开发服务器，它：

- 在前台运行，**关闭终端或按 `Ctrl+C` 后就会停止**
- 每次要访问网页时，需要**重新启动一次**

## 如何开启 Django 服务

1. 打开终端（PowerShell 或 CMD）
2. 进入项目目录：
   ```powershell
   cd d:\SoftWare\Code\bysj
   ```
3. 执行：
   ```powershell
   python manage.py runserver
   ```
4. 看到类似输出表示启动成功：
   ```
   Starting development server at http://127.0.0.1:8000/
   ```
5. 在浏览器访问：**http://127.0.0.1:8000/**

## 如何关闭 Django 服务

在运行 `runserver` 的终端窗口中，按 **`Ctrl+C`** 即可停止服务。

## 想「一直开着」怎么办？

- **开发阶段**：每次用之前执行一次 `runserver` 即可
- **正式部署**：会使用 gunicorn、uwsgi 等 WSGI 服务器配合 nginx，部署到服务器上 24 小时运行，不需要每次手动启动

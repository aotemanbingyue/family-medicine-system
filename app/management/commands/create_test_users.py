"""
创建多个测试账号，方便用不同角色登录体验。
用法：python manage.py create_test_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


# 格式：(用户名, 密码, 角色)
# 说明：
# 1) 按开题报告对齐为「四类管理员 + 普通用户」：
#    - 用户管理员：admin_user
#    - 药品管理员：admin_med
#    - 帖子管理员：admin_post
#    - 系统管理员：admin_sys
# 2) 管理员账号均赋予 Django 后台权限（is_staff=True, is_superuser=True），
#    便于在 /admin/ 进行演示与数据维护。
TEST_USERS = [
    ("sys_admin", "123456", "admin_sys"),    # 系统管理员（主账号）
    ("user_admin", "123456", "admin_user"),  # 用户管理员
    ("med_admin", "123456", "admin_med"),    # 药品管理员
    ("post_admin", "123456", "admin_post"),  # 帖子管理员
    ("user1", "123456", "user"),             # 普通家庭用户（仅前台，不可进后台）
]


class Command(BaseCommand):
    help = "创建多个测试账号（不同角色），便于登录体验"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="已存在的用户也重置密码为上面设定的密码",
        )

    def handle(self, *args, **options):
        force = options["force"]
        for username, password, role in TEST_USERS:
            is_super = role != "user"  # 除普通家庭用户外，均为超级管理员（可进后台）
            try:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "role": role,
                        "is_staff": is_super,
                        "is_superuser": is_super,
                    },
                )
                if created:
                    user.set_password(password)
                    user.save()
                    tag = "超级管理员" if is_super else "普通用户"
                    self.stdout.write(self.style.SUCCESS(f"已创建: {username}（{user.get_role_display()}）密码: {password} [{tag}]"))
                else:
                    if force:
                        user.set_password(password)
                        user.role = role
                        user.is_staff = is_super
                        user.is_superuser = is_super
                        user.save()
                        self.stdout.write(self.style.WARNING(f"已更新: {username} 密码已重置为 {password}"))
                    else:
                        self.stdout.write(f"已存在，跳过: {username}（加 --force 可重置密码）")
            except IntegrityError as e:
                self.stdout.write(self.style.ERROR(f"创建 {username} 失败: {e}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("可登录地址："))
        self.stdout.write("  前台: http://127.0.0.1:8000/  或 http://127.0.0.1:8000/login/")
        self.stdout.write("  后台: http://127.0.0.1:8000/admin/  （药品/帖子/用户/系统 四种管理员均可进入）")

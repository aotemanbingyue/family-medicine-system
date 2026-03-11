"""
自动发布医学小贴士（本地题库版）。

用法：
    python manage.py auto_publish_medical_tip
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.medical_tip_auto import publish_auto_tip_for_date


class Command(BaseCommand):
    help = "自动发布今日医学小贴士（若当天已存在则跳过）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--publisher",
            type=str,
            default="sys_admin",
            help="发布人用户名（默认 sys_admin）",
        )

    def handle(self, *args, **options):
        username = options["publisher"]
        User = get_user_model()
        publisher = User.objects.filter(username=username).first()
        target_date = timezone.localdate()
        tip, created = publish_auto_tip_for_date(target_date, publisher=publisher)

        if created:
            self.stdout.write(self.style.SUCCESS(f"已自动发布：{tip.tip_date} - {tip.title}"))
        else:
            self.stdout.write(self.style.WARNING(f"已存在，跳过：{tip.tip_date} - {tip.title}"))

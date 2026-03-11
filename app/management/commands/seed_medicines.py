"""
向全局药品库添加示例药品。
用法：python manage.py seed_medicines
"""
from django.core.management.base import BaseCommand
from app.medicine_sync import sync_default_global_medicines


class Command(BaseCommand):
    help = "向全局药品库添加示例药品"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="先清空全局药品库（软删除），再添加示例药品",
        )

    def handle(self, *args, **options):
        result = sync_default_global_medicines(overwrite=bool(options.get("clear")))
        self.stdout.write(
            self.style.SUCCESS(
                f"同步完成：新增 {result['added']}，更新 {result['updated']}，恢复 {result['restored']}，"
                f"内置总量 {result['total_default']}。"
            )
        )

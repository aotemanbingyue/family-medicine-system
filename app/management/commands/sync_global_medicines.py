"""
同步全局标准药库（统一接口）。

用法：
    python manage.py sync_global_medicines
    python manage.py sync_global_medicines --overwrite
"""
from django.core.management.base import BaseCommand

from app.medicine_sync import sync_default_global_medicines


class Command(BaseCommand):
    help = "同步全局标准药库：增量同步或覆盖同步"

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="覆盖同步：先软删除现有启用药品，再同步内置数据",
        )

    def handle(self, *args, **options):
        overwrite = bool(options.get("overwrite"))
        result = sync_default_global_medicines(overwrite=overwrite)
        mode_text = "覆盖同步" if overwrite else "增量同步"
        self.stdout.write(
            self.style.SUCCESS(
                f"{mode_text}完成：新增 {result['added']}，更新 {result['updated']}，恢复 {result['restored']}，"
                f"内置总量 {result['total_default']}。"
            )
        )

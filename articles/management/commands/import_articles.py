import hashlib
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings

from articles.models import EconomistArticle


class Command(BaseCommand):
    help = "从 economist_articles.json 导入文章到 EconomistArticle 表（幂等：以 link 为基准 update_or_create）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="",
            help="JSON 文件路径，默认使用项目根目录下的 economist_articles.json",
        )

    def handle(self, *args, **options):
        file_path = options.get("file", "").strip()
        if not file_path:
            file_path = Path(settings.BASE_DIR) / "economist_articles.json"
        else:
            file_path = Path(file_path).resolve()

        if not file_path.exists():
            self.stderr.write(self.style.ERROR(f"文件不存在: {file_path}"))
            return

        try:
            raw = file_path.read_text(encoding="utf-8").strip()
            data = json.loads(raw)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"解析 JSON 失败: {e}"))
            return

        if not isinstance(data, list):
            self.stderr.write(self.style.ERROR("JSON 根节点应为数组"))
            return

        created = 0
        updated = 0
        for item in data:
            if not isinstance(item, dict):
                continue
            link = (item.get("link") or "").strip()
            if not link:
                continue
            link_hash = hashlib.sha256(link.encode("utf-8")).hexdigest()
            paragraphs = item.get("first_two_paragraphs") or []
            content = "\n\n".join(p.strip() for p in paragraphs if p and isinstance(p, str))
            title = (item.get("title") or "").strip() or link
            section = (item.get("section") or "").strip()
            snippet = (item.get("snippet") or "").strip()

            obj, was_created = EconomistArticle.objects.update_or_create(
                link_hash=link_hash,
                defaults={
                    "title": title,
                    "section": section,
                    "snippet": snippet,
                    "link": link,
                    "content": content,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"导入完成：新增 {created} 条，更新 {updated} 条。"))

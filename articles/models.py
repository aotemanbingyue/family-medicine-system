from django.db import models
import hashlib


class EconomistArticle(models.Model):
    """经济学人外刊文章，用于个人阅读室。"""
    title = models.CharField("标题", max_length=500)
    section = models.CharField("栏目分类", max_length=200, blank=True)
    snippet = models.TextField("摘要", blank=True)
    link = models.TextField("原文链接")
    link_hash = models.CharField("链接哈希", max_length=64, unique=True, db_index=True)
    content = models.TextField("正文（前两段合并）", blank=True)
    created_at = models.DateTimeField("导入时间", auto_now_add=True)

    class Meta:
        verbose_name = "经济学人文章"
        verbose_name_plural = "经济学人文章"
        ordering = ["-id"]

    def __str__(self):
        return self.title[:50]

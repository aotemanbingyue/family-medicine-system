from django.shortcuts import render
from .models import EconomistArticle


def article_list(request):
    """按最新导入顺序展示所有文章（卡片瀑布流）。"""
    articles = EconomistArticle.objects.all().order_by("-id")
    return render(request, "articles/list.html", {"articles": articles})

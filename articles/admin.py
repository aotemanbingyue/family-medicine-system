from django.contrib import admin
from .models import EconomistArticle


@admin.register(EconomistArticle)
class EconomistArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "link_hash", "created_at")
    search_fields = ("title", "section", "snippet")
    list_filter = ("created_at",)

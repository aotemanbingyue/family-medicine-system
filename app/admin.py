

# Register your models here.


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# 导入你刚才写的 4 个模型
from .models import User, GlobalMedicine, FamilyMedicine, SharePost, PostComment, CommentReply, SystemAnnouncement

# 1. 注册自定义用户模型
# 使用 Django 自带的 UserAdmin 来管理用户，功能更强大
admin.site.register(User, UserAdmin)

# 2. 注册全局药库
@admin.register(GlobalMedicine)
class GlobalMedicineAdmin(admin.ModelAdmin):
    # 后台列表显示哪些字段
    list_display = ('name', 'category', 'barcode', 'is_deleted')
    # 增加搜索框
    search_fields = ('name', 'barcode')
    # 增加过滤器
    list_filter = ('category', 'is_deleted')

# 3. 注册家庭药箱
@admin.register(FamilyMedicine)
class FamilyMedicineAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'stock', 'expiration_date', 'is_deleted')
    list_filter = ('owner',)

# 4. 注册共享帖子
@admin.register(SharePost)
class SharePostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'medicine', 'status', 'create_time')
    list_filter = ('status',)


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'content', 'create_time', 'read_at')


@admin.register(CommentReply)
class CommentReplyAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user', 'content', 'create_time', 'read_at')


@admin.register(SystemAnnouncement)
class SystemAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'publisher', 'is_pinned', 'create_time')
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', LoginView.as_view(template_name='app/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),

    # 家庭药箱
    path('medicine/', views.family_medicine_list, name='family_medicine_list'),
    path('medicine/add/', views.family_medicine_add, name='family_medicine_add'),
    path('medicine/<int:pk>/edit/', views.family_medicine_edit, name='family_medicine_edit'),
    path('medicine/<int:pk>/delete/', views.family_medicine_delete, name='family_medicine_delete'),

    # 过期提醒
    path('expiration/', views.expiration_reminder, name='expiration_reminder'),
    path('taking-reminder/', views.taking_reminder, name='taking_reminder'),

    # 家庭组协作：查看家庭成员药箱、设置/加入家庭组
    path('family/', views.family_group, name='family_group'),
    path('family/manage/', views.family_group_manage, name='family_group_manage'),

    # 共享广场：帖子列表、详情、发帖、我的帖子
    path('share/', views.share_list, name='share_list'),
    path('share/<int:pk>/', views.share_detail, name='share_detail'),
    path('share/add/', views.share_create, name='share_create'),
    path('share/my/', views.share_my_list, name='share_my_list'),
    path('share/<int:pk>/comment/', views.share_comment, name='share_comment'),
    path('share/comment/<int:pk>/reply/', views.share_reply, name='share_reply'),
    path('share/<int:pk>/add-to-box/', views.share_add_to_family_box, name='share_add_to_family_box'),

    # 消息中心（信箱）：谁在我的帖子下留言
    path('message/', views.message_inbox, name='message_inbox'),
    path('message/private/admins/', views.private_message_admin_select, name='private_message_admin_select'),
    path('message/private/admin/<int:admin_id>/', views.private_message_chat_with_admin, name='private_message_chat_with_admin'),
    path('message/private/inbox/', views.private_message_admin_inbox, name='private_message_admin_inbox'),
    path('message/private/user/<int:user_id>/', views.private_message_chat_with_user, name='private_message_chat_with_user'),

    # 普通用户：查询全局药品库（只读）
    path('medicine/search/', views.global_medicine_search, name='global_medicine_search'),

    # 系统公告：列表所有人可见，发布仅系统管理员
    path('announcement/', views.announcement_list, name='announcement_list'),
    path('announcement/create/', views.announcement_create, name='announcement_create'),
    path('medical-tips/', views.medical_tip_list, name='medical_tip_list'),
    path('medical-tips/create/', views.medical_tip_create, name='medical_tip_create'),
    path('medical-tips/auto-publish-today/', views.medical_tip_auto_publish_today, name='medical_tip_auto_publish_today'),

    # 按角色限制：药品管理员维护全局药库
    path('admin-med/global/', views.global_medicine_list, name='global_medicine_list'),
    path('admin-med/global/sync/', views.global_medicine_sync, name='global_medicine_sync'),
    path('admin-med/global/add/', views.global_medicine_add, name='global_medicine_add'),
    path('admin-med/global/<int:pk>/edit/', views.global_medicine_edit, name='global_medicine_edit'),
    path('admin-med/global/<int:pk>/delete/', views.global_medicine_delete, name='global_medicine_delete'),
    path('admin-med/family-medicine-audit/', views.family_medicine_audit_list, name='family_medicine_audit_list'),
    path('admin-med/family-medicine-audit/<int:pk>/approve/', views.family_medicine_audit_approve, name='family_medicine_audit_approve'),
    path('admin-med/family-medicine-audit/<int:pk>/reject/', views.family_medicine_audit_reject, name='family_medicine_audit_reject'),
    path('admin-med/post-medicine-audit/', views.post_medicine_audit_list, name='post_medicine_audit_list'),
    path('admin-med/post-medicine-audit/<int:pk>/approve/', views.post_medicine_audit_approve, name='post_medicine_audit_approve'),
    path('admin-med/post-medicine-audit/<int:pk>/reject/', views.post_medicine_audit_reject, name='post_medicine_audit_reject'),

    # 按角色限制：帖子管理员审核
    path('admin-post/audit/', views.post_audit_list, name='post_audit_list'),
    path('admin-post/audit/<int:pk>/approve/', views.post_audit_approve, name='post_audit_approve'),
    path('admin-post/audit/<int:pk>/reject/', views.post_audit_reject, name='post_audit_reject'),

    # 按角色限制：用户管理员管理用户
    path('admin-user/users/', views.user_admin_list, name='user_admin_list'),
    path('admin-user/users/<int:pk>/toggle-active/', views.user_admin_toggle_active, name='user_admin_toggle_active'),
    path('admin-user/users/<int:pk>/reset-password/', views.user_admin_reset_password, name='user_admin_reset_password'),
    path('admin-user/family-join-requests/', views.user_admin_family_join_requests, name='user_admin_family_join_requests'),
    path('admin-user/family-join-requests/<int:pk>/approve/', views.user_admin_family_join_approve, name='user_admin_family_join_approve'),
    path('admin-user/family-join-requests/<int:pk>/reject/', views.user_admin_family_join_reject, name='user_admin_family_join_reject'),
]

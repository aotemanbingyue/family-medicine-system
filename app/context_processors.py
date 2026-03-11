"""
为导航栏提供「待处理数量」，用于红点/数字角标提示。
"""
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q


def nav_alerts(request):
    """注入导航/下拉用待处理数量，用于红点与数字角标。未登录则为 0。"""
    data = {
        "expiration_alert_count": 0,
        "pending_audit_count": 0,
        "pending_family_medicine_count": 0,
        "pending_post_medicine_count": 0,
        "pending_family_join_count": 0,
        "my_posts_alert_count": 0,
        "unread_comment_count": 0,
        "unread_private_count": 0,
    }
    if not getattr(request, "user", None) or not request.user.is_authenticated:
        return data

    from app.models import FamilyMedicine, SharePost, PostComment, CommentReply, FamilyJoinRequest, PrivateMessage

    today = timezone.now().date()

    # 未读消息数 = 别人在我帖子下的留言 + 别人对我留言的回复（双方都有红点）
    data["unread_comment_count"] = PostComment.objects.filter(
        post__user=request.user,
        read_at__isnull=True,
    ).count()
    data["unread_comment_count"] += CommentReply.objects.filter(
        comment__user=request.user,
        read_at__isnull=True,
    ).count()
    # 私聊未读数：统一并入消息中心红点，避免用户遗漏管理员回复
    data["unread_private_count"] = PrivateMessage.objects.filter(
        receiver=request.user,
        read_at__isnull=True,
    ).count()
    data["unread_comment_count"] += data["unread_private_count"]
    # 过期提醒：已过期 + 30 天内将过期
    data["expiration_alert_count"] = FamilyMedicine.objects.filter(
        owner=request.user,
        is_deleted=False,
        audit_status=1,
        expiration_date__lte=today + timedelta(days=30),
    ).count()

    # 帖子审核（仅管理员）：待审核数
    if request.user.role in ("admin_post", "admin_sys"):
        data["pending_audit_count"] = SharePost.objects.filter(
            is_deleted=False,
            status=0,
        ).count()

    # 药品管理员：待审核家庭药箱药品数（仅普通用户提交）
    if request.user.role in ("admin_med", "admin_sys"):
        data["pending_family_medicine_count"] = FamilyMedicine.objects.filter(
            is_deleted=False,
            audit_status=0,
            owner__role="user",
        ).count()
        data["pending_post_medicine_count"] = SharePost.objects.filter(
            is_deleted=False,
            status=1,
            medicine_audit_status=0,
        ).count()

    # 用户管理员：待审核入组申请数
    if request.user.role in ("admin_user", "admin_sys"):
        data["pending_family_join_count"] = FamilyJoinRequest.objects.filter(
            status=0,
        ).count()

    # 我的帖子提醒：帖子审核待处理/驳回，或帖子已通过但药品审核待处理/驳回
    data["my_posts_alert_count"] = SharePost.objects.filter(
        user=request.user,
        is_deleted=False,
    ).filter(
        Q(status__in=(0, 2)) | Q(status=1, medicine_audit_status__in=(0, 2))
    ).count()

    return data

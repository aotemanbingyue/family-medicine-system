from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import (
    User,
    GlobalMedicine,
    FamilyMedicine,
    SharePost,
    PostComment,
    CommentReply,
    SystemAnnouncement,
    FamilyJoinRequest,
    PrivateMessage,
    MedicalTip,
    SharePostMedicineAdoption,
)
from .forms import (
    RegisterForm,
    FamilyMedicineForm,
    SharePostForm,
    PostCommentForm,
    CommentReplyForm,
    GlobalMedicineForm,
    SystemAnnouncementForm,
    PrivateMessageForm,
    MedicalTipForm,
)
from .decorators import role_required
from .medical_tip_auto import publish_auto_tip_for_date
from .medicine_sync import sync_default_global_medicines


def index(request):
    announcements = SystemAnnouncement.objects.all()[:5]
    latest_tip = MedicalTip.objects.order_by("-tip_date", "-create_time").first()
    if not request.user.is_authenticated:
        return render(request, 'app/index_guest.html', {'announcements': announcements, 'latest_tip': latest_tip})
    today = timezone.now().date()
    # 首页统计中只统计“审核通过”的家庭药品，避免待审核数据影响展示口径
    my_meds = FamilyMedicine.objects.filter(owner=request.user, is_deleted=False, audit_status=1)
    expiring_soon = my_meds.filter(expiration_date__lte=today + timedelta(days=30)).order_by('expiration_date')[:5]
    taking_reminder_count = my_meds.filter(reminder_enabled=True, daily_reminder_time__isnull=False).count()
    my_posts = SharePost.objects.filter(user=request.user, is_deleted=False).count()
    return render(request, 'app/index.html', {
        'my_meds_count': my_meds.count(),
        'expiring_soon': expiring_soon,
        'taking_reminder_count': taking_reminder_count,
        'my_posts_count': my_posts,
        'announcements': announcements,
        'latest_tip': latest_tip,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功，已为您登录。')
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form})


# ---------- 家庭药箱 ----------
@login_required
def family_medicine_list(request):
    # 家庭药箱列表展示用户自己的全部药品（含待审核/驳回），便于用户跟踪审核状态
    qs = FamilyMedicine.objects.filter(owner=request.user, is_deleted=False).order_by('-audit_status', 'expiration_date')
    return render(request, 'app/family_medicine_list.html', {'medicines': qs})


@login_required
def family_medicine_add(request):
    if request.method == 'POST':
        form = FamilyMedicineForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            # 普通用户提交后进入“待审核”；药品管理员/系统管理员提交可直接通过
            if request.user.role in ('admin_med', 'admin_sys'):
                obj.audit_status = 1
            else:
                obj.audit_status = 0
                obj.auditor = None
            obj.save()
            if obj.audit_status == 1:
                messages.success(request, '已添加药品并自动通过审核。')
            else:
                messages.success(request, '已提交药品，等待药品管理员审核。')
            return redirect('family_medicine_list')
    else:
        form = FamilyMedicineForm()
    return render(request, 'app/family_medicine_form.html', {'form': form, 'title': '添加药品'})


@login_required
def family_medicine_edit(request, pk):
    obj = get_object_or_404(FamilyMedicine, pk=pk, owner=request.user, is_deleted=False)
    if request.method == 'POST':
        form = FamilyMedicineForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save(commit=False)
            # 普通用户编辑后需重新审核；管理员编辑可直接通过
            if request.user.role in ('admin_med', 'admin_sys'):
                obj.audit_status = 1
            else:
                obj.audit_status = 0
                obj.auditor = None
            obj.save()
            if obj.audit_status == 1:
                messages.success(request, '已更新并通过审核。')
            else:
                messages.success(request, '已更新并重新提交审核。')
            return redirect('family_medicine_list')
    else:
        form = FamilyMedicineForm(instance=obj)
    return render(request, 'app/family_medicine_form.html', {'form': form, 'title': '编辑药品', 'medicine': obj})


@login_required
def family_medicine_delete(request, pk):
    obj = get_object_or_404(FamilyMedicine, pk=pk, owner=request.user, is_deleted=False)
    obj.is_deleted = True
    obj.save()
    messages.success(request, '已从药箱移除。')
    return redirect('family_medicine_list')


# ---------- 过期提醒 ----------
@login_required
def expiration_reminder(request):
    today = timezone.now().date()
    qs = FamilyMedicine.objects.filter(owner=request.user, is_deleted=False, audit_status=1)
    expired = qs.filter(expiration_date__lt=today).order_by('expiration_date')
    within_30 = qs.filter(expiration_date__gte=today, expiration_date__lte=today + timedelta(days=30)).order_by('expiration_date')
    return render(request, 'app/expiration_reminder.html', {
        'expired': expired,
        'within_30': within_30,
        'today': today,
    })


@login_required
def taking_reminder(request):
    """
    服药提醒页：展示用户已开启提醒的药品，并按“已到提醒时间 / 稍后提醒”分组。
    """
    now_time = timezone.localtime().time()
    qs = FamilyMedicine.objects.filter(
        owner=request.user,
        is_deleted=False,
        audit_status=1,
        reminder_enabled=True,
        daily_reminder_time__isnull=False,
    ).order_by("daily_reminder_time")
    due_now = [m for m in qs if m.daily_reminder_time <= now_time]
    due_later = [m for m in qs if m.daily_reminder_time > now_time]
    return render(
        request,
        "app/taking_reminder.html",
        {"due_now": due_now, "due_later": due_later, "now_time": now_time},
    )


# ---------- 家庭组协作 ----------
@login_required
def family_group(request):
    fid = request.user.family_id
    if not fid:
        return render(request, 'app/family_group.html', {'members': [], 'family_medicines': [], 'family_id': None, 'no_family': True})
    members = User.objects.filter(family_id=fid).exclude(role__startswith='admin')
    # 家庭成员（含自己）的药箱（未删除）
    family_medicines = FamilyMedicine.objects.filter(
        owner__family_id=fid, is_deleted=False, audit_status=1
    ).select_related('owner', 'global_info').order_by('owner__username', 'expiration_date')
    return render(request, 'app/family_group.html', {
        'members': members,
        'family_medicines': family_medicines,
        'family_id': fid,
        'no_family': False,
    })


@login_required
def family_group_manage(request):
    """设置或加入家庭组：创建新家庭组 或 输入家庭组ID加入已有家庭。"""
    from .forms import FamilyGroupForm
    if request.method == 'POST':
        form = FamilyGroupForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data.get('action')
            if action == 'create':
                import uuid
                fid = 'family_' + uuid.uuid4().hex[:8]
                request.user.family_id = fid
                request.user.save(update_fields=['family_id'])
                messages.success(request, f'已创建新家庭组，您的家庭组ID为：{fid}。请将此ID告知家人，他们填写相同ID即可加入。')
            else:
                fid = form.cleaned_data.get('family_id', '').strip()
                if fid:
                    if request.user.family_id == fid:
                        messages.info(request, f'您当前已在家庭组 {fid} 中。')
                        return redirect('family_group')
                    # 普通用户加入家庭组：改为“提交申请”，由用户管理员审核
                    if request.user.role in ('admin_user', 'admin_sys'):
                        request.user.family_id = fid
                        request.user.save(update_fields=['family_id'])
                        messages.success(request, f'已加入家庭组 {fid}。')
                    else:
                        pending = FamilyJoinRequest.objects.filter(
                            applicant=request.user, target_family_id=fid, status=0
                        ).exists()
                        if pending:
                            messages.warning(request, f'您已提交加入家庭组 {fid} 的申请，请等待用户管理员审核。')
                        else:
                            FamilyJoinRequest.objects.create(
                                applicant=request.user,
                                target_family_id=fid,
                                status=0,
                            )
                            messages.success(request, f'已提交加入家庭组 {fid} 的申请，请等待用户管理员审核。')
                else:
                    messages.error(request, '请输入家庭组ID。')
            return redirect('family_group')
    else:
        form = FamilyGroupForm()
    return render(request, 'app/family_group_manage.html', {'form': form})


# ---------- 共享广场 ----------
def share_list(request):
    # 共享广场仅展示“帖子审核通过 + 帖子药品审核通过”的内容
    qs = SharePost.objects.filter(
        is_deleted=False,
        status=1,
        medicine_audit_status=1,
    ).select_related('user', 'medicine').order_by('-create_time')
    return render(request, 'app/share_list.html', {'posts': qs})


def share_detail(request, pk):
    post = get_object_or_404(SharePost, pk=pk, is_deleted=False)
    # 非发布人查看时，帖子与帖子药品均需通过审核
    if (post.status != 1 or post.medicine_audit_status != 1) and post.user_id != request.user.id:
        messages.error(request, '该帖子未通过审核或已下架。')
        return redirect('share_list')
    comments = PostComment.objects.filter(post=post).select_related('user').order_by('create_time')
    # 帖子主人打开详情时，将该帖下所有留言标为已读
    if request.user.is_authenticated and request.user.id == post.user_id:
        PostComment.objects.filter(post=post, read_at__isnull=True).update(read_at=timezone.now())
    # 留言人（非帖子主人）打开详情时，将「别人回复我的留言」标为已读
    if request.user.is_authenticated and request.user.id != post.user_id:
        CommentReply.objects.filter(
            comment__post=post, comment__user=request.user, read_at__isnull=True
        ).update(read_at=timezone.now())
    replies = list(CommentReply.objects.filter(comment__post=post).select_related('user').order_by('create_time'))
    replies_by_cid = {}
    for r in replies:
        replies_by_cid.setdefault(r.comment_id, []).append(r)
    comments_with_replies = [(c, replies_by_cid.get(c.pk, [])) for c in comments]
    form = PostCommentForm() if request.user.is_authenticated and post.status == 1 and post.medicine_audit_status == 1 else None
    is_post_owner = request.user.is_authenticated and request.user.id == post.user_id
    can_add_to_box = (
        request.user.is_authenticated
        and not is_post_owner
        and post.status == 1
        and post.medicine_audit_status == 1
    )
    has_adopted = False
    if can_add_to_box:
        has_adopted = SharePostMedicineAdoption.objects.filter(
            post=post,
            adopter=request.user,
        ).exists()
    return render(request, 'app/share_detail.html', {
        'post': post,
        'comments_with_replies': comments_with_replies,
        'form': form,
        'is_post_owner': is_post_owner,
        'can_add_to_box': can_add_to_box,
        'has_adopted': has_adopted,
    })


@login_required
def share_create(request):
    # 发帖只允许使用“审核通过”的家庭药品，防止未审核药品进入共享流程
    my_meds = FamilyMedicine.objects.filter(owner=request.user, is_deleted=False, audit_status=1)
    if not my_meds.exists():
        messages.warning(request, '请先在家庭药箱中添加并通过审核的药品，再发布转让。')
        return redirect('family_medicine_list')
    if request.method == 'POST':
        form = SharePostForm(request.POST)
        form.fields['medicine'].queryset = my_meds
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            # 串行双审核：普通用户发帖先处于“待帖子审核”，帖子通过后再进入药品审核
            obj.medicine_audit_status = 1 if request.user.role in ("admin_med", "admin_sys") else -1
            if obj.medicine_audit_status == 1:
                obj.medicine_auditor = request.user
                obj.medicine_audit_time = timezone.now()
            else:
                obj.medicine_auditor = None
                obj.medicine_audit_time = None
            obj.save()
            if obj.medicine_audit_status == 1:
                messages.success(request, '已提交，等待帖子管理员审核。药品审核已自动通过。')
            else:
                messages.success(request, '已提交，先等待帖子管理员审核，通过后自动进入药品管理员审核。')
            return redirect('share_my_list')
    else:
        form = SharePostForm()
        form.fields['medicine'].queryset = my_meds
    return render(request, 'app/share_form.html', {'form': form, 'title': '发布转让'})


@login_required
def share_my_list(request):
    qs = SharePost.objects.filter(user=request.user, is_deleted=False).select_related('medicine').order_by('-create_time')
    return render(request, 'app/share_my_list.html', {'posts': qs})


@login_required
def share_comment(request, pk):
    post = get_object_or_404(SharePost, pk=pk, is_deleted=False, status=1, medicine_audit_status=1)
    if request.method == 'POST':
        form = PostCommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.post = post
            c.user = request.user
            c.save()
            messages.success(request, '留言成功。')
    return redirect('share_detail', pk=pk)


@login_required
def share_reply(request, pk):
    """帖子主人对某条留言回复；留言人会收到未读红点。"""
    comment = get_object_or_404(PostComment, pk=pk)
    post = comment.post
    if request.user.id != post.user_id:
        messages.error(request, '仅帖子主人可回复留言。')
        return redirect('share_detail', pk=post.pk)
    if post.is_deleted or post.status != 1 or post.medicine_audit_status != 1:
        messages.error(request, '该帖子不可回复。')
        return redirect('share_list')
    if request.method == 'POST':
        form = CommentReplyForm(request.POST)
        if form.is_valid():
            r = form.save(commit=False)
            r.comment = comment
            r.user = request.user
            r.save()
            messages.success(request, '回复成功，对方将收到消息提示。')
    return redirect('share_detail', pk=post.pk)


@login_required
@require_POST
def share_add_to_family_box(request, pk):
    """
    用户将“已通过双审核”的帖子药品加入自己的家庭药箱（仅一次）。
    """
    post = get_object_or_404(
        SharePost,
        pk=pk,
        is_deleted=False,
        status=1,
        medicine_audit_status=1,
    )
    if post.user_id == request.user.id:
        messages.warning(request, "不能把自己发布的帖子药品再次加入自己的药箱。")
        return redirect("share_detail", pk=pk)

    adopted, created = SharePostMedicineAdoption.objects.get_or_create(
        post=post,
        adopter=request.user,
    )
    if not created:
        messages.info(request, "该帖子药品您已加入过家庭药箱。")
        return redirect("share_detail", pk=pk)

    source = post.medicine
    FamilyMedicine.objects.create(
        owner=request.user,
        global_info=source.global_info,
        name=source.name,
        production_date=source.production_date,
        expiration_date=source.expiration_date,
        stock=1,
        unit=source.unit,
        reminder_enabled=source.reminder_enabled,
        daily_reminder_time=source.daily_reminder_time,
        dosage_note=source.dosage_note,
        # 来源于药品管理员审核通过的帖子药品，可直接通过
        audit_status=1,
        auditor=post.medicine_auditor,
    )
    messages.success(request, "已将该帖子药品加入您的家庭药箱。")
    return redirect("family_medicine_list")


# ---------- 消息中心（信箱）：谁在我的帖子下留言 + 谁回复了我的留言 ----------
@login_required
def message_inbox(request):
    """信箱：别人在我帖子下的留言 + 别人回复我在某帖下的留言，点击可跳转并标为已读。"""
    comments = (
        PostComment.objects.filter(post__user=request.user)
        .select_related("post", "user")
        .order_by("-create_time")
    )
    replies_to_me = (
        CommentReply.objects.filter(comment__user=request.user)
        .select_related("comment__post", "user")
        .order_by("-create_time")
    )
    # 私聊未读数：当前用户作为接收方且未读
    unread_private_count = PrivateMessage.objects.filter(
        receiver=request.user,
        read_at__isnull=True,
    ).count()
    recent_announcements = SystemAnnouncement.objects.select_related("publisher").order_by("-is_pinned", "-create_time")[:5]
    recent_tips = MedicalTip.objects.select_related("publisher").order_by("-tip_date", "-create_time")[:5]
    return render(
        request,
        "app/message_inbox.html",
        {
            "comments": comments,
            "replies_to_me": replies_to_me,
            "unread_private_count": unread_private_count,
            "recent_announcements": recent_announcements,
            "recent_tips": recent_tips,
        },
    )


# ---------- 私聊（普通用户 <-> 管理员） ----------
@login_required
def private_message_admin_select(request):
    """
    普通用户发起私聊：选择管理员作为会话对象。

    规则说明：
    1. 普通用户可联系任意管理员（用户/药品/帖子/系统管理员），避免用户先判断职责导致沟通阻塞；
    2. 管理员自己也可进入此页，用于主动联系其他管理员（答辩演示时更灵活）。
    """
    admin_roles = ("admin_user", "admin_med", "admin_post", "admin_sys")
    admins = User.objects.filter(role__in=admin_roles, is_active=True).order_by("role", "username")
    primary_admin = (
        User.objects.filter(role="admin_user", is_active=True).order_by("id").first()
        or User.objects.filter(role="admin_sys", is_active=True).order_by("id").first()
    )
    return render(
        request,
        "app/private_message_admin_select.html",
        {"admins": admins, "primary_admin": primary_admin},
    )


@login_required
def private_message_chat_with_admin(request, admin_id):
    """
    与某位管理员的私聊会话页（当前登录人作为普通用户侧入口）。
    """
    target_admin = get_object_or_404(
        User,
        pk=admin_id,
        role__in=("admin_user", "admin_med", "admin_post", "admin_sys"),
        is_active=True,
    )

    # 查询双向会话消息（我->管理员 或 管理员->我）
    chat_qs = PrivateMessage.objects.filter(
        (Q(sender=request.user, receiver=target_admin)) | (Q(sender=target_admin, receiver=request.user))
    ).select_related("sender", "receiver").order_by("create_time")

    # 打开会话即将“管理员发给我”的未读消息标为已读
    PrivateMessage.objects.filter(
        sender=target_admin,
        receiver=request.user,
        read_at__isnull=True,
    ).update(read_at=timezone.now())

    if request.method == "POST":
        form = PrivateMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = target_admin
            msg.save()
            messages.success(request, "消息已发送。")
            return redirect("private_message_chat_with_admin", admin_id=target_admin.pk)
    else:
        form = PrivateMessageForm()

    return render(
        request,
        "app/private_message_chat.html",
        {
            "target_user": target_admin,
            "messages_qs": chat_qs,
            "form": form,
            "is_admin_side": False,
        },
    )


@login_required
@role_required("admin_user", "admin_med", "admin_post", "admin_sys")
def private_message_admin_inbox(request):
    """
    管理员私聊收件箱：按“普通用户会话”聚合展示。
    """
    # 管理员收件箱仅聚合普通用户，避免管理员之间消息干扰审核工作流
    user_qs = User.objects.filter(role="user", is_active=True).order_by("username")
    conversations = []
    for normal_user in user_qs:
        latest = PrivateMessage.objects.filter(
            (Q(sender=request.user, receiver=normal_user)) | (Q(sender=normal_user, receiver=request.user))
        ).order_by("-create_time").first()
        if not latest:
            continue
        unread_count = PrivateMessage.objects.filter(
            sender=normal_user,
            receiver=request.user,
            read_at__isnull=True,
        ).count()
        conversations.append(
            {
                "user_obj": normal_user,
                "latest": latest,
                "unread_count": unread_count,
            }
        )

    # 最近会话优先
    conversations.sort(key=lambda x: x["latest"].create_time, reverse=True)
    return render(request, "app/private_message_admin_inbox.html", {"conversations": conversations})


@login_required
@role_required("admin_user", "admin_med", "admin_post", "admin_sys")
def private_message_chat_with_user(request, user_id):
    """
    管理员与普通用户私聊页。
    """
    target_user = get_object_or_404(User, pk=user_id, role="user", is_active=True)
    chat_qs = PrivateMessage.objects.filter(
        (Q(sender=request.user, receiver=target_user)) | (Q(sender=target_user, receiver=request.user))
    ).select_related("sender", "receiver").order_by("create_time")

    # 打开会话即将“用户发给管理员”的未读消息置为已读
    PrivateMessage.objects.filter(
        sender=target_user,
        receiver=request.user,
        read_at__isnull=True,
    ).update(read_at=timezone.now())

    if request.method == "POST":
        form = PrivateMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = target_user
            msg.save()
            messages.success(request, "回复已发送。")
            return redirect("private_message_chat_with_user", user_id=target_user.pk)
    else:
        form = PrivateMessageForm()

    return render(
        request,
        "app/private_message_chat.html",
        {
            "target_user": target_user,
            "messages_qs": chat_qs,
            "form": form,
            "is_admin_side": True,
        },
    )


# ---------- 普通用户：查询全局药品库（只读）----------
def global_medicine_search(request):
    """普通用户可查询全局药品库，支持按名称、分类、条形码筛选。数据来自药品管理员维护的本地库。"""
    qs = GlobalMedicine.objects.filter(is_deleted=False)
    keyword = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    if keyword:
        qs = qs.filter(Q(name__icontains=keyword) | Q(barcode__icontains=keyword))
    if category:
        qs = qs.filter(category=category)
    qs = qs.order_by('category', 'name')
    return render(request, 'app/global_medicine_search.html', {'medicines': qs, 'keyword': keyword, 'category': category})


# ---------- 药品管理员：全局药库（按角色限制）----------
@login_required
@role_required('admin_med', 'admin_sys')
def global_medicine_list(request):
    qs = GlobalMedicine.objects.filter(is_deleted=False).order_by('category', 'name')
    return render(request, 'app/global_medicine_list.html', {'medicines': qs})


@login_required
@role_required('admin_med', 'admin_sys')
@require_POST
def global_medicine_sync(request):
    """
    标准药库同步接口：
    1) 增量同步（默认）：不清理其他药品，仅更新内置数据；
    2) 覆盖同步：先软删除现有启用药品，再同步内置数据。
    """
    mode = request.POST.get("mode", "incremental").strip()
    overwrite = mode == "overwrite"
    result = sync_default_global_medicines(overwrite=overwrite)
    mode_text = "覆盖同步" if overwrite else "增量同步"
    messages.success(
        request,
        f"{mode_text}完成：新增 {result['added']}，更新 {result['updated']}，恢复 {result['restored']}。",
    )
    return redirect("global_medicine_list")


@login_required
@role_required('admin_med', 'admin_sys')
def global_medicine_add(request):
    if request.method == 'POST':
        form = GlobalMedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '已添加标准药品。')
            return redirect('global_medicine_list')
    else:
        form = GlobalMedicineForm()
    return render(request, 'app/global_medicine_form.html', {'form': form, 'title': '添加标准药品'})


@login_required
@role_required('admin_med', 'admin_sys')
def global_medicine_edit(request, pk):
    obj = get_object_or_404(GlobalMedicine, pk=pk, is_deleted=False)
    if request.method == 'POST':
        form = GlobalMedicineForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, '已更新。')
            return redirect('global_medicine_list')
    else:
        form = GlobalMedicineForm(instance=obj)
    return render(request, 'app/global_medicine_form.html', {'form': form, 'title': '编辑标准药品'})


@login_required
@role_required('admin_med', 'admin_sys')
def global_medicine_delete(request, pk):
    obj = get_object_or_404(GlobalMedicine, pk=pk, is_deleted=False)
    obj.is_deleted = True
    obj.save()
    messages.success(request, '已软删除。')
    return redirect('global_medicine_list')


# ---------- 药品管理员：家庭药箱药品审核 ----------
@login_required
@role_required('admin_med', 'admin_sys')
def family_medicine_audit_list(request):
    """
    药品管理员审核普通用户提交的家庭药箱药品。

    业务要点：
    1. 仅审核待审核（audit_status=0）的记录；
    2. 仅面向普通用户提交的数据（owner.role='user'），避免管理员互相审核造成职责混乱；
    3. 审核通过后，药品才能参与过期提醒、家庭共享、共享转让等后续业务链路。
    """
    qs = FamilyMedicine.objects.filter(
        is_deleted=False, audit_status=0, owner__role='user'
    ).select_related('owner', 'global_info').order_by('expiration_date')
    return render(request, 'app/family_medicine_audit_list.html', {'medicines': qs})


@login_required
@role_required('admin_med', 'admin_sys')
@require_POST
def family_medicine_audit_approve(request, pk):
    """
    审核通过：将药品状态改为 1，并记录审核人。
    """
    obj = get_object_or_404(FamilyMedicine, pk=pk, is_deleted=False, audit_status=0)
    obj.audit_status = 1
    obj.auditor = request.user
    obj.save(update_fields=['audit_status', 'auditor'])
    messages.success(request, '该药品已审核通过。')
    return redirect('family_medicine_audit_list')


@login_required
@role_required('admin_med', 'admin_sys')
@require_POST
def family_medicine_audit_reject(request, pk):
    """
    审核驳回：将药品状态改为 2，并记录审核人。
    用户可在家庭药箱中编辑后再次提交审核。
    """
    obj = get_object_or_404(FamilyMedicine, pk=pk, is_deleted=False, audit_status=0)
    obj.audit_status = 2
    obj.auditor = request.user
    obj.save(update_fields=['audit_status', 'auditor'])
    messages.success(request, '该药品已驳回。')
    return redirect('family_medicine_audit_list')


@login_required
@role_required('admin_med', 'admin_sys')
def post_medicine_audit_list(request):
    """
    药品管理员审核帖子内药品：仅处理帖子审核已通过但药品审核待处理的数据。
    """
    qs = SharePost.objects.filter(
        is_deleted=False,
        status=1,
        medicine_audit_status=0,
    ).select_related("user", "medicine").order_by("create_time")
    return render(request, "app/post_medicine_audit_list.html", {"posts": qs})


@login_required
@role_required('admin_med', 'admin_sys')
@require_POST
def post_medicine_audit_approve(request, pk):
    post = get_object_or_404(SharePost, pk=pk, is_deleted=False, status=1, medicine_audit_status=0)
    post.medicine_audit_status = 1
    post.medicine_auditor = request.user
    post.medicine_audit_time = timezone.now()
    post.save(update_fields=["medicine_audit_status", "medicine_auditor", "medicine_audit_time"])
    messages.success(request, "帖子药品审核已通过，用户可将该药品加入家庭药箱。")
    return redirect("post_medicine_audit_list")


@login_required
@role_required('admin_med', 'admin_sys')
@require_POST
def post_medicine_audit_reject(request, pk):
    post = get_object_or_404(SharePost, pk=pk, is_deleted=False, status=1, medicine_audit_status=0)
    post.medicine_audit_status = 2
    post.medicine_auditor = request.user
    post.medicine_audit_time = timezone.now()
    post.save(update_fields=["medicine_audit_status", "medicine_auditor", "medicine_audit_time"])
    messages.success(request, "帖子药品审核已驳回。")
    return redirect("post_medicine_audit_list")


# ---------- 帖子管理员：审核（按角色限制）----------
@login_required
@role_required('admin_post', 'admin_sys')
def post_audit_list(request):
    qs = SharePost.objects.filter(is_deleted=False, status=0).select_related('user', 'medicine').order_by('create_time')
    return render(request, 'app/post_audit_list.html', {'posts': qs})


@login_required
@role_required('admin_post', 'admin_sys')
def post_audit_approve(request, pk):
    post = get_object_or_404(SharePost, pk=pk, is_deleted=False, status=0)
    post.status = 1
    # 串行双审核：帖子通过后，若药品审核尚未启动(-1)，自动切换到待药品审核(0)
    if post.medicine_audit_status == -1:
        post.medicine_audit_status = 0
        post.medicine_auditor = None
        post.medicine_audit_time = None
    post.save()
    if post.medicine_audit_status == 1:
        messages.success(request, '帖子已通过审核，可直接在共享广场展示。')
    else:
        messages.success(request, '帖子已通过审核，已进入“待药品审核”。')
    return redirect('post_audit_list')


@login_required
@role_required('admin_post', 'admin_sys')
def post_audit_reject(request, pk):
    post = get_object_or_404(SharePost, pk=pk, is_deleted=False, status=0)
    post.status = 2
    post.save()
    messages.success(request, '已驳回。')
    return redirect('post_audit_list')


# ---------- 用户管理员：用户管理（按角色限制）----------
@login_required
@role_required('admin_user', 'admin_sys')
def user_admin_list(request):
    """
    用户管理员前台页面：查看用户列表，并支持按用户名关键字筛选。

    设计说明（论文答辩可讲）：
    1. 通过 role_required 装饰器实现 RBAC 访问控制，只有「用户管理员/系统管理员」可进入。
    2. 列表默认只展示 is_deleted 概念之外的“系统当前用户数据”（本项目 User 无软删除字段），
       因此直接基于 User 表做查询，并按角色、用户名排序，方便管理员巡检。
    3. 增加 q 查询参数，用于前台模糊搜索，便于演示“用户管理”功能的可用性。
    """
    keyword = request.GET.get('q', '').strip()
    # 基础查询：把用户按角色、用户名稳定排序，保证页面展示顺序可预测
    qs = User.objects.all().order_by('role', 'username')
    # 若输入关键字，则在用户名/手机号/家庭组ID 三个字段进行模糊匹配
    if keyword:
        qs = qs.filter(
            Q(username__icontains=keyword) |
            Q(phone__icontains=keyword) |
            Q(family_id__icontains=keyword)
        )
    return render(request, 'app/user_admin_list.html', {'users': qs, 'keyword': keyword})


@login_required
@role_required('admin_user', 'admin_sys')
def user_admin_family_join_requests(request):
    """
    用户管理员审核家庭组加入申请列表。
    """
    qs = FamilyJoinRequest.objects.filter(status=0).select_related('applicant').order_by('create_time')
    return render(request, 'app/user_admin_family_join_requests.html', {'requests': qs})


@login_required
@role_required('admin_user', 'admin_sys')
@require_POST
def user_admin_family_join_approve(request, pk):
    """
    通过家庭组加入申请：
    1) 申请状态置为通过；
    2) 将申请人 family_id 更新为目标家庭组ID。
    """
    req = get_object_or_404(FamilyJoinRequest, pk=pk, status=0)
    req.status = 1
    req.reviewer = request.user
    req.review_time = timezone.now()
    req.save(update_fields=['status', 'reviewer', 'review_time'])

    applicant = req.applicant
    applicant.family_id = req.target_family_id
    applicant.save(update_fields=['family_id'])

    messages.success(request, f'已通过 {applicant.username} 的入组申请。')
    return redirect('user_admin_family_join_requests')


@login_required
@role_required('admin_user', 'admin_sys')
@require_POST
def user_admin_family_join_reject(request, pk):
    """
    驳回家庭组加入申请：仅更新申请状态，不修改申请人家庭组信息。
    """
    req = get_object_or_404(FamilyJoinRequest, pk=pk, status=0)
    req.status = 2
    req.reviewer = request.user
    req.review_time = timezone.now()
    req.save(update_fields=['status', 'reviewer', 'review_time'])
    messages.success(request, f'已驳回 {req.applicant.username} 的入组申请。')
    return redirect('user_admin_family_join_requests')


@login_required
@role_required('admin_user', 'admin_sys')
@require_POST
def user_admin_toggle_active(request, pk):
    """
    用户启用/禁用切换。

    安全与业务约束：
    1. 必须使用 POST，避免 GET 链接误触导致状态改变（幂等与安全考虑）。
    2. 不允许管理员禁用自己账号，防止把自己“锁死”。
    3. 仅做 is_active 状态切换，不改动角色字段，职责边界清晰。
    """
    target_user = get_object_or_404(User, pk=pk)
    if target_user.pk == request.user.pk:
        messages.error(request, '不能禁用当前登录账号。')
        return redirect('user_admin_list')

    target_user.is_active = not target_user.is_active
    target_user.save(update_fields=['is_active'])
    state_text = '已启用' if target_user.is_active else '已禁用'
    messages.success(request, f'用户 {target_user.username} {state_text}。')
    return redirect('user_admin_list')


@login_required
@role_required('admin_user', 'admin_sys')
@require_POST
def user_admin_reset_password(request, pk):
    """
    用户密码重置（演示版）。

    说明：
    1. 该功能用于课程项目演示，统一重置为固定测试密码 123456。
    2. set_password 会自动执行 Django 密码哈希，符合认证安全流程。
    3. 同样限制不能重置当前登录管理员自身密码，避免演示过程中误操作。
    """
    target_user = get_object_or_404(User, pk=pk)
    if target_user.pk == request.user.pk:
        messages.error(request, '不能重置当前登录账号密码。')
        return redirect('user_admin_list')

    target_user.set_password('123456')
    target_user.save(update_fields=['password'])
    messages.success(request, f'用户 {target_user.username} 的密码已重置为 123456。')
    return redirect('user_admin_list')


# ---------- 系统公告：全体可见 + 系统管理员发布 ----------
def announcement_list(request):
    """系统公告列表，所有人可查看。"""
    qs = SystemAnnouncement.objects.select_related('publisher').order_by('-is_pinned', '-create_time')
    tips = MedicalTip.objects.select_related("publisher").order_by("-tip_date", "-create_time")[:7]
    return render(request, 'app/announcement_list.html', {'announcements': qs, 'tips': tips})


@login_required
@role_required('admin_sys')
def announcement_create(request):
    """系统管理员发布公告。"""
    if request.method == 'POST':
        form = SystemAnnouncementForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.publisher = request.user
            obj.save()
            messages.success(request, '公告已发布。')
            return redirect('announcement_list')
    else:
        form = SystemAnnouncementForm()
    return render(request, 'app/announcement_form.html', {'form': form, 'title': '发布系统公告'})


def medical_tip_list(request):
    """医学小贴士列表，所有人可见。"""
    tips = MedicalTip.objects.select_related("publisher").order_by("-tip_date", "-create_time")
    return render(request, "app/medical_tip_list.html", {"tips": tips})


@login_required
@role_required("admin_sys")
def medical_tip_create(request):
    """
    系统管理员发布“每日医学小贴士”。
    若同一天重复发布，则更新当天内容，确保“一天一条”。
    """
    if request.method == "POST":
        form = MedicalTipForm(request.POST)
        if form.is_valid():
            tip_date = form.cleaned_data["tip_date"]
            defaults = {
                "title": form.cleaned_data["title"],
                "content": form.cleaned_data["content"],
                "publisher": request.user,
            }
            tip, created = MedicalTip.objects.update_or_create(tip_date=tip_date, defaults=defaults)
            if created:
                messages.success(request, "医学小贴士已发布。")
            else:
                messages.success(request, "该日期已有小贴士，已更新为最新内容。")
            return redirect("medical_tip_list")
    else:
        form = MedicalTipForm(initial={"tip_date": timezone.localdate()})
    return render(request, "app/medical_tip_form.html", {"form": form, "title": "发布医学小贴士"})


@login_required
@role_required("admin_sys")
@require_POST
def medical_tip_auto_publish_today(request):
    """
    方案B：从本地题库自动发布“今日小贴士”。
    若当天已存在内容，则不覆盖（保留手动发布优先级）。
    """
    tip, created = publish_auto_tip_for_date(timezone.localdate(), publisher=request.user)
    if created:
        messages.success(request, f"已自动发布今日小贴士：{tip.title}")
    else:
        messages.info(request, "今天的小贴士已存在，未重复生成。")
    return redirect("medical_tip_list")

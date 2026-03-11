from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

# ==================================
# 1. 核心模型：用户系统 (对应开题报告：家庭组模块)
# ==================================
class User(AbstractUser):
    # 对应开题报告中的四种管理员角色 + 普通用户
    ROLE_CHOICES = (
        ('user', '普通家庭用户'),
        ('admin_user', '用户管理员'),
        ('admin_med', '药品管理员'),
        ('admin_post', '帖子管理员'),
        ('admin_sys', '系统管理员'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name="角色身份")
    
    phone = models.CharField(max_length=11, verbose_name="手机号", blank=True)
    family_id = models.CharField(max_length=20, verbose_name="家庭组ID", blank=True, null=True, help_text="同一ID视为一家人")
    
    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

# ==================================
# 2. 核心模型：全局标准药库 (对应开题报告：药品管理模块)
# ==================================
# 这是给"药品管理员"维护的“字典”，用户不能改，只能查
class GlobalMedicine(models.Model):
    name = models.CharField(max_length=100, verbose_name="药品通用名")
    category = models.CharField(max_length=50, verbose_name="分类", choices=(('感冒', '感冒类'), ('消炎', '消炎类'), ('慢性病', '慢性病'), ('儿童', '儿童用药')))
    barcode = models.CharField(max_length=50, verbose_name="条形码/国药准字", unique=True)
    description = models.TextField(verbose_name="说明书/功效", blank=True)
    
    # 【核心难点解决】软删除标记
    is_deleted = models.BooleanField(default=False, verbose_name="是否已删除")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "全局标准药库"
        verbose_name_plural = verbose_name

# ==================================
# 3. 核心模型：家庭药箱库存 (对应开题报告：家庭组模块)
# ==================================
# 这是用户自己家里的药
class FamilyMedicine(models.Model):
    # 药品审核状态：
    # 0 = 待审核（普通用户新增/编辑后需要药品管理员审核）
    # 1 = 审核通过（可参与过期提醒、共享转让、家庭汇总展示）
    # 2 = 审核驳回（用户可编辑后再次提交）
    AUDIT_STATUS_CHOICES = (
        (0, "待审核"),
        (1, "审核通过"),
        (2, "审核驳回"),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="归属人")
    # 关联全局药库信息（如果存在）
    global_info = models.ForeignKey(GlobalMedicine, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="关联标准库")
    
    # 用户自己填写的具体信息
    name = models.CharField(max_length=100, verbose_name="药品名称") 
    production_date = models.DateField(verbose_name="生产日期")
    expiration_date = models.DateField(verbose_name="过期日期") # 对应过期提醒
    
    stock = models.IntegerField(verbose_name="剩余数量")
    unit = models.CharField(max_length=10, default='盒', verbose_name="单位")
    # 服药提醒：启用后会在“服药提醒”页面按时间提示
    reminder_enabled = models.BooleanField(default=False, verbose_name="启用服药提醒")
    daily_reminder_time = models.TimeField(null=True, blank=True, verbose_name="每日提醒时间")
    dosage_note = models.CharField(max_length=100, blank=True, verbose_name="用药提示")

    # 家庭药箱药品审核字段：
    # 默认给 1（审核通过），用于兼容历史数据；
    # 新增逻辑中，普通用户提交会改成 0（待审核）。
    audit_status = models.IntegerField(
        choices=AUDIT_STATUS_CHOICES,
        default=1,
        verbose_name="审核状态",
    )
    # 记录最后一次审核该药品的管理员（药品管理员/系统管理员）
    auditor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audited_family_medicines",
        verbose_name="审核人",
    )
    
    # 【核心难点解决】软删除标记
    is_deleted = models.BooleanField(default=False, verbose_name="是否已删除")

    def __str__(self):
        return f"{self.owner.username}的{self.name}"

    class Meta:
        verbose_name = "我的家庭药箱"
        verbose_name_plural = verbose_name

# ==================================
# 4. 核心模型：共享帖子 (对应开题报告：帖子模块)
# ==================================
class SharePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="发布人")
    # 帖子必须引用家里的某个药
    medicine = models.ForeignKey(FamilyMedicine, on_delete=models.CASCADE, verbose_name="转让药品")
    
    title = models.CharField(max_length=100, verbose_name="标题")
    content = models.TextField(verbose_name="描述信息")
    
    # 帖子审核状态
    STATUS_CHOICES = (
        (0, '待审核'),
        (1, '审核通过'),
        (2, '驳回/违规'),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name="状态")
    # 帖子内药品审核状态：由药品管理员负责
    MED_AUDIT_CHOICES = (
        (-1, '待帖子审核'),
        (0, '待药品审核'),
        (1, '审核通过'),
        (2, '审核驳回'),
    )
    # 串行双审核：先帖子审核（status），通过后才进入药品审核（medicine_audit_status 从 -1 -> 0）
    medicine_audit_status = models.IntegerField(choices=MED_AUDIT_CHOICES, default=-1, verbose_name="药品审核状态")
    medicine_auditor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audited_share_post_medicines",
        verbose_name="药品审核人",
    )
    medicine_audit_time = models.DateTimeField(null=True, blank=True, verbose_name="药品审核时间")
    
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    
    # 【核心难点解决】软删除标记
    is_deleted = models.BooleanField(default=False, verbose_name="是否已删除")

    class Meta:
        verbose_name = "药品共享广场"
        verbose_name_plural = verbose_name


# ==================================
# 5. 帖子互动：评论/留言（我想联系）
# ==================================
class PostComment(models.Model):
    post = models.ForeignKey(SharePost, on_delete=models.CASCADE, verbose_name="帖子")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="留言人")
    content = models.CharField(max_length=300, verbose_name="留言内容")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="留言时间")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="帖子主人阅读时间", help_text="为空表示帖子主人未读")

    class Meta:
        verbose_name = "帖子留言"
        verbose_name_plural = verbose_name


# ==================================
# 6. 系统公告（系统管理员发布，全体用户可见）
# ==================================
class SystemAnnouncement(models.Model):
    title = models.CharField(max_length=200, verbose_name="公告标题")
    content = models.TextField(verbose_name="公告内容")
    publisher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="发布人")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    is_pinned = models.BooleanField(default=False, verbose_name="是否置顶")

    class Meta:
        verbose_name = "系统公告"
        verbose_name_plural = verbose_name
        ordering = ["-is_pinned", "-create_time"]

    def __str__(self):
        return self.title


# 帖子主人对某条留言的回复（留言人可见，并产生未读红点）
class CommentReply(models.Model):
    comment = models.ForeignKey(PostComment, on_delete=models.CASCADE, verbose_name="针对的留言")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="回复人（通常为帖子主人）")
    content = models.CharField(max_length=300, verbose_name="回复内容")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="回复时间")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="留言人阅读时间", help_text="为空表示被回复的留言人未读")

    class Meta:
        verbose_name = "留言回复"
        verbose_name_plural = verbose_name


# 家庭组加入申请：普通用户发起，用户管理员审核
class FamilyJoinRequest(models.Model):
    # 申请状态定义：
    # 0 = 待审核，1 = 审核通过，2 = 审核驳回
    STATUS_CHOICES = (
        (0, "待审核"),
        (1, "审核通过"),
        (2, "审核驳回"),
    )

    # 申请人（发起加入家庭组请求的用户）
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="family_join_requests",
        verbose_name="申请人",
    )
    # 目标家庭组 ID（申请加入哪个家庭）
    target_family_id = models.CharField(max_length=20, verbose_name="目标家庭组ID")
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name="审核状态")
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_family_join_requests",
        verbose_name="审核人",
    )
    review_note = models.CharField(max_length=200, blank=True, verbose_name="审核备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="申请时间")
    review_time = models.DateTimeField(null=True, blank=True, verbose_name="审核时间")

    class Meta:
        verbose_name = "家庭组加入申请"
        verbose_name_plural = verbose_name
        ordering = ["-create_time"]


class PrivateMessage(models.Model):
    """
    私聊消息模型（普通用户 <-> 管理员）。

    设计目标：
    1. 满足开题报告中的“普通用户可向管理员私聊”要求；
    2. 支持管理员回复，形成双向会话；
    3. 保持结构简单，便于毕业设计答辩演示。
    """
    # 消息发送方
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_private_messages",
        verbose_name="发送方",
    )
    # 消息接收方
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_private_messages",
        verbose_name="接收方",
    )
    # 文本消息正文
    content = models.CharField(max_length=500, verbose_name="消息内容")
    # 发送时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="发送时间")
    # 已读时间：为空表示接收方未读
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="已读时间")

    class Meta:
        verbose_name = "私聊消息"
        verbose_name_plural = verbose_name
        ordering = ["create_time"]


class MedicalTip(models.Model):
    """
    医学小贴士：由系统管理员每日发布一条，面向全体用户可见。
    """
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    tip_date = models.DateField(unique=True, verbose_name="发布日期")
    publisher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="published_medical_tips",
        verbose_name="发布人",
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "医学小贴士"
        verbose_name_plural = verbose_name
        ordering = ["-tip_date", "-create_time"]

    def __str__(self):
        return f"{self.tip_date} - {self.title}"


class SharePostMedicineAdoption(models.Model):
    """
    记录“用户从共享帖子将药品加入家庭药箱”的行为，避免重复加入。
    """
    post = models.ForeignKey(SharePost, on_delete=models.CASCADE, related_name="adoptions", verbose_name="来源帖子")
    adopter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="adopted_post_medicines", verbose_name="接收用户")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")

    class Meta:
        verbose_name = "帖子药品加入记录"
        verbose_name_plural = verbose_name
        unique_together = ("post", "adopter")
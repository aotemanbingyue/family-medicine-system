"""
创建两组家庭成员 + 感冒药相关数据，用于测试家庭组、发帖、审核、留言流程。
用法：python manage.py create_family_and_posts
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import date, timedelta

User = get_user_model()

# 需要 import 的模型在 handle 里按需导入，避免循环依赖
def run():
    from app.models import GlobalMedicine, FamilyMedicine, SharePost

    today = date.today()
    default_pass = "123456"

    # 1) 确保有感冒类标准药品（供家庭药箱关联）
    g1, _ = GlobalMedicine.objects.get_or_create(
        barcode="Z10930001",
        defaults={
            "name": "感冒灵颗粒",
            "category": "感冒",
            "description": "解热镇痛。用于感冒引起的头痛、发热、鼻塞等。",
            "is_deleted": False,
        },
    )
    g2, _ = GlobalMedicine.objects.get_or_create(
        barcode="Z10890002",
        defaults={
            "name": "板蓝根颗粒",
            "category": "感冒",
            "description": "清热解毒。用于肺胃热盛所致的咽喉肿痛等。",
            "is_deleted": False,
        },
    )

    # 2) 两组家庭成员（普通用户，不设超级管理员）
    families = [
        ("family_zhang", "张家", ["张家爸", "张家妈"]),
        ("family_li", "李家", ["李家爸", "李家妈"]),
    ]

    created_users = []  # (user, family_label)
    with transaction.atomic():
        for family_id, family_label, usernames in families:
            for username in usernames:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "role": "user",
                        "is_staff": False,
                        "is_superuser": False,
                        "family_id": family_id,
                    },
                )
                if created:
                    user.set_password(default_pass)
                    user.family_id = family_id
                    user.save()
                else:
                    user.family_id = family_id
                    user.save(update_fields=["family_id"])
                created_users.append((user, family_label))

        # 3) 为每个成员添加感冒药到家庭药箱（未删除）
        meds_for_post = []  # (user, family_medicine) 用于后面发帖
        for user, family_label in created_users:
            fm1 = FamilyMedicine.objects.filter(owner=user, name="感冒灵颗粒", is_deleted=False).first()
            if not fm1:
                fm1 = FamilyMedicine.objects.create(
                    owner=user,
                    name="感冒灵颗粒",
                    global_info=g1,
                    production_date=today - timedelta(days=200),
                    expiration_date=today + timedelta(days=165),
                    stock=2,
                    unit="盒",
                    is_deleted=False,
                )
            meds_for_post.append((user, fm1))
            fm2 = FamilyMedicine.objects.filter(owner=user, name="板蓝根颗粒", is_deleted=False).first()
            if not fm2:
                FamilyMedicine.objects.create(
                    owner=user,
                    name="板蓝根颗粒",
                    global_info=g2,
                    production_date=today - timedelta(days=100),
                    expiration_date=today + timedelta(days=265),
                    stock=1,
                    unit="盒",
                    is_deleted=False,
                )

        # 4) 发布感冒药转让帖：2 条待审核 + 1 条已通过（方便直接测留言）
        posts_data = [
            (created_users[0][0], meds_for_post[0][1], "转让一盒感冒灵颗粒", "家里多买了一盒感冒灵，未拆封，转给需要的人。", 0),
            (created_users[2][0], meds_for_post[2][1], "转让板蓝根一盒", "板蓝根颗粒一盒，保质期还长，有需要的联系。", 0),
            (created_users[1][0], meds_for_post[1][1], "多余感冒灵转让", "感冒灵颗粒剩余一盒转让，同城可自取。", 1),
        ]
        for user, fm, title, content, status in posts_data:
            post = SharePost.objects.filter(user=user, medicine=fm, title=title, is_deleted=False).first()
            if not post:
                post = SharePost.objects.create(
                    user=user,
                    medicine=fm,
                    title=title,
                    content=content,
                    status=status,
                    is_deleted=False,
                )
            else:
                post.content = content
                post.status = status
                post.is_deleted = False
                post.save()

    return created_users, families


class Command(BaseCommand):
    help = "创建两组家庭成员、感冒药数据与转让帖，用于测试流程"

    def handle(self, *args, **options):
        try:
            created_users, families = run()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"执行失败: {e}"))
            raise

        self.stdout.write(self.style.SUCCESS("两组家庭成员（密码均为 123456）："))
        for family_id, family_label, usernames in families:
            self.stdout.write(f"  【{family_label}】 family_id={family_id}：{', '.join(usernames)}")
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("已添加家庭药箱（感冒灵/板蓝根），并发布 3 条感冒药转让帖："))
        self.stdout.write("  · 2 条「待审核」：用 post_admin 登录 → 帖子审核 → 通过/驳回")
        self.stdout.write("  · 1 条「已通过」：在共享广场可见，可留言测试")
        self.stdout.write("")
        self.stdout.write("建议测试：登录 post_admin(123456) → 帖子审核 → 通过前两条 → 再用张家爸/李家爸 等登录看共享广场与留言。")

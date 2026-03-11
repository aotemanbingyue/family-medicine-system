"""
一键生成毕业设计演示数据（用户管理/药品管理/帖子管理/系统通知）。

用法：
    python manage.py seed_demo_scenarios
"""
from datetime import date, timedelta, time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone


class Command(BaseCommand):
    help = "生成演示场景数据：新帖子、待审药品、公告、小贴士、入组申请、私聊等"

    def handle(self, *args, **options):
        from app.models import (
            FamilyJoinRequest,
            FamilyMedicine,
            MedicalTip,
            PostComment,
            PrivateMessage,
            SharePost,
            SystemAnnouncement,
        )

        User = get_user_model()

        with transaction.atomic():
            # 1) 先确保核心测试账号和基础家庭帖子数据存在
            needed = ["sys_admin", "user_admin", "med_admin", "post_admin", "user1", "张家爸", "张家妈", "李家爸"]
            missing = [u for u in needed if not User.objects.filter(username=u).exists()]
            if missing:
                self.stdout.write(self.style.WARNING("检测到缺少基础用户，建议先执行："))
                self.stdout.write("  python manage.py create_test_users --force")
                self.stdout.write("  python manage.py create_family_and_posts")
                self.stdout.write(self.style.ERROR(f"缺少用户：{', '.join(missing)}"))
                return

            sys_admin = User.objects.get(username="sys_admin")
            user_admin = User.objects.get(username="user_admin")
            user1 = User.objects.get(username="user1")
            zhang_dad = User.objects.get(username="张家爸")
            zhang_mom = User.objects.get(username="张家妈")
            li_dad = User.objects.get(username="李家爸")

            # 2) 系统公告 + 每日医学小贴士（系统通知）
            SystemAnnouncement.objects.update_or_create(
                title="系统测试通知",
                defaults={
                    "content": "本周演示功能已更新：服药提醒、私聊管理员、帖子药品审核、用户信箱聚合。",
                    "publisher": sys_admin,
                    "is_pinned": True,
                },
            )
            MedicalTip.objects.update_or_create(
                tip_date=timezone.localdate(),
                defaults={
                    "title": "今日医学小贴士：感冒用药三注意",
                    "content": "1) 按说明书剂量服用；2) 不随意叠加同类成分；3) 出现持续高热及时就医。",
                    "publisher": sys_admin,
                },
            )

            # 3) 用户管理员场景：user1 申请加入张家家庭组
            user1.family_id = ""
            user1.save(update_fields=["family_id"])
            FamilyJoinRequest.objects.get_or_create(
                applicant=user1,
                target_family_id="family_zhang",
                status=0,
            )

            # 4) 药品管理员场景：user1 提交一个待审核家庭药品 + 服药提醒
            FamilyMedicine.objects.update_or_create(
                owner=user1,
                name="布洛芬缓释胶囊（测试待审）",
                defaults={
                    "production_date": date.today() - timedelta(days=30),
                    "expiration_date": date.today() + timedelta(days=360),
                    "stock": 1,
                    "unit": "盒",
                    "audit_status": 0,
                    "auditor": None,
                    "reminder_enabled": True,
                    "daily_reminder_time": time(20, 0),
                    "dosage_note": "晚饭后一次，每次1粒",
                    "is_deleted": False,
                },
            )

            # 5) 帖子管理员 + 药品管理员联动场景
            med_zhang_dad = FamilyMedicine.objects.filter(owner=zhang_dad, is_deleted=False).order_by("id").first()
            med_zhang_mom = FamilyMedicine.objects.filter(owner=zhang_mom, is_deleted=False).order_by("id").first()
            med_li_dad = FamilyMedicine.objects.filter(owner=li_dad, is_deleted=False).order_by("id").first()
            if not (med_zhang_dad and med_zhang_mom and med_li_dad):
                self.stdout.write(self.style.ERROR("缺少家庭药箱基础数据，请先执行 python manage.py create_family_and_posts"))
                return

            # 张家爸新帖子：待帖子审核（你提到的“张家爸发布了新帖子”）
            SharePost.objects.update_or_create(
                user=zhang_dad,
                title="张家爸新发布测试帖",
                defaults={
                    "medicine": med_zhang_dad,
                    "content": "这是用于演示的最新帖子：等待帖子管理员审核。",
                    "status": 0,
                    "medicine_audit_status": -1,
                    "medicine_auditor": None,
                    "medicine_audit_time": None,
                    "is_deleted": False,
                },
            )

            # 张家妈帖子：帖子已通过，但待药品审核（给药品管理员测试）
            SharePost.objects.update_or_create(
                user=zhang_mom,
                title="张家妈待药品审核帖子",
                defaults={
                    "medicine": med_zhang_mom,
                    "content": "该帖子内容已合规，等待药品管理员审核帖子内药品。",
                    "status": 1,
                    "medicine_audit_status": 0,
                    "medicine_auditor": None,
                    "medicine_audit_time": None,
                    "is_deleted": False,
                },
            )

            # 李家爸帖子：双审核通过（给普通用户测试“加入家庭药箱”）
            approved_post, _ = SharePost.objects.update_or_create(
                user=li_dad,
                title="李家爸可加入药箱示例帖",
                defaults={
                    "medicine": med_li_dad,
                    "content": "本帖用于演示：普通用户可在详情页点击“加入我的家庭药箱”。",
                    "status": 1,
                    "medicine_audit_status": 1,
                    "medicine_auditor": sys_admin,
                    "medicine_audit_time": timezone.now(),
                    "is_deleted": False,
                },
            )

            # 6) 留言与私聊消息（消息中心/用户信箱测试）
            PostComment.objects.get_or_create(
                post=approved_post,
                user=user1,
                content="我想要这盒药，请问如何联系您？",
            )
            PrivateMessage.objects.get_or_create(
                sender=user1,
                receiver=user_admin,
                content="管理员您好，我想咨询入组申请什么时候审核。",
            )

        self.stdout.write(self.style.SUCCESS("演示数据已就绪。建议测试路径："))
        self.stdout.write("1) post_admin：帖子审核 -> 查看“张家爸新发布测试帖”")
        self.stdout.write("2) med_admin：帖子药品审核 + 药箱药品审核")
        self.stdout.write("3) user_admin：入组审核 + 私聊收件箱")
        self.stdout.write("4) sys_admin：系统公告 + 今日医学小贴士")
        self.stdout.write("5) 普通用户(user1)：消息中心(聚合信箱) + 服药提醒 + 浏览帖子并加入家庭药箱")

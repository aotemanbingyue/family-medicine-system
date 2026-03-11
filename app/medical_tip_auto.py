"""
医学小贴士自动发布（本地题库版，不依赖外部 API）。
"""
from datetime import date

from app.models import MedicalTip


TIP_POOL = [
    ("感冒用药三注意", "按说明书剂量服用；避免重复使用同成分药；高热不退应及时就医。"),
    ("家庭药箱存放建议", "药品应避光、干燥、阴凉存放；儿童药物与成人药物建议分区管理。"),
    ("抗生素使用提醒", "抗生素需遵医嘱使用，不应自行加量、减量或提前停药。"),
    ("退烧药使用提醒", "退烧药可缓解症状，但持续发热超过 3 天建议线下就诊。"),
    ("慢病药物管理", "高血压、糖尿病等慢病药应规律服用，避免断药和自行换药。"),
    ("过期药品处理", "过期药品不建议继续服用，应按当地规范进行回收或分类处置。"),
    ("儿童用药原则", "儿童用药要按体重和年龄选择剂量，避免直接套用成人剂量。"),
    ("合并用药风险", "多种药物同服前应确认是否有相互作用，必要时咨询药师或医生。"),
    ("止痛药使用提醒", "止痛药可短期缓解疼痛，若疼痛反复或加重应尽快明确病因。"),
    ("胃药服用时机", "部分胃药需空腹服用，部分需饭后服用，请按说明书执行。"),
    ("家庭应急药建议", "可常备退热、止泻、创可贴、碘伏等基础应急用品。"),
    ("外用药注意事项", "外用药一般不可口服，涂抹前应清洁患处并注意过敏反应。"),
]


def publish_auto_tip_for_date(target_date: date, publisher=None):
    """
    自动发布指定日期的小贴士。
    - 若当日已存在，直接返回（不覆盖手动发布内容）；
    - 若不存在，从本地题库按日期轮换取一条生成。
    """
    exists = MedicalTip.objects.filter(tip_date=target_date).first()
    if exists:
        return exists, False

    idx = target_date.toordinal() % len(TIP_POOL)
    title, content = TIP_POOL[idx]
    tip = MedicalTip.objects.create(
        tip_date=target_date,
        title=f"今日医学小贴士：{title}",
        content=content,
        publisher=publisher,
    )
    return tip, True

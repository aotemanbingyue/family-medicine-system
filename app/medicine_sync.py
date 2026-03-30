"""
全局标准药库同步能力（本地数据源，不依赖外部 API）。
"""
from app.models import GlobalMedicine


DEFAULT_GLOBAL_MEDICINES = [
    ("感冒灵颗粒", "感冒", "6901234567890", "解热镇痛。用于感冒引起的头痛，发热，鼻塞，流涕，咽痛。"),
    ("板蓝根颗粒", "感冒", "6901234567891", "清热解毒，凉血利咽。用于肺胃热盛所致的咽喉肿痛、口咽干燥；急性扁桃体炎见上述证候者。"),
    ("复方氨酚烷胺片", "感冒", "6901234567892", "适用于缓解普通感冒及流行性感冒引起的发热、头痛、四肢酸痛、打喷嚏、流鼻涕、鼻塞、咽痛等症状。"),
    ("维C银翘片", "感冒", "6901234567893", "辛凉解表，清热解毒。用于流行性感冒引起的发热头痛、咳嗽、口干、咽喉疼痛。"),
    ("小儿氨酚黄那敏颗粒", "儿童", "6901234567894", "适用于缓解儿童普通感冒及流行性感冒引起的发热、头痛、四肢酸痛、打喷嚏、流鼻涕、鼻塞、咽痛等症状。"),
    ("阿莫西林胶囊", "消炎", "6901234567895", "用于敏感菌所致的中耳炎、鼻窦炎、咽炎、扁桃体炎等上呼吸道感染。"),
    ("头孢克肟分散片", "消炎", "6901234567896", "适用于敏感菌引起的支气管炎、支气管扩张症、慢性呼吸系统感染、肺炎等。"),
    ("阿奇霉素片", "消炎", "6901234567897", "用于敏感细菌引起的呼吸道感染、皮肤软组织感染。"),
    ("布洛芬缓释胶囊", "消炎", "6901234567898", "用于缓解轻至中度疼痛如头痛、关节痛、偏头痛、牙痛、肌肉痛、神经痛、痛经。也用于普通感冒或流行性感冒引起的发热。"),
    ("对乙酰氨基酚片", "消炎", "6901234567899", "用于普通感冒或流行性感冒引起的发热，也用于缓解轻至中度疼痛如头痛、关节痛、偏头痛、牙痛。"),
    ("硝苯地平缓释片", "慢性病", "6901234567800", "用于高血压、心绞痛。"),
    ("苯磺酸氨氯地平片", "慢性病", "6901234567801", "用于高血压、冠心病心绞痛。"),
    ("二甲双胍片", "慢性病", "6901234567802", "用于单纯饮食控制及体育锻炼治疗无效的2型糖尿病。"),
    ("阿卡波糖片", "慢性病", "6901234567803", "配合饮食控制，用于2型糖尿病。"),
    ("奥美拉唑肠溶胶囊", "慢性病", "6901234567804", "用于胃酸过多引起的烧心和反酸症状的短期缓解。"),
    ("蒙脱石散", "儿童", "6901234567805", "用于成人及儿童急、慢性腹泻。"),
    ("健胃消食片", "儿童", "6901234567806", "健胃消食。用于脾胃虚弱所致的食积，症见不思饮食、嗳腐酸臭、脘腹胀满。"),
    ("小儿止咳糖浆", "儿童", "6901234567807", "祛痰，镇咳。用于小儿感冒引起的咳嗽。"),
    ("氯雷他定片", "感冒", "6901234567808", "用于缓解过敏性鼻炎有关的症状，如喷嚏、流涕、鼻痒、鼻塞以及眼部痒及烧灼感。"),
    ("葡萄糖酸钙口服液", "儿童", "6901234567809", "用于预防和治疗钙缺乏症，如骨质疏松、手足抽搐症、骨发育不全等。"),
]

RX_NAME_KEYWORDS = ("阿莫西林", "头孢", "阿奇霉素", "硝苯地平", "氨氯地平", "二甲双胍", "阿卡波糖")


def _infer_rx_otc(name: str) -> str:
    for kw in RX_NAME_KEYWORDS:
        if kw in name:
            return "RX"
    return "OTC"


def sync_default_global_medicines(overwrite=False):
    """
    同步内置标准药库。
    - overwrite=False: 增量同步（新增+更新，保留其它药品）
    - overwrite=True : 覆盖同步（先软删除旧数据，再按内置数据重建）
    """
    if overwrite:
        GlobalMedicine.objects.filter(is_deleted=False).update(is_deleted=True)

    added = 0
    updated = 0
    restored = 0

    for name, category, barcode, description in DEFAULT_GLOBAL_MEDICINES:
        rx_otc = _infer_rx_otc(name)
        obj, created = GlobalMedicine.objects.get_or_create(
            barcode=barcode,
            defaults={
                "name": name,
                "rx_otc": rx_otc,
                "category": category,
                "description": description,
                "is_deleted": False,
            },
        )
        if created:
            added += 1
            continue

        changed = False
        if obj.name != name:
            obj.name = name
            changed = True
        if obj.rx_otc != rx_otc:
            obj.rx_otc = rx_otc
            changed = True
        if obj.category != category:
            obj.category = category
            changed = True
        if obj.description != description:
            obj.description = description
            changed = True
        if obj.is_deleted:
            obj.is_deleted = False
            restored += 1
            changed = True
        if changed:
            obj.save()
            updated += 1

    return {
        "added": added,
        "updated": updated,
        "restored": restored,
        "total_default": len(DEFAULT_GLOBAL_MEDICINES),
    }

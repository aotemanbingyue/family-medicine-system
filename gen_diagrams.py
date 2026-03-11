# -*- coding: utf-8 -*-
"""
用 matplotlib 生成论文所需图片：
1. 图4-1 系统总体架构图
2. 图4-2 系统功能模块图  
3. 图4-3 家庭组模块流程图
4. 图4-4 药品管理模块流程图
5. 图4-5 帖子双审核流程图
6. 图4-6 系统通知模块流程图
7. 图4-7 系统ER实体关系图
"""
import matplotlib
matplotlib.rcParams['font.family'] = ['Microsoft YaHei', 'SimHei', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

OUT = r'd:\SoftWare\Code\bysj\diagrams'
os.makedirs(OUT, exist_ok=True)

# ── 通用颜色 ──────────────────────────────────────────────
C_BLUE   = '#2E75B6'
C_GREEN  = '#70AD47'
C_ORANGE = '#ED7D31'
C_GRAY   = '#767171'
C_LIGHT  = '#BDD7EE'
C_PURPLE = '#7030A0'
C_RED    = '#C00000'
C_YELLOW = '#FFC000'

def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  生成: {path}')
    return path

# ══════════════════════════════════════════════════════════
# 工具：画流程图节点 + 箭头
# ══════════════════════════════════════════════════════════
def flowbox(ax, x, y, w, h, text, color='#2E75B6', shape='rect', fontsize=9):
    if shape == 'diamond':
        dx, dy = w/2, h/2
        poly = plt.Polygon([[x,y+dy],[x+dx,y],[x+w,y+dy],[x+dx,y+h*2]],
                            closed=True, fc=color, ec='white', lw=1.5, zorder=3)
        ax.add_patch(poly)
        ax.text(x+dx, y+dy, text, ha='center', va='center',
                fontsize=fontsize, color='white', fontweight='bold', zorder=4)
    elif shape == 'oval':
        ellipse = mpatches.Ellipse((x+w/2, y+h/2), w, h,
                                    fc=color, ec='white', lw=1.5, zorder=3)
        ax.add_patch(ellipse)
        ax.text(x+w/2, y+h/2, text, ha='center', va='center',
                fontsize=fontsize, color='white', fontweight='bold', zorder=4)
    else:
        rect = FancyBboxPatch((x, y), w, h,
                               boxstyle='round,pad=0.03',
                               fc=color, ec='white', lw=1.5, zorder=3)
        ax.add_patch(rect)
        ax.text(x+w/2, y+h/2, text, ha='center', va='center',
                fontsize=fontsize, color='white', fontweight='bold',
                wrap=True, zorder=4)

def arrow(ax, x1, y1, x2, y2, label='', color='#555555'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx+0.05, my, label, fontsize=7.5, color=color, va='center')

# ══════════════════════════════════════════════════════════
# 图4-2  系统功能模块图（树形结构）
# ══════════════════════════════════════════════════════════
def gen_module_tree():
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14); ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # 根节点
    flowbox(ax, 5.5, 5.8, 3, 0.8, '家庭药品管理与共享平台', C_BLUE, fontsize=10)

    # 5个一级模块
    modules = [
        (0.3, 3.8, '家庭组\n模块', C_GREEN),
        (2.9, 3.8, '药品管理\n模块', C_ORANGE),
        (5.5, 3.8, '帖子\n模块', C_BLUE),
        (8.1, 3.8, '系统通知\n模块', C_PURPLE),
        (10.7, 3.8, '系统管理\n模块', C_RED),
    ]
    for mx, my, txt, c in modules:
        flowbox(ax, mx, my, 2.4, 0.9, txt, c, fontsize=9)
        ax.annotate('', xy=(mx+1.2, my+0.9), xytext=(7, 5.8),
                    arrowprops=dict(arrowstyle='->', color='#888', lw=1.2))

    # 二级功能
    subs = [
        # 家庭组
        (0.0, 2.2, '用户注册/登录', C_LIGHT, '#333'),
        (0.0, 1.4, '家庭组创建/加入', C_LIGHT, '#333'),
        (0.0, 0.6, '成员信息管理', C_LIGHT, '#333'),
        # 药品管理
        (2.6, 2.2, '标准药库维护', C_LIGHT, '#333'),
        (2.6, 1.4, '家庭药箱管理', C_LIGHT, '#333'),
        (2.6, 0.6, '药品审核流程', C_LIGHT, '#333'),
        # 帖子
        (5.2, 2.2, '帖子发布/管理', C_LIGHT, '#333'),
        (5.2, 1.4, '串行双审核', C_LIGHT, '#333'),
        (5.2, 0.6, '药品采纳入箱', C_LIGHT, '#333'),
        # 系统通知
        (7.8, 2.2, '过期/服药提醒', C_LIGHT, '#333'),
        (7.8, 1.4, '系统公告推送', C_LIGHT, '#333'),
        (7.8, 0.6, '私信沟通渠道', C_LIGHT, '#333'),
        # 系统管理
        (10.4, 2.2, '用户管理员', C_LIGHT, '#333'),
        (10.4, 1.4, '药品管理员', C_LIGHT, '#333'),
        (10.4, 0.6, '帖子/系统管理员', C_LIGHT, '#333'),
    ]
    parents_x = [1.5, 4.1, 6.7, 9.3, 11.9]
    for i, (sx, sy, stxt, sc, tc) in enumerate(subs):
        rect = FancyBboxPatch((sx, sy), 2.5, 0.65,
                               boxstyle='round,pad=0.02', fc=sc, ec='#aaa', lw=1, zorder=3)
        ax.add_patch(rect)
        ax.text(sx+1.25, sy+0.32, stxt, ha='center', va='center',
                fontsize=8, color=tc, zorder=4)
        px = parents_x[i // 3]
        ax.annotate('', xy=(sx+1.25, sy+0.65), xytext=(px, 3.8),
                    arrowprops=dict(arrowstyle='->', color='#aaa', lw=1.0))

    ax.set_title('图 4-2  系统功能模块图', fontsize=12, fontweight='bold', pad=10)
    return save(fig, 'fig4-2_module_tree.png')

# ══════════════════════════════════════════════════════════
# 通用流程图生成器（垂直链）
# ══════════════════════════════════════════════════════════
def gen_flowchart(title, steps, figname, w=5, step_h=0.7, gap=0.35):
    """
    steps: list of (text, shape, color)
           shape: 'oval'|'rect'|'diamond'
    """
    n = len(steps)
    total_h = n * step_h + (n-1) * gap + 1.5
    fig, ax = plt.subplots(figsize=(w, total_h))
    ax.set_xlim(0, w); ax.set_ylim(0, total_h)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    bw = w * 0.7
    bx = (w - bw) / 2
    y = total_h - 1.0

    for i, (txt, shape, color) in enumerate(steps):
        if shape == 'diamond':
            bh = step_h * 1.3
        else:
            bh = step_h
        flowbox(ax, bx, y - bh, bw, bh, txt, color, shape, fontsize=8.5)
        if i < n - 1:
            arrow(ax, w/2, y - bh, w/2, y - bh - gap)
        y = y - bh - gap

    ax.set_title(title, fontsize=11, fontweight='bold', pad=8)
    return save(fig, figname)

# ══════════════════════════════════════════════════════════
# 图4-3  家庭组模块流程图
# ══════════════════════════════════════════════════════════
def gen_family_flow():
    steps = [
        ('开始', 'oval', C_GRAY),
        ('用户填写注册信息', 'rect', C_BLUE),
        ('账号激活，完成注册', 'rect', C_GREEN),
        ('用户登录系统', 'rect', C_BLUE),
        ('选择：创建 或 申请加入家庭组', 'diamond', C_ORANGE),
        ('创建家庭组\n（系统生成 family_id）', 'rect', C_GREEN),
        ('提交加入申请\n（状态：待审核）', 'rect', C_BLUE),
        ('用户管理员审核申请', 'rect', C_PURPLE),
        ('审核通过，更新家庭组归属', 'rect', C_GREEN),
        ('进入家庭协作管理', 'rect', C_BLUE),
        ('结束', 'oval', C_GRAY),
    ]
    return gen_flowchart('图 4-3  家庭组模块流程图', steps, 'fig4-3_family_flow.png', w=6)

# ══════════════════════════════════════════════════════════
# 图4-4  药品管理模块流程图
# ══════════════════════════════════════════════════════════
def gen_medicine_flow():
    steps = [
        ('开始', 'oval', C_GRAY),
        ('用户在标准药库中检索药品', 'rect', C_BLUE),
        ('点击"添加至家庭药箱"', 'rect', C_BLUE),
        ('系统创建药箱记录\n（状态：待审核）', 'rect', C_ORANGE),
        ('药品管理员审核药品申请', 'rect', C_PURPLE),
        ('审核通过，状态变更为"已通过"', 'rect', C_GREEN),
        ('系统检测有效期（< 30天预警）', 'rect', C_ORANGE),
        ('用户设置服药提醒时间', 'rect', C_BLUE),
        ('结束', 'oval', C_GRAY),
    ]
    return gen_flowchart('图 4-4  药品管理模块流程图', steps, 'fig4-4_medicine_flow.png', w=6)

# ══════════════════════════════════════════════════════════
# 图4-5  帖子串行双审核流程图（横向）
# ══════════════════════════════════════════════════════════
def gen_post_flow():
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.set_xlim(0, 14); ax.set_ylim(0, 5)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    nodes = [
        (0.2,  2.0, 1.6, 0.8, '用户填写帖子\n绑定药品记录', 'rect',    C_BLUE),
        (2.2,  2.0, 1.6, 0.8, '提交发布\n（待帖子审核）', 'rect',    C_ORANGE),
        (4.2,  1.6, 1.6, 1.5, '帖子管理员\n审核内容合规？', 'diamond', C_PURPLE),
        (6.2,  2.0, 1.6, 0.8, '进入待药品审核\n通知药品管理员', 'rect', C_ORANGE),
        (8.2,  1.6, 1.6, 1.5, '药品管理员\n审核药品真实？', 'diamond', C_PURPLE),
        (10.2, 2.0, 1.6, 0.8, '帖子公开展示\n共享广场', 'rect',    C_GREEN),
        (12.2, 2.0, 1.6, 0.8, '其他用户\n采纳药品入箱', 'rect',    C_BLUE),
    ]
    cx = []
    for x, y, w, h, txt, shape, color in nodes:
        flowbox(ax, x, y, w, h, txt, color, shape, fontsize=8)
        cx.append(x + w/2)

    # 主流箭头
    for i in range(len(nodes)-1):
        x1 = nodes[i][0] + nodes[i][2]
        y1 = nodes[i][1] + nodes[i][3]/2
        x2 = nodes[i+1][0]
        y2 = nodes[i+1][1] + nodes[i+1][3]/2
        arrow(ax, x1, y1, x2, y2, color='#555')

    # 驳回路径（帖子管理员）
    ax.annotate('', xy=(3.0, 0.7), xytext=(5.0, 1.6),
                arrowprops=dict(arrowstyle='->', color=C_RED, lw=1.5,
                                connectionstyle='arc3,rad=0.3'))
    ax.text(3.5, 0.45, '驳回 → 通知用户', fontsize=8, color=C_RED, ha='center')

    # 驳回路径（药品管理员）
    ax.annotate('', xy=(7.0, 0.7), xytext=(9.0, 1.6),
                arrowprops=dict(arrowstyle='->', color=C_RED, lw=1.5,
                                connectionstyle='arc3,rad=0.3'))
    ax.text(7.6, 0.45, '驳回 → 通知用户', fontsize=8, color=C_RED, ha='center')

    # 角色标注
    ax.text(5.0, 4.5, '帖子管理员审核', fontsize=8.5, color=C_PURPLE,
            ha='center', style='italic',
            bbox=dict(boxstyle='round', fc='#F2E8FA', ec=C_PURPLE, lw=1))
    ax.text(9.0, 4.5, '药品管理员审核', fontsize=8.5, color=C_PURPLE,
            ha='center', style='italic',
            bbox=dict(boxstyle='round', fc='#F2E8FA', ec=C_PURPLE, lw=1))
    ax.annotate('', xy=(5.0, 3.2), xytext=(5.0, 4.4),
                arrowprops=dict(arrowstyle='->', color=C_PURPLE, lw=1))
    ax.annotate('', xy=(9.0, 3.2), xytext=(9.0, 4.4),
                arrowprops=dict(arrowstyle='->', color=C_PURPLE, lw=1))

    ax.set_title('图 4-5  帖子串行双审核流程图', fontsize=11, fontweight='bold', pad=8)
    return save(fig, 'fig4-5_post_flow.png')

# ══════════════════════════════════════════════════════════
# 图4-6  系统通知模块流程图
# ══════════════════════════════════════════════════════════
def gen_notify_flow():
    steps = [
        ('开始', 'oval', C_GRAY),
        ('系统管理员发布公告/医学小贴士', 'rect', C_PURPLE),
        ('消息推送至用户消息中心', 'rect', C_BLUE),
        ('系统扫描药品有效期（< 30天）', 'rect', C_ORANGE),
        ('生成过期提醒 / 服药提醒', 'rect', C_ORANGE),
        ('用户通过私信联系管理员', 'rect', C_BLUE),
        ('管理员在私聊收件箱回复', 'rect', C_GREEN),
        ('用户消息中心统一展示', 'rect', C_BLUE),
        ('结束', 'oval', C_GRAY),
    ]
    return gen_flowchart('图 4-6  系统通知模块流程图', steps, 'fig4-6_notify_flow.png', w=6)

# ══════════════════════════════════════════════════════════
# 图4-7  系统 ER 图（实体关系图）
# ══════════════════════════════════════════════════════════
def gen_er_diagram():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14); ax.set_ylim(0, 9)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # 实体定义 (x, y, w, h, name, color)
    entities = {
        'User':          (5.5, 7.2, 2.8, 0.8, '用户\n(User)',          C_BLUE),
        'GlobalMed':     (0.5, 4.5, 2.8, 0.8, '全局标准药库\n(GlobalMedicine)', C_GREEN),
        'FamilyMed':     (5.5, 4.5, 2.8, 0.8, '家庭药箱\n(FamilyMedicine)',     C_ORANGE),
        'SharePost':     (10.5, 4.5, 2.8, 0.8, '共享帖子\n(SharePost)',          C_PURPLE),
        'JoinReq':       (0.5, 1.8, 2.8, 0.8, '家庭组加入申请\n(FamilyJoinRequest)', C_RED),
        'PrivMsg':       (5.5, 1.8, 2.8, 0.8, '私信消息\n(PrivateMessage)',       C_BLUE),
        'Announce':      (10.5, 1.8, 2.8, 0.8, '系统公告\n(SystemAnnouncement)', C_PURPLE),
        'MedTip':        (10.5, 0.2, 2.8, 0.8, '医学小贴士\n(MedicalTip)',        C_GREEN),
        'Adoption':      (5.5, 2.8, 2.8, 0.8, '药品采纳记录\n(Adoption)',         C_GRAY),
    }

    def ec(name):
        e = entities[name]
        return e[0]+e[2]/2, e[1]+e[3]/2

    for key, (x, y, w, h, txt, c) in entities.items():
        flowbox(ax, x, y, w, h, txt, c, fontsize=8.5)

    def rel_line(e1, e2, label, label_pos=0.5, offset=(0,0.12)):
        x1, y1 = ec(e1)
        x2, y2 = ec(e2)
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#555', lw=1.5))
        mx = x1 + (x2-x1)*label_pos + offset[0]
        my = y1 + (y2-y1)*label_pos + offset[1]
        ax.text(mx, my, label, fontsize=7.5, color='#333', ha='center',
                bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='#ccc', lw=0.8))

    rel_line('User', 'FamilyMed',  '1拥有N', label_pos=0.5, offset=(-0.5, 0.1))
    rel_line('FamilyMed', 'GlobalMed', 'N关联1(可选)', label_pos=0.5, offset=(0, 0.15))
    rel_line('User', 'SharePost',  '1发布N', label_pos=0.5, offset=(0.5, 0.1))
    rel_line('FamilyMed', 'SharePost', '1绑定1', label_pos=0.5, offset=(0, 0.15))
    rel_line('User', 'JoinReq',    '1提交N', label_pos=0.5, offset=(-0.5, 0.1))
    rel_line('User', 'PrivMsg',    '1发送N', label_pos=0.5, offset=(-0.4, 0.1))
    rel_line('User', 'Announce',   '1发布N', label_pos=0.5, offset=(0.5, 0.1))
    rel_line('User', 'MedTip',     '1发布N', label_pos=0.5, offset=(0.6, 0.05))
    rel_line('SharePost', 'Adoption', '1产生N', label_pos=0.5, offset=(0.5, 0.1))
    rel_line('User', 'Adoption',   '1采纳N', label_pos=0.5, offset=(-0.2, 0.1))
    rel_line('FamilyMed', 'Adoption', '1对应N', label_pos=0.5, offset=(-0.5, 0.1))

    ax.set_title('图 4-7  系统 E-R 图（实体关系图）', fontsize=12, fontweight='bold', pad=10)
    return save(fig, 'fig4-7_er.png')

# ══════════════════════════════════════════════════════════
# 执行
# ══════════════════════════════════════════════════════════
print('开始生成图片...')
p2 = gen_module_tree()
p3 = gen_family_flow()
p4 = gen_medicine_flow()
p5 = gen_post_flow()
p6 = gen_notify_flow()
p7 = gen_er_diagram()
print('\n全部图片生成完成。')

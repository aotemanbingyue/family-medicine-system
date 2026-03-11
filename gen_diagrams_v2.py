# -*- coding: utf-8 -*-
"""
黑白风格图表生成（参考用户提供的样式：白底、黑框、黑字、直角连线）
生成内容：
  fig4-2  系统功能模块图（树形）
  fig4-3  家庭组模块流程图
  fig4-4  药品管理模块流程图
  fig4-5  帖子串行双审核流程图
  fig4-6  系统通知模块流程图
  fig4-7a ER图（用户/药品/帖子核心关系）
  fig4-7b ER图（消息/公告/家庭组关系）
"""
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['font.family'] = ['Microsoft YaHei', 'SimHei', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os, sys

OUT = r'd:\SoftWare\Code\bysj\diagrams'
os.makedirs(OUT, exist_ok=True)

BK  = 'white'          # 背景/填充
BRD = 'black'          # 边框/线条/箭头颜色
TXT = 'black'          # 文字颜色
LW  = 1.2              # 线宽

def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    sys.stdout.buffer.write(f'  生成: {path}\n'.encode('utf-8','replace'))
    return path

# ─────────────────────────────────────────────────────────
# 基础绘图工具
# ─────────────────────────────────────────────────────────
def draw_rect(ax, x, y, w, h, text, fontsize=9, bold=False):
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle='square,pad=0',
        fc=BK, ec=BRD, lw=LW, zorder=3
    )
    ax.add_patch(rect)
    fw = 'bold' if bold else 'normal'
    ax.text(x+w/2, y+h/2, text, ha='center', va='center',
            fontsize=fontsize, color=TXT, fontweight=fw,
            zorder=4, linespacing=1.4)

def draw_oval(ax, x, y, w, h, text, fontsize=9):
    ellipse = mpatches.Ellipse((x+w/2, y+h/2), w, h,
                                fc=BK, ec=BRD, lw=LW, zorder=3)
    ax.add_patch(ellipse)
    ax.text(x+w/2, y+h/2, text, ha='center', va='center',
            fontsize=fontsize, color=TXT, zorder=4)

def draw_diamond(ax, x, y, w, h, text, fontsize=8.5):
    cx, cy = x+w/2, y+h/2
    pts = [[cx, y+h], [x+w, cy], [cx, y], [x, cy]]
    poly = plt.Polygon(pts, closed=True, fc=BK, ec=BRD, lw=LW, zorder=3)
    ax.add_patch(poly)
    ax.text(cx, cy, text, ha='center', va='center',
            fontsize=fontsize, color=TXT, zorder=4, linespacing=1.3)

def v_arrow(ax, x, y1, y2):
    ax.annotate('', xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle='->', color=BRD, lw=LW))

def h_line(ax, x1, x2, y):
    ax.plot([x1, x2], [y, y], color=BRD, lw=LW, zorder=2)

def v_line(ax, x, y1, y2):
    ax.plot([x, x], [y1, y2], color=BRD, lw=LW, zorder=2)

def corner_arrow_down(ax, x_from, y_from, x_to, y_to):
    """L形折线+箭头（先水平后垂直）"""
    ax.plot([x_from, x_to], [y_from, y_from], color=BRD, lw=LW, zorder=2)
    ax.annotate('', xy=(x_to, y_to), xytext=(x_to, y_from),
                arrowprops=dict(arrowstyle='->', color=BRD, lw=LW))

def side_label(ax, x, y, text, fontsize=8, side='right'):
    dx = 0.12 if side == 'right' else -0.12
    ax.text(x+dx, y, text, ha='left' if side == 'right' else 'right',
            va='center', fontsize=fontsize, color='#333')

# ══════════════════════════════════════════════════════════
# 图4-2  系统功能模块图（参考用户图，直角连线，白底黑框）
# ══════════════════════════════════════════════════════════
def gen_module_tree():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14); ax.set_ylim(0, 8)
    ax.axis('off')

    # 根节点
    draw_rect(ax, 5.3, 6.6, 3.4, 0.7, '家庭药品管理和共享平台', fontsize=10, bold=True)
    root_cx = 5.3 + 3.4/2   # 7.0
    root_by = 6.6            # 根节点底部y

    # 一级模块：5列，均匀分布
    m1 = [
        (0.4,  4.9, 2.0, 0.65, '家庭组模块'),
        (3.0,  4.9, 2.2, 0.65, '药品管理模块'),
        (5.8,  4.9, 1.8, 0.65, '帖子模块'),
        (8.2,  4.9, 2.2, 0.65, '系统通知模块'),
        (10.9, 4.9, 2.2, 0.65, '系统管理模块'),
    ]
    module_cxs = []
    for mx, my, mw, mh, mtxt in m1:
        draw_rect(ax, mx, my, mw, mh, mtxt, fontsize=9, bold=False)
        module_cxs.append(mx + mw/2)

    # 根到一级：从根底部中心下一段垂直线，再水平分叉到各模块顶部中心
    mid_y = 5.8   # 水平汇聚线的y
    v_line(ax, root_cx, root_by, mid_y)
    h_line(ax, module_cxs[0], module_cxs[-1], mid_y)
    for cx in module_cxs:
        v_line(ax, cx, mid_y, 4.9+0.65)

    # 二级功能（每列竖排小框，文字竖写用换行）
    subs = {
        0: [  # 家庭组
            '用户\n注册\n登录\n成组',
            '家庭\n药品\n库添\n加删\n除药\n品',
            '用户\n管理\n员查\n询用\n户信\n息',
            '设立\n用户\n信箱',
        ],
        1: [  # 药品管理
            '用户\n查询\n全局\n药品\n库',
            '药品\n管理\n员审\n核申\n请',
            '药品\n管理\n员管\n理全\n局药\n品库',
        ],
        2: [  # 帖子
            '用户\n发布\n删除\n修改\n引用\n帖子',
            '用户\n帖子\n内申\n请入\n库药\n品',
            '帖子\n管理\n员审\n核帖\n子',
        ],
        3: [  # 系统通知
            '药品\n过期\n服用\n提醒',
            '系统\n公告\n消息\n推送',
            '系统\n管理\n员管\n理系\n统',
        ],
        4: [  # 系统管理
            '添加\n各类\n管理\n员',
            '权限\n管理',
        ],
    }

    sub_w = 0.5
    sub_h_unit = 0.48  # 每行高度

    for col, items in subs.items():
        mx, my, mw, mh, _ = m1[col]
        parent_cx = mx + mw/2
        parent_by = my  # 模块框底部

        n = len(items)
        total_w = n * sub_w + (n-1) * 0.18
        start_x = parent_cx - total_w/2

        # 水平汇聚线
        sub_top_y = my - 0.35
        h_line(ax, start_x + sub_w/2, start_x + (n-1)*(sub_w+0.18) + sub_w/2, sub_top_y)
        v_line(ax, parent_cx, parent_by, sub_top_y)

        for j, stxt in enumerate(items):
            sx = start_x + j*(sub_w + 0.18)
            lines = stxt.count('\n') + 1
            sh = lines * sub_h_unit
            sy = sub_top_y - sh

            draw_rect(ax, sx, sy, sub_w, sh, stxt, fontsize=7)
            v_line(ax, sx + sub_w/2, sub_top_y, sy + sh)

    ax.set_title('图 4-2  系统功能模块图', fontsize=11, fontweight='bold',
                 pad=8, color=TXT)
    return save(fig, 'fig4-2_module_tree.png')


# ══════════════════════════════════════════════════════════
# 通用垂直流程图（黑白、直角）
# ══════════════════════════════════════════════════════════
def gen_flow(title, steps, figname, fig_w=5.5):
    """
    steps: list of (text, shape)
           shape: 'oval' | 'rect' | 'diamond'
    """
    BOX_W = 3.2
    BOX_H_RECT    = 0.62
    BOX_H_DIAMOND = 0.85
    BOX_H_OVAL    = 0.55
    GAP = 0.35
    PAD_X = (fig_w - BOX_W) / 2

    # 计算总高
    total_h = 1.0
    for _, shape in steps:
        if shape == 'diamond': total_h += BOX_H_DIAMOND + GAP
        elif shape == 'oval':  total_h += BOX_H_OVAL + GAP
        else:                  total_h += BOX_H_RECT + GAP

    fig, ax = plt.subplots(figsize=(fig_w, total_h))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, total_h)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    y = total_h - 0.7
    cx = fig_w / 2

    for i, (txt, shape) in enumerate(steps):
        if shape == 'diamond':
            bh = BOX_H_DIAMOND
        elif shape == 'oval':
            bh = BOX_H_OVAL
        else:
            bh = BOX_H_RECT

        bx = PAD_X
        by = y - bh

        if shape == 'oval':
            draw_oval(ax, bx, by, BOX_W, bh, txt, fontsize=9)
        elif shape == 'diamond':
            draw_diamond(ax, bx, by, BOX_W, bh, txt, fontsize=8.5)
        else:
            draw_rect(ax, bx, by, BOX_W, bh, txt, fontsize=9)

        if i < len(steps) - 1:
            v_arrow(ax, cx, by, by - GAP)

        y = by - GAP

    ax.set_title(title, fontsize=10, fontweight='bold', pad=6, color=TXT)
    return save(fig, figname)


# ══════════════════════════════════════════════════════════
# 图4-3  家庭组模块流程图
# ══════════════════════════════════════════════════════════
def gen_family_flow():
    steps = [
        ('开始', 'oval'),
        ('用户填写注册信息', 'rect'),
        ('账号激活，完成注册', 'rect'),
        ('用户登录系统', 'rect'),
        ('选择：创建 或 申请加入家庭组', 'diamond'),
        ('创建家庭组（系统生成 family_id）', 'rect'),
        ('提交加入申请（状态：待审核）', 'rect'),
        ('用户管理员审核申请', 'rect'),
        ('审核通过，更新家庭组归属', 'rect'),
        ('进入家庭协作管理', 'rect'),
        ('结束', 'oval'),
    ]
    return gen_flow('图 4-3  家庭组模块流程图', steps, 'fig4-3_family_flow.png')


# ══════════════════════════════════════════════════════════
# 图4-4  药品管理模块流程图
# ══════════════════════════════════════════════════════════
def gen_medicine_flow():
    steps = [
        ('开始', 'oval'),
        ('用户在标准药库中检索药品', 'rect'),
        ('点击"添加至家庭药箱"', 'rect'),
        ('系统创建药箱记录（状态：待审核）', 'rect'),
        ('药品管理员审核申请', 'rect'),
        ('是否通过审核？', 'diamond'),
        ('状态变更为"已通过"，入库成功', 'rect'),
        ('系统检测有效期（< 30天提醒）', 'rect'),
        ('用户设置服药提醒时间', 'rect'),
        ('结束', 'oval'),
    ]
    return gen_flow('图 4-4  药品管理模块流程图', steps, 'fig4-4_medicine_flow.png')


# ══════════════════════════════════════════════════════════
# 图4-5  帖子串行双审核流程图（横向）
# ══════════════════════════════════════════════════════════
def gen_post_flow():
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.set_xlim(0, 15); ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    BH = 0.7   # 矩形高
    DH = 1.0   # 菱形高
    BW = 1.6   # 宽
    MID_Y = 3.2

    # 节点定义 (x_left, text, shape)
    nodes = [
        (0.3,  '用户填写帖子\n绑定药品记录', 'rect'),
        (2.3,  '提交发布\n（待帖子审核）', 'rect'),
        (4.3,  '帖子管理员\n审核内容\n是否合规？', 'diamond'),
        (6.5,  '进入待药品审核\n通知药品管理员', 'rect'),
        (8.5,  '药品管理员\n审核药品\n是否真实？', 'diamond'),
        (10.7, '帖子公开展示\n共享广场', 'rect'),
        (12.7, '其他用户\n采纳药品入箱', 'rect'),
    ]

    centers = []
    for x, txt, shape in nodes:
        if shape == 'diamond':
            bh = DH; by = MID_Y - DH/2
        else:
            bh = BH; by = MID_Y - BH/2
        if shape == 'diamond':
            draw_diamond(ax, x, by, BW, bh, txt, fontsize=8)
        else:
            draw_rect(ax, x, by, BW, bh, txt, fontsize=8.5)
        centers.append((x+BW/2, MID_Y))

    # 主流箭头
    for i in range(len(nodes)-1):
        x1 = nodes[i][0] + BW
        x2 = nodes[i+1][0]
        ax.annotate('', xy=(x2, MID_Y), xytext=(x1, MID_Y),
                    arrowprops=dict(arrowstyle='->', color=BRD, lw=LW))

    # 驳回 ─ 帖子管理员 → 向下弯折 → 标注"驳回"
    rej_y = 1.5
    rej1_x = 4.3 + BW/2  # 菱形中心x
    ax.annotate('', xy=(rej1_x, MID_Y - DH/2), xytext=(rej1_x, rej_y),
                arrowprops=dict(arrowstyle='<-', color=BRD, lw=LW))
    ax.text(rej1_x+0.1, rej_y+0.15, '驳回，\n通知用户', fontsize=8, color='black')

    rej2_x = 8.5 + BW/2
    ax.annotate('', xy=(rej2_x, MID_Y - DH/2), xytext=(rej2_x, rej_y),
                arrowprops=dict(arrowstyle='<-', color=BRD, lw=LW))
    ax.text(rej2_x+0.1, rej_y+0.15, '驳回，\n通知用户', fontsize=8, color='black')

    # 角色标注框（上方）
    for rx, rlabel in [(4.3+BW/2, '① 帖子管理员审核'), (8.5+BW/2, '② 药品管理员审核')]:
        ax.text(rx, 5.4, rlabel, ha='center', fontsize=8.5,
                bbox=dict(boxstyle='square,pad=0.3', fc='white', ec='black', lw=1.0))
        ax.annotate('', xy=(rx, MID_Y+DH/2), xytext=(rx, 5.2),
                    arrowprops=dict(arrowstyle='->', color=BRD, lw=1.0))

    ax.set_title('图 4-5  帖子串行双审核流程图', fontsize=10, fontweight='bold', pad=6)
    return save(fig, 'fig4-5_post_flow.png')


# ══════════════════════════════════════════════════════════
# 图4-6  系统通知模块流程图
# ══════════════════════════════════════════════════════════
def gen_notify_flow():
    steps = [
        ('开始', 'oval'),
        ('系统管理员发布公告 / 医学小贴士', 'rect'),
        ('消息推送至用户消息中心', 'rect'),
        ('系统扫描药品有效期（< 30天）', 'rect'),
        ('生成过期提醒 / 服药提醒通知', 'rect'),
        ('用户通过私信联系管理员', 'rect'),
        ('管理员在私聊收件箱回复', 'rect'),
        ('用户消息中心统一展示全部通知', 'rect'),
        ('结束', 'oval'),
    ]
    return gen_flow('图 4-6  系统通知模块流程图', steps, 'fig4-6_notify_flow.png')


# ══════════════════════════════════════════════════════════
# ER 图：黑白 Chen 风格（实体矩形 + 菱形关系 + 连线）
# ══════════════════════════════════════════════════════════
def er_entity(ax, x, y, w, h, name, attrs=None, fontsize=9):
    """实体：双层矩形（外框加粗）"""
    draw_rect(ax, x, y, w, h, name, fontsize=fontsize, bold=True)
    if attrs:
        # 属性列表竖排在实体框内（小字）
        pass

def er_rel(ax, x, y, w, h, verb, fontsize=8.5):
    """关系：菱形"""
    draw_diamond(ax, x, y, w, h, verb, fontsize=fontsize)

def er_line(ax, x1, y1, x2, y2, card1='', card2=''):
    ax.plot([x1, x2], [y1, y2], color=BRD, lw=LW, zorder=2)
    if card1:
        ax.text(x1+(x2-x1)*0.1, y1+(y2-y1)*0.1, card1,
                fontsize=8, ha='center', va='center',
                bbox=dict(fc='white', ec='none', pad=1))
    if card2:
        ax.text(x1+(x2-x1)*0.9, y1+(y2-y1)*0.9, card2,
                fontsize=8, ha='center', va='center',
                bbox=dict(fc='white', ec='none', pad=1))

# ─── 图4-7a  核心药品/帖子关系 ────────────────────────────
def gen_er_a():
    """
    用户 — 拥有 — 家庭药箱 — 关联 — 全局标准药库
    用户 — 发布 — 共享帖子 — 绑定 — 家庭药箱
    共享帖子 — 产生 — 采纳记录 — 归属 — 用户
    """
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(0, 13); ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    EW, EH = 2.2, 0.7
    RW, RH = 1.4, 0.6

    # 实体
    entities = {
        'user':      (5.0, 5.8, '用户\n(User)'),
        'familymed': (5.0, 3.6, '家庭药箱\n(FamilyMedicine)'),
        'globalmed': (0.5, 3.6, '全局标准药库\n(GlobalMedicine)'),
        'post':      (9.5, 3.6, '共享帖子\n(SharePost)'),
        'adoption':  (5.0, 1.4, '药品采纳记录\n(Adoption)'),
    }
    ecx = {}   # 实体中心x
    ecy = {}   # 实体中心y
    for k, (x, y, txt) in entities.items():
        draw_rect(ax, x, y, EW, EH, txt, fontsize=8.5, bold=True)
        ecx[k] = x + EW/2
        ecy[k] = y + EH/2

    # 关系菱形
    rels = {
        'own':    (5.0, 4.85, '拥有(1:N)'),
        'ref':    (2.6, 3.95, '关联(N:1)'),
        'pub':    (7.8, 5.1,  '发布(1:N)'),
        'bind':   (7.8, 3.95, '绑定(1:1)'),
        'adopt':  (5.0, 2.5,  '产生(1:N)'),
        'belong': (7.8, 2.0,  '归属(N:1)'),
    }
    rcx = {}; rcy = {}
    for k, (x, y, txt) in rels.items():
        draw_diamond(ax, x, y, RW, RH, txt, fontsize=7.5)
        rcx[k] = x + RW/2
        rcy[k] = y + RH/2

    # 连线（实体 <-> 关系菱形）
    def link(e, r, card_e='', card_r=''):
        er_line(ax, ecx[e], ecy[e], rcx[r], rcy[r], card_e, card_r)

    link('user',      'own')
    link('familymed', 'own')
    link('familymed', 'ref')
    link('globalmed', 'ref')
    link('user',      'pub')
    link('post',      'pub')
    link('post',      'bind')
    link('familymed', 'bind')
    link('post',      'adopt')
    link('adoption',  'adopt')
    link('user',      'belong')
    link('adoption',  'belong')

    ax.set_title('图 4-7a  E-R 图（核心药品与帖子关系）',
                 fontsize=10, fontweight='bold', pad=6)
    return save(fig, 'fig4-7a_er_core.png')


# ─── 图4-7b  用户/消息/通知/家庭组申请关系 ─────────────────
def gen_er_b():
    """
    用户 — 发送 — 私信消息
    用户 — 提交 — 家庭组加入申请
    系统管理员(User) — 发布 — 系统公告
    系统管理员(User) — 发布 — 医学小贴士
    """
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(0, 13); ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    EW, EH = 2.4, 0.7
    RW, RH = 1.6, 0.6

    entities = {
        'user':     (5.0, 5.8, '用户\n(User)'),
        'privmsg':  (0.5, 3.5, '私信消息\n(PrivateMessage)'),
        'joinreq':  (0.5, 1.5, '家庭组加入申请\n(FamilyJoinRequest)'),
        'announce': (9.5, 3.5, '系统公告\n(SystemAnnouncement)'),
        'medtip':   (9.5, 1.5, '医学小贴士\n(MedicalTip)'),
        'admin':    (5.0, 1.5, '系统管理员\n(User子角色)'),
    }
    ecx = {}; ecy = {}
    for k, (x, y, txt) in entities.items():
        draw_rect(ax, x, y, EW, EH, txt, fontsize=8.5, bold=True)
        ecx[k] = x + EW/2
        ecy[k] = y + EH/2

    rels = {
        'send':    (2.8, 4.1,  '发送(1:N)'),
        'submit':  (2.8, 2.1,  '提交(1:N)'),
        'pub_ann': (8.0, 4.1,  '发布(1:N)'),
        'pub_tip': (8.0, 2.1,  '发布(1:N)'),
    }
    rcx = {}; rcy = {}
    for k, (x, y, txt) in rels.items():
        draw_diamond(ax, x, y, RW, RH, txt, fontsize=7.5)
        rcx[k] = x + RW/2
        rcy[k] = y + RH/2

    def link(e, r):
        er_line(ax, ecx[e], ecy[e], rcx[r], rcy[r])

    link('user',    'send')
    link('privmsg', 'send')
    link('user',    'submit')
    link('joinreq', 'submit')
    link('admin',   'pub_ann')
    link('announce','pub_ann')
    link('admin',   'pub_tip')
    link('medtip',  'pub_tip')

    # user -> admin 虚线（管理员是用户子角色）
    ax.annotate('', xy=(ecx['admin'], ecy['admin']+EH/2),
                xytext=(ecx['user'], ecy['user']-EH/2),
                arrowprops=dict(arrowstyle='->', color=BRD, lw=LW,
                                linestyle='dashed'))
    ax.text((ecx['user']+ecx['admin'])/2 + 0.2, (ecy['user']+ecy['admin'])/2,
            '角色继承', fontsize=8, ha='left')

    ax.set_title('图 4-7b  E-R 图（用户/消息/通知/家庭组申请关系）',
                 fontsize=10, fontweight='bold', pad=6)
    return save(fig, 'fig4-7b_er_msg.png')


# ══════════════════════════════════════════════════════════
# 执行
# ══════════════════════════════════════════════════════════
sys.stdout.buffer.write('开始生成黑白图表...\n'.encode('utf-8','replace'))
gen_module_tree()
gen_family_flow()
gen_medicine_flow()
gen_post_flow()
gen_notify_flow()
gen_er_a()
gen_er_b()
sys.stdout.buffer.write('全部完成！\n'.encode('utf-8','replace'))

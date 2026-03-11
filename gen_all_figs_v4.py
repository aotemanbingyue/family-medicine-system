# -*- coding: utf-8 -*-
"""
v4: 所有图片去掉 set_title（图内不含标题），图题由Word负责
    ER图完全重新布局：实体和菱形固定坐标，连线用正交折线，不交叉
"""
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['font.family'] = ['Microsoft YaHei', 'SimHei', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os, sys

OUT = r'd:\SoftWare\Code\bysj\diagrams'
os.makedirs(OUT, exist_ok=True)

def log(s): sys.stdout.buffer.write((s+'\n').encode('utf-8','replace'))

def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    log(f'  OK: {name}')

BRD = 'black'; LW = 1.2

# ──────────────────────────────────────────────────────────
# 基础绘图工具
# ──────────────────────────────────────────────────────────
def draw_rect(ax, x, y, w, h, line1='', line2='', fs=10, bold=False, lw=LW):
    ax.add_patch(mpatches.FancyBboxPatch((x,y),w,h,
        boxstyle='square,pad=0', fc='white', ec='black', lw=lw, zorder=3))
    if line2:
        ax.text(x+w/2, y+h*0.64, line1, ha='center', va='center',
                fontsize=fs, fontweight='bold' if bold else 'normal', zorder=4)
        ax.text(x+w/2, y+h*0.28, line2, ha='center', va='center',
                fontsize=fs-1.5, color='#444', zorder=4)
    elif line1:
        ax.text(x+w/2, y+h/2, line1, ha='center', va='center',
                fontsize=fs, fontweight='bold' if bold else 'normal',
                linespacing=1.5, zorder=4)

def draw_diamond(ax, x, y, w, h, text, fs=8.5):
    cx, cy = x+w/2, y+h/2
    ax.add_patch(plt.Polygon([[cx,y+h],[x+w,cy],[cx,y],[x,cy]],
        closed=True, fc='white', ec='black', lw=LW, zorder=3))
    ax.text(cx, cy, text, ha='center', va='center',
            fontsize=fs, linespacing=1.35, zorder=4)

def draw_oval(ax, x, y, w, h, text, fs=9):
    ax.add_patch(mpatches.Ellipse((x+w/2, y+h/2), w, h,
        fc='white', ec='black', lw=LW, zorder=3))
    ax.text(x+w/2, y+h/2, text, ha='center', va='center', fontsize=fs, zorder=4)

def arr_v(ax, x, y1, y2):   # 向下箭头
    ax.annotate('', xy=(x,y2), xytext=(x,y1),
                arrowprops=dict(arrowstyle='->', color='black', lw=LW))

def arr_bidir_v(ax, x, y1, y2):
    ax.annotate('', xy=(x,y2), xytext=(x,y1),
                arrowprops=dict(arrowstyle='<->', color='black', lw=LW))

def seg(ax, x1,y1,x2,y2):  # 直线段
    ax.plot([x1,x2],[y1,y2], color='black', lw=LW, zorder=2)

def lbl(ax, x, y, text, fs=8.5, ha='left'):
    ax.text(x, y, text, fontsize=fs, color='#333', ha=ha, va='center',
            bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none'))

# ══════════════════════════════════════════════════════════
# 图4-1  系统总体架构图
# ══════════════════════════════════════════════════════════
def gen_arch():
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.set_xlim(0, 11); ax.set_ylim(0, 8.5); ax.axis('off')

    # 层标签 x
    LX = 0.08

    # ── 用户层
    draw_rect(ax, 1.5,7.1, 8.8,0.95, '浏览器 / 客户端', 'PC  ·  平板  ·  手机', fs=11, bold=True, lw=1.8)
    ax.text(LX, 7.58, '用户层', fontsize=9, color='#555',
            bbox=dict(boxstyle='round,pad=0.25', fc='#f5f5f5', ec='#aaa', lw=0.8))

    # ── 箭头 + 协议标注（箭头在左，标注在右）
    arr_bidir_v(ax, 4.0, 7.1, 6.22)
    lbl(ax, 4.2, 6.66, 'HTTP / HTTPS')

    # ── 前端展示层
    draw_rect(ax, 1.5,5.55, 8.8,1.0, '前端展示层',
              'Bootstrap 5  ·  HTML5  ·  CSS3  ·  JavaScript', fs=11, bold=True, lw=1.8)
    ax.text(LX, 6.05, '前端展示层', fontsize=9, color='#555',
            bbox=dict(boxstyle='round,pad=0.25', fc='#f5f5f5', ec='#aaa', lw=0.8))

    arr_bidir_v(ax, 4.0, 5.55, 4.62)
    lbl(ax, 4.2, 5.08, 'Django  Request / Response')

    # ── Django MVT 大框
    draw_rect(ax, 1.5,1.55, 8.8,3.4, lw=2.0)
    ax.text(5.9, 4.73, 'Django MVT 框架层', ha='center', va='center',
            fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='black', lw=1.2))
    ax.text(LX, 3.25, 'Django\n框架层', fontsize=9, color='#555', va='center',
            bbox=dict(boxstyle='round,pad=0.25', fc='#f5f5f5', ec='#aaa', lw=0.8))

    SW, SH, SY = 2.35, 2.55, 1.75
    SX = [1.65, 4.23, 6.81]
    subs = [
        ('Model 层\n（模型层）',    'Django ORM\nMySQL 数据映射\n实体关系定义'),
        ('View 层\n（视图层）',     '业务逻辑处理\nRBAC 权限校验\n多级审批流转'),
        ('Template 层\n（模板层）', 'HTML 页面渲染\n角色菜单动态显示\n上下文数据注入'),
    ]
    for sx, (t, d) in zip(SX, subs):
        draw_rect(ax, sx, SY, SW, SH, t, d, fs=9.5, lw=1.0)
    for i in range(2):
        xm = SX[i]+SW
        ax.annotate('', xy=(xm+0.35, SY+SH/2), xytext=(xm, SY+SH/2),
                    arrowprops=dict(arrowstyle='<->', color='black', lw=1.0))

    arr_bidir_v(ax, 4.0, 1.55, 1.42)
    lbl(ax, 4.2, 1.48, 'Django ORM / SQL')

    # ── 数据存储层
    draw_rect(ax, 1.5,0.3, 8.8,1.0, '数据存储层',
              'MySQL 关系型数据库  ·  9 张核心业务表', fs=11, bold=True, lw=1.8)
    ax.text(LX, 0.80, '数据存储层', fontsize=9, color='#555',
            bbox=dict(boxstyle='round,pad=0.25', fc='#f5f5f5', ec='#aaa', lw=0.8))

    fig.tight_layout(pad=0.5)
    save(fig, 'fig4-1_arch.png')

# ══════════════════════════════════════════════════════════
# 图4-2  系统功能模块图
# ══════════════════════════════════════════════════════════
def gen_module_tree():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14); ax.set_ylim(0, 8); ax.axis('off')

    # 根节点
    draw_rect(ax, 5.2,6.8, 3.6,0.75, '家庭药品管理和共享平台', fs=10, bold=True, lw=1.8)
    root_cx = 5.2+3.6/2   # 7.0

    m1 = [
        (0.3,  4.9, 2.0, 0.7, '家庭组模块'),
        (3.0,  4.9, 2.2, 0.7, '药品管理模块'),
        (5.8,  4.9, 2.0, 0.7, '帖子模块'),
        (8.4,  4.9, 2.2, 0.7, '系统通知模块'),
        (11.0, 4.9, 2.2, 0.7, '系统管理模块'),
    ]
    mcx = [mx+mw/2 for mx,_,mw,_,_ in m1]

    for mx,my,mw,mh,mt in m1:
        draw_rect(ax, mx, my, mw, mh, mt, fs=9.5, bold=False, lw=1.2)

    # 根→各模块连线（直角：垂直→水平汇聚线→垂直）
    mid_y = 5.9
    seg(ax, root_cx, 6.8, root_cx, mid_y)
    seg(ax, mcx[0], mid_y, mcx[-1], mid_y)
    for cx in mcx:
        seg(ax, cx, mid_y, cx, 4.9+0.7)

    # 二级功能（每列子框）
    subs_all = [
        ['用户注册/登录成组', '家庭药品库\n添加删除药品', '用户管理员\n查询用户信息', '设立用户信箱'],
        ['用户查询\n全局药品库', '药品管理员\n审核申请', '药品管理员\n管理全局药品库'],
        ['用户发布/删除\n修改引用帖子', '用户帖子内\n申请入库药品', '帖子管理员\n审核帖子'],
        ['药品过期\n服用提醒', '系统公告\n消息推送', '系统管理员\n管理系统'],
        ['添加各类管理员', '权限管理'],
    ]

    SW = 0.52
    for col, (items, (mx,my,mw,mh,_)) in enumerate(zip(subs_all, m1)):
        n = len(items)
        total_w = n*SW + (n-1)*0.16
        sx0 = mx+mw/2 - total_w/2
        sub_top = my - 0.3
        seg(ax, sx0+SW/2, my, sx0+(n-1)*(SW+0.16)+SW/2, my)
        seg(ax, mx+mw/2, my, mx+mw/2, sub_top)
        for j, stxt in enumerate(items):
            sx = sx0 + j*(SW+0.16)
            lines = stxt.count('\n') + 1
            sh = lines*0.42 + 0.1
            sy = sub_top - sh
            draw_rect(ax, sx, sy, SW, sh, stxt, fs=7.0, lw=0.9)
            seg(ax, sx+SW/2, sub_top, sx+SW/2, sy+sh)

    fig.tight_layout(pad=0.5)
    save(fig, 'fig4-2_module_tree.png')

# ══════════════════════════════════════════════════════════
# 通用竖向流程图（无图内标题）
# ══════════════════════════════════════════════════════════
def gen_flow(steps, figname, fig_w=5.5):
    BW = 3.2; RH = 0.62; DH = 0.85; OH = 0.55; GAP = 0.32
    PAD = (fig_w-BW)/2

    total_h = 0.8
    for _,shape in steps:
        total_h += (DH if shape=='diamond' else OH if shape=='oval' else RH) + GAP

    fig, ax = plt.subplots(figsize=(fig_w, total_h))
    ax.set_xlim(0,fig_w); ax.set_ylim(0,total_h); ax.axis('off')

    y = total_h - 0.5
    cx = fig_w/2
    for i,(txt,shape) in enumerate(steps):
        bh = DH if shape=='diamond' else OH if shape=='oval' else RH
        by = y - bh
        if shape=='oval':    draw_oval(ax, PAD, by, BW, bh, txt)
        elif shape=='diamond': draw_diamond(ax, PAD, by, BW, bh, txt)
        else:                draw_rect(ax, PAD, by, BW, bh, txt, fs=9)
        if i < len(steps)-1:
            arr_v(ax, cx, by, by-GAP)
        y = by - GAP

    fig.tight_layout(pad=0.3)
    save(fig, figname)

# ══════════════════════════════════════════════════════════
# 图4-5  帖子双审核流程图（改为竖向版，风格与图4-6一致）
# ══════════════════════════════════════════════════════════
def gen_post_flow():
    steps = [
        ('开始', 'oval'),
        ('用户填写帖子并选择绑定药品记录', 'rect'),
        ('提交发布（进入待帖子审核队列）', 'rect'),
        ('帖子管理员审核内容是否合规', 'diamond'),
        ('是否通过帖子审核？', 'diamond'),
        ('进入待药品审核，通知药品管理员', 'rect'),
        ('药品管理员审核药品信息是否真实', 'diamond'),
        ('是否通过药品审核？', 'diamond'),
        ('帖子公开展示于共享广场', 'rect'),
        ('其他用户在帖子中一键采纳药品入箱', 'rect'),
        ('结束', 'oval'),
    ]
    gen_flow(steps, 'fig4-5_post_flow.png', fig_w=5.5)

# ══════════════════════════════════════════════════════════
# ER 图工具：正交折线连接，彻底避免交叉
# ══════════════════════════════════════════════════════════
def er_entity(ax, cx, cy, w, h, name, eng='', fs=9.5):
    """以中心坐标画实体框"""
    x, y = cx-w/2, cy-h/2
    draw_rect(ax, x, y, w, h, '', lw=1.5)
    if eng:
        ax.text(cx, cy+h*0.15, name, ha='center', va='center',
                fontsize=fs, fontweight='bold', zorder=4)
        ax.text(cx, cy-h*0.22, f'({eng})', ha='center', va='center',
                fontsize=fs-1.5, color='#444', zorder=4)
    else:
        ax.text(cx, cy, name, ha='center', va='center',
                fontsize=fs, fontweight='bold', zorder=4)

def er_diamond(ax, cx, cy, w, h, text, fs=8.5):
    """以中心坐标画关系菱形"""
    draw_diamond(ax, cx-w/2, cy-h/2, w, h, text, fs=fs)

def ortho(ax, p1, p2, via=None):
    """
    正交折线连接 p1→p2，via 指定中间转折点（可选）
    p1, p2, via 都是 (x, y) 元组
    """
    if via:
        seg(ax, p1[0], p1[1], via[0], via[1])
        seg(ax, via[0], via[1], p2[0], p2[1])
    else:
        seg(ax, p1[0], p1[1], p2[0], p1[1])
        seg(ax, p2[0], p1[1], p2[0], p2[1])

def card_lbl(ax, x, y, text, fs=8):
    ax.text(x, y, text, fontsize=fs, ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none'), zorder=5)

# ══════════════════════════════════════════════════════════
# 图4-7a  核心药品/帖子关系 ER图
#
# 布局（网格坐标，单位cm）：
#
#         [用户]            col=6.5  row=8
#         /     \
#    [拥有1:N] [发布1:N]   col=4/9  row=6.5
#         |         |
#   [家庭药箱]  [共享帖子]  col=4/9  row=5
#       |    \----[绑定1:1]----/
#  [关联N:1]
#       |
#  [全局药库]              col=1.5  row=5
#
#  [家庭药箱]-[产生1:N]-[采纳记录]  col=4/7  row=2.5
#  [用户]----[归属N:1]--[采纳记录]
# ══════════════════════════════════════════════════════════
def gen_er_a():
    """图4-7a：核心药品/帖子关系 ER 图（严格按 1:N / M:N 规范建模）"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    EW, EH = 2.4, 0.8
    DW, DH = 1.7, 0.75

    # 实体布局：上中是 User，第二行左右是 FamilyMedicine / SharePost，
    # 左下是 GlobalMedicine，右下是 SharePostMedicineAdoption。
    E = {
        'user':   (6.0, 7.0),
        'fmed':   (3.0, 4.8),
        'post':   (9.0, 4.8),
        'gmed':   (1.5, 2.4),
        'adopt':  (6.0, 2.4),
    }

    R = {
        'u_fm':   (4.5, 6.0),   # User 1:N FamilyMedicine
        'u_sp':   (7.5, 6.0),   # User 1:N SharePost
        'gm_fm':  (2.2, 3.4),   # GlobalMedicine 1:N FamilyMedicine
        'fm_sp':  (6.0, 4.0),   # FamilyMedicine 1:N SharePost
        'u_adopt':(4.5, 3.2),   # User 1:N Adoption
        'sp_adpt':(7.5, 3.2),   # SharePost 1:N Adoption
        'fm_adpt':(6.0, 1.6),   # FamilyMedicine 1:N Adoption
    }

    # 实体
    er_entity(ax, *E['user'],  EW, EH, '用户',       'User')
    er_entity(ax, *E['fmed'],  EW, EH, '家庭药箱',   'FamilyMedicine')
    er_entity(ax, *E['post'],  EW, EH, '共享帖子',   'SharePost')
    er_entity(ax, *E['gmed'],  EW, EH, '全局标准药库', 'GlobalMedicine')
    er_entity(ax, *E['adopt'], EW, EH, '帖子药品采纳记录', 'SharePostMedicineAdoption')

    # 关系菱形（全部标注 1:N 含义）
    er_diamond(ax, *R['u_fm'],   DW, DH, '拥有\n1 : N')
    er_diamond(ax, *R['u_sp'],   DW, DH, '发布\n1 : N')
    er_diamond(ax, *R['gm_fm'],  DW, DH, '实例化\n1 : N')
    er_diamond(ax, *R['fm_sp'],  DW, DH, '引用药品记录\n1 : N')
    er_diamond(ax, *R['u_adopt'],DW, DH, '作为采纳人\n1 : N')
    er_diamond(ax, *R['sp_adpt'],DW, DH, '来源帖子\n1 : N')
    er_diamond(ax, *R['fm_adpt'],DW, DH, '目标家庭药箱记录\n1 : N')

    # 连线：全部为简短直线 / 折线，避免回绕
    # User -[拥有]-> FamilyMedicine
    seg(ax, E['user'][0]-EW/4, E['user'][1]-EH/2, R['u_fm'][0], R['u_fm'][1]+DH/2)
    seg(ax, E['fmed'][0],      E['fmed'][1]+EH/2, R['u_fm'][0], R['u_fm'][1]-DH/2)

    # User -[发布]-> SharePost
    seg(ax, E['user'][0]+EW/4, E['user'][1]-EH/2, R['u_sp'][0], R['u_sp'][1]+DH/2)
    seg(ax, E['post'][0],      E['post'][1]+EH/2, R['u_sp'][0], R['u_sp'][1]-DH/2)

    # GlobalMedicine -[实例化]-> FamilyMedicine
    seg(ax, E['gmed'][0]+EW/2, E['gmed'][1]+EH/2, R['gm_fm'][0]-DW/2, R['gm_fm'][1])
    seg(ax, E['fmed'][0]-EW/2, E['fmed'][1],      R['gm_fm'][0]+DW/2, R['gm_fm'][1])

    # FamilyMedicine -[引用药品记录]-> SharePost
    seg(ax, E['fmed'][0]+EW/2, E['fmed'][1]-EH/4, R['fm_sp'][0]-DW/2, R['fm_sp'][1])
    seg(ax, E['post'][0]-EW/2, E['post'][1]-EH/4, R['fm_sp'][0]+DW/2, R['fm_sp'][1])

    # User -[作为采纳人]-> Adoption
    seg(ax, E['user'][0]-EW/2, E['user'][1]-EH/2, R['u_adopt'][0], R['u_adopt'][1]+DH/2)
    seg(ax, E['adopt'][0]-EW/2, E['adopt'][1]+EH/2, R['u_adopt'][0], R['u_adopt'][1]-DH/2)

    # SharePost -[来源帖子]-> Adoption
    seg(ax, E['post'][0]+EW/2,  E['post'][1]-EH/2, R['sp_adpt'][0], R['sp_adpt'][1]+DH/2)
    seg(ax, E['adopt'][0]+EW/2, E['adopt'][1]+EH/2, R['sp_adpt'][0], R['sp_adpt'][1]-DH/2)

    # FamilyMedicine -[目标家庭药箱记录]-> Adoption
    seg(ax, E['fmed'][0],       E['fmed'][1]-EH/2, R['fm_adpt'][0], R['fm_adpt'][1]+DH/2)
    seg(ax, E['adopt'][0],      E['adopt'][1]-EH/2, R['fm_adpt'][0], R['fm_adpt'][1]-DH/2)

    fig.tight_layout(pad=0.5)
    save(fig, 'fig4-7a_er_core.png')


# ══════════════════════════════════════════════════════════
# 图4-7b  用户/消息/通知/家庭组申请 ER图
#
# 布局：
#            [用户]               col=6  row=8
#           /  |  \
#     [发送]   |   [发布公告]
#       |  [继承↓]     |
#  [私信]   [管理员]  [公告]
#             |
#          [发布贴士]   [提交]
#             |            |
#          [贴士]       [申请]
# ══════════════════════════════════════════════════════════
def gen_er_b():
    """图4-7b：用户 / 消息 / 通知 / 加入申请 ER 图（严格基于给定实体）"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    EW, EH = 2.4, 0.8
    DW, DH = 1.7, 0.75

    # 左：User，第二行：私信 / 加入申请，右：公告 / 小贴士
    E = {
        'user':    (2.0, 6.8),
        'pmsg':    (2.0, 4.5),
        'join':    (2.0, 2.5),
        'ann':     (9.5, 6.2),
        'mtip':    (9.5, 3.5),
    }

    R = {
        'send':    (4.0, 5.6),   # User 1:N PrivateMessage (sender)
        'recv':    (4.0, 4.0),   # User 1:N PrivateMessage (receiver)
        'apply':   (4.0, 2.9),   # User 1:N FamilyJoinRequest
        'pub_ann': (7.5, 6.2),   # User(管理员) 1:N SystemAnnouncement
        'pub_tip': (7.5, 3.5),   # User(管理员) 1:N MedicalTip
    }

    # 实体
    er_entity(ax, *E['user'], EW, EH, '用户', 'User')
    er_entity(ax, *E['pmsg'], EW, EH, '私信消息', 'PrivateMessage')
    er_entity(ax, *E['join'], EW, EH, '家庭组加入申请', 'FamilyJoinRequest')
    er_entity(ax, *E['ann'],  EW, EH, '系统公告', 'SystemAnnouncement')
    er_entity(ax, *E['mtip'], EW, EH, '医学小贴士', 'MedicalTip')

    # 关系
    er_diamond(ax, *R['send'],    DW, DH, '作为发送方\n1 : N')
    er_diamond(ax, *R['recv'],    DW, DH, '作为接收方\n1 : N')
    er_diamond(ax, *R['apply'],   DW, DH, '提交申请\n1 : N')
    er_diamond(ax, *R['pub_ann'], DW, DH, '发布公告\n1 : N')
    er_diamond(ax, *R['pub_tip'], DW, DH, '发布贴士\n1 : N')

    # 连线：采用短直线 + 少量折线
    # User -> send -> PrivateMessage
    seg(ax, E['user'][0]+EW/2, E['user'][1]-EH/4, R['send'][0]-DW/2, R['send'][1]+DH/2)
    seg(ax, E['pmsg'][0]+EW/2, E['pmsg'][1]+EH/2, R['send'][0]-DW/2, R['send'][1]-DH/2)

    # User -> recv -> PrivateMessage
    seg(ax, E['user'][0]+EW/2, E['user'][1]-EH/2, R['recv'][0]-DW/2, R['recv'][1]+DH/2)
    seg(ax, E['pmsg'][0]+EW/2, E['pmsg'][1]+EH/4, R['recv'][0]-DW/2, R['recv'][1]-DH/2)

    # User -> apply -> FamilyJoinRequest
    seg(ax, E['user'][0]+EW/2, E['user'][1]-EH/2-0.2, R['apply'][0]-DW/2, R['apply'][1]+DH/2)
    seg(ax, E['join'][0]+EW/2, E['join'][1]+EH/2,    R['apply'][0]-DW/2, R['apply'][1]-DH/2)

    # User(管理员) -> pub_ann -> SystemAnnouncement
    seg(ax, E['user'][0]+EW/2+0.2, E['user'][1]-EH/6, R['pub_ann'][0]-DW/2, R['pub_ann'][1]+DH/2)
    seg(ax, E['ann'][0]-EW/2,      E['ann'][1],      R['pub_ann'][0]+DW/2, R['pub_ann'][1]-DH/2)

    # User(管理员) -> pub_tip -> MedicalTip
    seg(ax, E['user'][0]+EW/2+0.2, E['user'][1]-EH/1.5, R['pub_tip'][0]-DW/2, R['pub_tip'][1]+DH/2)
    seg(ax, E['mtip'][0]-EW/2,     E['mtip'][1],       R['pub_tip'][0]+DW/2, R['pub_tip'][1]-DH/2)

    fig.tight_layout(pad=0.5)
    save(fig, 'fig4-7b_er_msg.png')


# ══════════════════════════════════════════════════════════
# 执行
# ══════════════════════════════════════════════════════════
log('开始生成所有图片（v4，无图内标题）...')
gen_arch()
gen_module_tree()
gen_flow([
    ('开始','oval'),('用户填写注册信息','rect'),('账号激活，完成注册','rect'),
    ('用户登录系统','rect'),('选择：创建或申请加入家庭组','diamond'),
    ('创建家庭组\n（系统生成 family_id）','rect'),('提交加入申请\n（状态：待审核）','rect'),
    ('用户管理员审核申请','rect'),('审核通过，更新家庭组归属','rect'),
    ('进入家庭协作管理','rect'),('结束','oval'),
], 'fig4-3_family_flow.png')
gen_flow([
    ('开始','oval'),('用户在标准药库中检索药品','rect'),
    ('点击"添加至家庭药箱"','rect'),('系统创建药箱记录（状态：待审核）','rect'),
    ('药品管理员审核申请','rect'),('是否通过审核？','diamond'),
    ('状态变更为"已通过"，入库成功','rect'),('系统检测有效期（< 30天提醒）','rect'),
    ('用户设置服药提醒时间','rect'),('结束','oval'),
], 'fig4-4_medicine_flow.png')
gen_post_flow()
gen_flow([
    ('开始','oval'),('系统管理员发布公告 / 医学小贴士','rect'),
    ('消息推送至用户消息中心','rect'),('系统扫描药品有效期（< 30天）','rect'),
    ('生成过期提醒 / 服药提醒通知','rect'),('用户通过私信联系管理员','rect'),
    ('管理员在私聊收件箱回复','rect'),('用户消息中心统一展示全部通知','rect'),
    ('结束','oval'),
], 'fig4-6_notify_flow.png')
gen_er_a()
gen_er_b()
log('全部完成！')

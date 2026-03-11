# -*- coding: utf-8 -*-
"""
修复版：
  fig4-1  架构图：去掉图内标题，修复箭头/文字，层标签更清晰
  fig4-7a ER图：重新布局，连线不交叉
  fig4-7b ER图：重新布局，连线不交叉
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
BRD = 'black'; LW = 1.2

def log(s):
    sys.stdout.buffer.write((s+'\n').encode('utf-8','replace'))

def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    log(f'  生成: {p}')

# ─── 通用绘图工具 ──────────────────────────────────────────
def rect(ax, x, y, w, h, title, sub='', fs=10, bold=False, lw=LW, pad=0):
    r = mpatches.FancyBboxPatch((x,y), w, h,
        boxstyle='square,pad=0', fc='white', ec=BRD, lw=lw, zorder=3)
    ax.add_patch(r)
    if sub:
        ax.text(x+w/2, y+h*0.65, title, ha='center', va='center',
                fontsize=fs, color='black', fontweight='bold' if bold else 'normal', zorder=4)
        ax.text(x+w/2, y+h*0.28, sub, ha='center', va='center',
                fontsize=fs-1.5, color='#444', zorder=4, linespacing=1.5)
    else:
        ax.text(x+w/2, y+h/2, title, ha='center', va='center',
                fontsize=fs, color='black', fontweight='bold' if bold else 'normal',
                zorder=4, linespacing=1.5)

def diamond(ax, x, y, w, h, text, fs=8.5):
    cx, cy = x+w/2, y+h/2
    pts = [[cx,y+h],[x+w,cy],[cx,y],[x,cy]]
    ax.add_patch(plt.Polygon(pts, closed=True, fc='white', ec=BRD, lw=LW, zorder=3))
    ax.text(cx, cy, text, ha='center', va='center',
            fontsize=fs, color='black', zorder=4, linespacing=1.35)

def arrow_v(ax, x, y1, y2, label='', label_dx=0.15):
    ax.annotate('', xy=(x,y2), xytext=(x,y1),
                arrowprops=dict(arrowstyle='->', color=BRD, lw=LW))
    if label:
        ax.text(x+label_dx, (y1+y2)/2, label,
                va='center', fontsize=8, color='#444')

def arrow_bidir_v(ax, x, y1, y2):
    ax.annotate('', xy=(x,y2), xytext=(x,y1),
                arrowprops=dict(arrowstyle='<->', color=BRD, lw=LW))

def line(ax, x1,y1,x2,y2):
    ax.plot([x1,x2],[y1,y2], color=BRD, lw=LW, zorder=2)

def label_box(ax, x, y, text, fs=8):
    ax.text(x, y, text, ha='left', va='center', fontsize=fs, color='#555',
            bbox=dict(boxstyle='round,pad=0.25', fc='#f8f8f8', ec='#aaa', lw=0.8))

# ══════════════════════════════════════════════════════════
# 图 4-1  系统总体架构图（修复版）
#   - 不在图内写标题（title 放图下方由 Word 图题显示）
#   - 左侧层标签加宽，字号增大
#   - Django↔数据库的标注改为侧边文字，不压在箭头上
# ══════════════════════════════════════════════════════════
def gen_arch():
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.set_xlim(0, 11); ax.set_ylim(0, 8.5)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # 左侧层标签 x起点
    LBL_X = 0.05

    # ── 层1：用户层 ─────────────────────────
    rect(ax, 1.5, 7.1, 8.8, 0.95,
         '浏览器 / 客户端',
         'PC  ·  平板  ·  手机',
         fs=11, bold=True, lw=1.8)
    label_box(ax, LBL_X, 7.58, '用户层', fs=9)

    # 箭头 用户层↕前端层
    arrow_bidir_v(ax, 5.9, 7.1, 6.22)
    ax.text(6.1, 6.66, 'HTTP / HTTPS', va='center', fontsize=8.5, color='#333')

    # ── 层2：前端展示层 ──────────────────────
    rect(ax, 1.5, 5.55, 8.8, 1.0,
         '前端展示层',
         'Bootstrap 5  ·  HTML5  ·  CSS3  ·  JavaScript',
         fs=11, bold=True, lw=1.8)
    label_box(ax, LBL_X, 6.05, '前端展示层', fs=9)

    # 箭头 前端层↕Django层，标注放右侧
    arrow_bidir_v(ax, 5.9, 5.55, 4.62)
    ax.text(6.1, 5.08, 'Django Request / Response', va='center', fontsize=8.5, color='#333')

    # ── 层3：Django MVT 大框 ─────────────────
    rect(ax, 1.5, 1.55, 8.8, 3.4, '', lw=2.0)
    ax.text(5.9, 4.72, 'Django MVT 框架层', ha='center', va='center',
            fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=BRD, lw=1.2))
    label_box(ax, LBL_X, 3.25, 'Django\n框架层', fs=9)

    # 三个子框
    SW, SH = 2.35, 2.55
    SY = 1.75
    S_POSITIONS = [1.65, 4.23, 6.81]
    sub_data = [
        ('Model 层\n（模型层）',   'Django ORM\nMySQL 数据映射\n实体关系定义'),
        ('View 层\n（视图层）',    '业务逻辑处理\nRBAC 权限校验\n多级审批流转'),
        ('Template 层\n（模板层）','HTML 页面渲染\n角色菜单动态显示\n上下文数据注入'),
    ]
    for i, (sx, (title, desc)) in enumerate(zip(S_POSITIONS, sub_data)):
        rect(ax, sx, SY, SW, SH, title, desc, fs=9.5, lw=1.0)

    # 子框间双向箭头
    for i in range(2):
        x_mid = S_POSITIONS[i] + SW
        ax.annotate('', xy=(x_mid+0.35, SY+SH/2), xytext=(x_mid, SY+SH/2),
                    arrowprops=dict(arrowstyle='<->', color=BRD, lw=1.0))

    # 箭头 Django↕数据层，标注放右侧（不压箭头）
    arrow_bidir_v(ax, 5.9, 1.55, 1.42)
    ax.text(6.1, 1.48, 'Django ORM / SQL', va='center', fontsize=8.5, color='#333')

    # ── 层4：数据存储层 ──────────────────────
    rect(ax, 1.5, 0.3, 8.8, 1.0,
         '数据存储层',
         'MySQL 关系型数据库  ·  9 张核心业务表',
         fs=11, bold=True, lw=1.8)
    label_box(ax, LBL_X, 0.80, '数据存储层', fs=9)

    # 不加 suptitle，图题由 Word 统一处理
    fig.tight_layout(pad=0.5)
    save(fig, 'fig4-1_arch.png')


# ══════════════════════════════════════════════════════════
# ER 图通用连线工具（走 L 形折线，避免连线交叉）
# ══════════════════════════════════════════════════════════
def er_line_straight(ax, x1,y1,x2,y2, card='', card_side='mid'):
    """直线连接，card标注在中点旁"""
    ax.plot([x1,x2],[y1,y2], color=BRD, lw=LW, zorder=2)
    if card:
        mx,my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx+0.15, my+0.12, card, fontsize=8, color='black',
                ha='left', va='center',
                bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none'))

def er_entity(ax, x, y, w, h, name, eng='', fs=9.5):
    rect(ax, x, y, w, h, '', lw=1.5)
    if eng:
        ax.text(x+w/2, y+h*0.62, name, ha='center', va='center',
                fontsize=fs, fontweight='bold', zorder=4)
        ax.text(x+w/2, y+h*0.25, f'({eng})', ha='center', va='center',
                fontsize=fs-1.5, color='#333', zorder=4)
    else:
        ax.text(x+w/2, y+h/2, name, ha='center', va='center',
                fontsize=fs, fontweight='bold', zorder=4)

def er_rel(ax, x, y, w, h, verb, fs=8.5):
    diamond(ax, x, y, w, h, verb, fs=fs)


# ══════════════════════════════════════════════════════════
# 图 4-7a  核心药品/帖子关系（重新布局，连线不交叉）
#
#  布局设计（从上到下，左到右）：
#
#        [用户]
#       /       \
#  [拥有1:N]  [发布1:N]
#      |            |
#  [家庭药箱]  [共享帖子]
#      |    \   /
#  [关联N:1] [绑定1:1]
#      |
#  [全局药库]
#
#  [家庭药箱] --[产生1:N]--> [采纳记录]
#  [用户]      --[归属N:1]--> [采纳记录]
# ══════════════════════════════════════════════════════════
def gen_er_a():
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(0, 12); ax.set_ylim(0, 9)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    EW, EH = 2.4, 0.85   # 实体框
    RW, RH = 1.5, 0.75   # 关系菱形

    # ── 实体位置（左边缘x, 底边缘y）──────────────
    E = {
        'user':      (4.5,  7.6),   # 顶部居中
        'familymed': (4.5,  4.9),   # 中部居中
        'globalmed': (0.4,  4.9),   # 左中
        'post':      (8.8,  4.9),   # 右中
        'adoption':  (4.5,  1.5),   # 底部居中
    }
    # ── 关系节点位置 ──────────────────────────────
    R = {
        'own':    (2.8,  6.5),    # 用户→家庭药箱 左侧
        'pub':    (7.2,  6.5),    # 用户→帖子 右侧
        'ref':    (2.1,  5.2),    # 家庭药箱→全局药库
        'bind':   (7.2,  5.2),    # 帖子↔家庭药箱
        'adopt_r':(4.5,  3.0),    # 家庭药箱→采纳
        'belong': (7.2,  2.5),    # 帖子→采纳
    }

    def ec(k): return E[k][0]+EW/2, E[k][1]+EH/2
    def rc(k): return R[k][0]+RW/2, R[k][1]+RH/2

    # 画实体
    er_entity(ax, *E['user'],      EW, EH, '用户',       'User')
    er_entity(ax, *E['familymed'], EW, EH, '家庭药箱',   'FamilyMedicine')
    er_entity(ax, *E['globalmed'], EW, EH, '全局标准药库','GlobalMedicine')
    er_entity(ax, *E['post'],      EW, EH, '共享帖子',   'SharePost')
    er_entity(ax, *E['adoption'],  EW, EH, '药品采纳记录','Adoption')

    # 画关系菱形
    er_rel(ax, *R['own'],    RW, RH, '拥有\n(1:N)')
    er_rel(ax, *R['pub'],    RW, RH, '发布\n(1:N)')
    er_rel(ax, *R['ref'],    RW, RH, '关联\n(N:1)')
    er_rel(ax, *R['bind'],   RW, RH, '绑定\n(1:1)')
    er_rel(ax, *R['adopt_r'],RW, RH, '产生\n(1:N)')
    er_rel(ax, *R['belong'], RW, RH, '归属\n(N:1)')

    # 连线（实体边缘点 → 关系菱形边缘点）
    # 用户 → 拥有
    er_line_straight(ax, ec('user')[0]-EW*0.25,   ec('user')[1],
                         rc('own')[0],            rc('own')[1]+RH*0.4)
    # 家庭药箱 → 拥有
    er_line_straight(ax, ec('familymed')[0]-EW*0.15, ec('familymed')[1]+EH*0.35,
                         rc('own')[0]+RW*0.3,    rc('own')[1])

    # 用户 → 发布
    er_line_straight(ax, ec('user')[0]+EW*0.25,  ec('user')[1],
                         rc('pub')[0]+RW*0.3,    rc('pub')[1]+RH*0.4)
    # 帖子 → 发布
    er_line_straight(ax, ec('post')[0],          ec('post')[1]+EH*0.35,
                         rc('pub')[0]+RW,        rc('pub')[1])

    # 家庭药箱 → 关联
    er_line_straight(ax, ec('familymed')[0],     ec('familymed')[1],
                         rc('ref')[0]+RW,        rc('ref')[1]+RH*0.5)
    # 全局药库 → 关联
    er_line_straight(ax, ec('globalmed')[0]+EW,  ec('globalmed')[1]+EH*0.5,
                         rc('ref')[0],           rc('ref')[1]+RH*0.5)

    # 帖子 → 绑定
    er_line_straight(ax, ec('post')[0],          ec('post')[1],
                         rc('bind')[0]+RW,       rc('bind')[1]+RH*0.5)
    # 家庭药箱 → 绑定
    er_line_straight(ax, ec('familymed')[0]+EW,  ec('familymed')[1],
                         rc('bind')[0],          rc('bind')[1]+RH*0.5)

    # 家庭药箱 → 产生
    er_line_straight(ax, ec('familymed')[0]+EW*0.3, ec('familymed')[1]-EH*0.5+0.1,
                         rc('adopt_r')[0]+RW*0.3,   rc('adopt_r')[1]+RH*0.5)
    # 采纳记录 → 产生
    er_line_straight(ax, ec('adoption')[0]+EW*0.3,  ec('adoption')[1]+EH*0.5,
                         rc('adopt_r')[0]+RW*0.3,   rc('adopt_r')[1])

    # 帖子 → 归属（右侧垂直）
    er_line_straight(ax, ec('post')[0]+EW*0.3,   ec('post')[1]-EH*0.5+0.1,
                         rc('belong')[0]+RW*0.5,  rc('belong')[1]+RH*0.5)
    # 采纳记录 → 归属
    er_line_straight(ax, ec('adoption')[0]+EW*0.8, ec('adoption')[1]+EH*0.5,
                         rc('belong')[0]+RW*0.3,   rc('belong')[1])

    ax.set_title('', pad=0)   # 标题由 Word 图题显示
    fig.tight_layout(pad=0.5)
    save(fig, 'fig4-7a_er_core.png')


# ══════════════════════════════════════════════════════════
# 图 4-7b  用户/消息/通知/家庭组申请（重新布局，连线不交叉）
#
# 布局：
#       [用户]  (顶部)
#     /   |    \
#  [发送] │  [发布_ann]
#   |  [角色继承]  |
# [私信] [管理员] [公告]
#          |
#       [发布_tip]
#          |
#  [申请]  |  [小贴士]
#  [提交]--|
# ══════════════════════════════════════════════════════════
def gen_er_b():
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(0, 12); ax.set_ylim(0, 9)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    EW, EH = 2.5, 0.85
    RW, RH = 1.5, 0.75

    E = {
        'user':     (4.6,  7.5),
        'privmsg':  (0.3,  4.5),
        'admin':    (4.6,  4.5),
        'announce': (9.0,  5.8),
        'joinreq':  (0.3,  2.0),
        'medtip':   (9.0,  2.5),
    }
    R = {
        'send':     (2.0,  6.1),
        'inherit':  (5.2,  6.1),   # 角色继承（虚线，不是关系菱形）
        'pub_ann':  (7.5,  6.6),
        'submit':   (2.0,  3.2),
        'pub_tip':  (7.5,  3.8),
    }

    def ec(k): return E[k][0]+EW/2, E[k][1]+EH/2
    def rc(k): return R[k][0]+RW/2, R[k][1]+RH/2

    er_entity(ax, *E['user'],     EW, EH, '用户',     'User')
    er_entity(ax, *E['privmsg'],  EW, EH, '私信消息', 'PrivateMessage')
    er_entity(ax, *E['admin'],    EW, EH, '系统管理员','User 子角色')
    er_entity(ax, *E['announce'], EW, EH, '系统公告', 'SystemAnnouncement')
    er_entity(ax, *E['joinreq'],  EW, EH, '家庭组加入申请','FamilyJoinRequest')
    er_entity(ax, *E['medtip'],   EW, EH, '医学小贴士','MedicalTip')

    er_rel(ax, *R['send'],    RW, RH, '发送\n(1:N)')
    er_rel(ax, *R['pub_ann'], RW, RH, '发布\n(1:N)')
    er_rel(ax, *R['submit'],  RW, RH, '提交\n(1:N)')
    er_rel(ax, *R['pub_tip'], RW, RH, '发布\n(1:N)')

    # 用户 → 发送
    er_line_straight(ax, ec('user')[0]-EW*0.3, ec('user')[1],
                         rc('send')[0]+RW*0.4,  rc('send')[1]+RH*0.5)
    # 私信 → 发送
    er_line_straight(ax, ec('privmsg')[0]+EW*0.5, ec('privmsg')[1]+EH*0.5,
                         rc('send')[0]+RW*0.4,    rc('send')[1])

    # 用户 → 发布公告
    er_line_straight(ax, ec('user')[0]+EW*0.35,  ec('user')[1],
                         rc('pub_ann')[0]+RW*0.3, rc('pub_ann')[1]+RH*0.5)
    # 公告 → 发布公告
    er_line_straight(ax, ec('announce')[0],      ec('announce')[1],
                         rc('pub_ann')[0]+RW,    rc('pub_ann')[1]+RH*0.5)

    # 用户 →（虚线）→ 管理员（角色继承）
    ax.annotate('', xy=(ec('admin')[0], ec('admin')[1]+EH*0.4),
                xytext=(ec('user')[0], ec('user')[1]-EH*0.4),
                arrowprops=dict(arrowstyle='->', color=BRD, lw=LW,
                                linestyle='dashed', connectionstyle='arc3,rad=0'))
    ax.text(ec('user')[0]+0.18, (ec('user')[1]+ec('admin')[1])/2,
            '角色继承', fontsize=8.5, color='black')

    # 用户 → 提交申请（走到左边）
    ax.plot([ec('user')[0]-EW*0.5, rc('submit')[0]+RW*0.4],
            [ec('user')[1],        ec('user')[1]], color=BRD, lw=LW, zorder=2)
    ax.plot([rc('submit')[0]+RW*0.4, rc('submit')[0]+RW*0.4],
            [ec('user')[1],          rc('submit')[1]+RH*0.5], color=BRD, lw=LW, zorder=2)
    # 申请 → 提交
    er_line_straight(ax, ec('joinreq')[0]+EW*0.5, ec('joinreq')[1]+EH*0.5,
                         rc('submit')[0]+RW*0.4,   rc('submit')[1])

    # 管理员 → 发布小贴士
    er_line_straight(ax, ec('admin')[0]+EW*0.7, ec('admin')[1],
                         rc('pub_tip')[0],       rc('pub_tip')[1]+RH*0.5)
    # 小贴士 → 发布
    er_line_straight(ax, ec('medtip')[0],       ec('medtip')[1],
                         rc('pub_tip')[0]+RW,   rc('pub_tip')[1]+RH*0.5)

    fig.tight_layout(pad=0.5)
    save(fig, 'fig4-7b_er_msg.png')


# ══════════════════════════════════════════════════════════
log('开始生成...')
gen_arch()
gen_er_a()
gen_er_b()
log('全部完成！')

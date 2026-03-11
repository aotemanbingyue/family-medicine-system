# -*- coding: utf-8 -*-
"""
生成图4-1 系统总体架构图（黑白、分层矩形风格）
分层：
  浏览器层（用户端）
  前端展示层（Bootstrap 5 / HTML / CSS / JS）
  Web 服务层（Django MVT）
    Model层 | View层 | Template层
  数据存储层（MySQL）
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

BRD = 'black'
LW  = 1.2

def draw_rect(ax, x, y, w, h, text, sub='', fontsize=10, bold=False, fill='white', lw=LW):
    rect = mpatches.FancyBboxPatch((x, y), w, h,
        boxstyle='square,pad=0', fc=fill, ec=BRD, lw=lw, zorder=3)
    ax.add_patch(rect)
    if sub:
        ax.text(x+w/2, y+h*0.62, text, ha='center', va='center',
                fontsize=fontsize, color='black',
                fontweight='bold' if bold else 'normal', zorder=4)
        ax.text(x+w/2, y+h*0.28, sub, ha='center', va='center',
                fontsize=fontsize-1.5, color='#333', zorder=4)
    else:
        ax.text(x+w/2, y+h/2, text, ha='center', va='center',
                fontsize=fontsize, color='black',
                fontweight='bold' if bold else 'normal',
                linespacing=1.5, zorder=4)

def v_arrow(ax, x, y1, y2):
    ax.annotate('', xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle='<->', color=BRD, lw=LW))

fig, ax = plt.subplots(figsize=(11, 9))
ax.set_xlim(0, 11)
ax.set_ylim(0, 9)
ax.axis('off')
fig.patch.set_facecolor('white')

# ── 层标签（左侧竖排）──────────────────────────────
layer_labels = [
    (7.8, '用户层'),
    (6.4, '前端展示层'),
    (3.4, 'Django 框架层'),
    (1.0, '数据存储层'),
]
for ly, lt in layer_labels:
    ax.text(0.15, ly + 0.3, lt, ha='left', va='center',
            fontsize=8.5, color='#555',
            bbox=dict(boxstyle='round,pad=0.3', fc='#f5f5f5', ec='#aaa', lw=0.8))

# ── 1. 用户层 ───────────────────────────────────────
draw_rect(ax, 1.2, 7.6, 8.6, 1.0,
          '浏览器 / 客户端',
          'PC  ·  平板  ·  手机',
          fontsize=10, bold=True, lw=1.5)

# ── 双向箭头：用户层 ↕ 前端层 ──────────────────────
v_arrow(ax, 5.5, 7.6, 6.55)
ax.text(5.65, 7.1, 'HTTP/HTTPS', fontsize=8, color='#444')

# ── 2. 前端展示层 ────────────────────────────────────
draw_rect(ax, 1.2, 5.9, 8.6, 1.1,
          '前端展示层',
          'Bootstrap 5  ·  HTML5  ·  CSS3  ·  JavaScript',
          fontsize=10, bold=True, lw=1.5)

# ── 双向箭头：前端层 ↕ Django层 ───────────────────
v_arrow(ax, 5.5, 5.9, 4.85)
ax.text(5.65, 5.35, 'Django Request/Response', fontsize=8, color='#444')

# ── 3. Django MVT 框架层（大框+三个子框）──────────────
draw_rect(ax, 1.2, 1.8, 8.6, 3.5,
          '', fontsize=9, bold=False, lw=1.8)

# 大框标题
ax.text(5.5, 5.1, 'Django MVT 框架层', ha='center', va='center',
        fontsize=10, fontweight='bold', color='black',
        bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='black', lw=1.0))

# 三个子框
SUB_Y  = 2.2
SUB_H  = 2.6
SUB_W  = 2.3
GAP    = 0.35
sx0    = 1.55

sub_boxes = [
    (sx0,              'Model 层\n（模型层）',     'Django ORM\nMySQL 数据映射\n实体关系定义'),
    (sx0+SUB_W+GAP,    'View 层\n（视图层）',      '业务逻辑处理\nRBAC 权限校验\n多级审批流转'),
    (sx0+2*(SUB_W+GAP),'Template 层\n（模板层）', 'HTML 页面渲染\n角色菜单动态显示\n上下文数据注入'),
]

for bx, title, desc in sub_boxes:
    draw_rect(ax, bx, SUB_Y, SUB_W, SUB_H, title, desc, fontsize=9, bold=False, lw=1.0)

# 子框之间的双向箭头
for bx, _, _ in sub_boxes[:-1]:
    mid_x = bx + SUB_W
    ax.annotate('', xy=(mid_x+GAP, SUB_Y+SUB_H/2),
                xytext=(mid_x, SUB_Y+SUB_H/2),
                arrowprops=dict(arrowstyle='<->', color=BRD, lw=1.0))

# ── 双向箭头：Django层 ↕ 数据层 ──────────────────
v_arrow(ax, 5.5, 1.8, 1.75)
ax.text(5.65, 1.75, 'Django ORM / SQL', fontsize=8, color='#444')

# ── 4. 数据存储层 ─────────────────────────────────
draw_rect(ax, 1.2, 0.3, 8.6, 1.1,
          '数据存储层',
          'MySQL 关系型数据库  ·  9 张核心业务表',
          fontsize=10, bold=True, lw=1.5)

ax.set_title('图 4-1  系统总体架构图', fontsize=11, fontweight='bold', pad=10)

path = os.path.join(OUT, 'fig4-1_arch.png')
fig.savefig(path, dpi=180, bbox_inches='tight', facecolor='white')
plt.close(fig)
sys.stdout.buffer.write(f'生成: {path}\n'.encode('utf-8','replace'))

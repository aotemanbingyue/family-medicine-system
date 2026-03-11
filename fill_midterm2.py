# -*- coding: utf-8 -*-
"""
填写中期检查自查表 v2 —— 精准操作合并单元格
"""
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt
from lxml import etree
import sys, copy

doc = Document(r'd:\SoftWare\Code\bysj\midterm_check.docx')

def log(s): sys.stdout.buffer.write((s+'\n').encode('utf-8','replace'))

def set_cell_text(cell, text, fontsize=10.5, bold=False):
    """
    清除单元格所有段落并重新写入，支持 \\n 换行（每行新段落）
    """
    # 删掉单元格内除第一段外的其余段
    tc = cell._tc
    paras = tc.findall(qn('w:p'))
    for p in paras[1:]:
        tc.remove(p)
    # 清空第一段
    p0 = paras[0]
    for child in list(p0):
        p0.remove(child)

    lines = text.split('\n')
    for li, line in enumerate(lines):
        if li == 0:
            para_elem = p0
        else:
            # 新建段落
            para_elem = OxmlElement('w:p')
            tc.append(para_elem)

        # 段落属性：居左
        pPr = OxmlElement('w:pPr')
        jc = OxmlElement('w:jc')
        jc.set(qn('w:val'), 'left')
        pPr.append(jc)
        para_elem.append(pPr)

        r = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        # 字体
        rFonts = OxmlElement('w:rFonts')
        rFonts.set(qn('w:hint'), 'eastAsia')
        rFonts.set(qn('w:ascii'), '宋体')
        rFonts.set(qn('w:hAnsi'), '宋体')
        rFonts.set(qn('w:eastAsia'), '宋体')
        rPr.append(rFonts)
        # 字号
        sz = OxmlElement('w:sz')
        sz.set(qn('w:val'), str(int(fontsize * 2)))
        rPr.append(sz)
        szCs = OxmlElement('w:szCs')
        szCs.set(qn('w:val'), str(int(fontsize * 2)))
        rPr.append(szCs)
        if bold:
            b = OxmlElement('w:b')
            rPr.append(b)
        r.append(rPr)
        t = OxmlElement('w:t')
        t.text = line
        if line.startswith(' ') or line.endswith(' '):
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        r.append(t)
        para_elem.append(r)


tbl = doc.tables[0]
log(f'表格: {len(tbl.rows)}行 x {len(tbl.columns)}列')

# ── 第0行：基本信息 ──────────────────────────────────────
# [0,0]=学生姓名(标签)  [0,1]=填写姓名  [0,3]=专业名称(标签)  [0,4]=已有值
# 注意合并单元格，col[1]和col[2]可能是同一个tc
r0 = tbl.rows[0]
# 找唯一的tc
seen = set()
unique_cells = []
for c in r0.cells:
    if id(c._tc) not in seen:
        seen.add(id(c._tc))
        unique_cells.append(c)
log(f'第0行唯一格数: {len(unique_cells)}')
for ci, c in enumerate(unique_cells):
    log(f'  [{ci}] "{c.text.strip()}"')

# 填写学生姓名（第1格，即标签"学生姓名"后的格）
# unique_cells[0]=学生姓名(标签), [1]=值格, [2]=专业名称(标签), [3]=值格
if len(unique_cells) >= 4:
    set_cell_text(unique_cells[1], '（请填写您的姓名）')
    set_cell_text(unique_cells[3], '计算机科学与技术')

# ── 第1行：任务书 / 参考文献 ─────────────────────────────
r1 = tbl.rows[1]
seen = set(); uc1 = []
for c in r1.cells:
    if id(c._tc) not in seen:
        seen.add(id(c._tc)); uc1.append(c)
log(f'第1行唯一格: {len(uc1)}')
for ci, c in enumerate(uc1): log(f'  [{ci}] "{c.text.strip()[:40]}"')
# [0]=任务书(标签) [1]=任务书值 [2]=参考文献(标签) [3]=参考文献值
if len(uc1) >= 4:
    set_cell_text(uc1[1], '已完成（ √ ），进行中（  ）')
    set_cell_text(uc1[3], '15篇；其中外文文献  2  篇')

# ── 第2行：开题报告 ──────────────────────────────────────
r2 = tbl.rows[2]
seen = set(); uc2 = []
for c in r2.cells:
    if id(c._tc) not in seen:
        seen.add(id(c._tc)); uc2.append(c)
log(f'第2行唯一格: {len(uc2)}')
for ci, c in enumerate(uc2): log(f'  [{ci}] "{c.text.strip()[:40]}"')
if len(uc2) >= 2:
    set_cell_text(uc2[1], '已完成（ √ ），进行中（  ）；完成字数约：3500 字')

# ── 第3行：正文 ──────────────────────────────────────────
r3 = tbl.rows[3]
seen = set(); uc3 = []
for c in r3.cells:
    if id(c._tc) not in seen:
        seen.add(id(c._tc)); uc3.append(c)
log(f'第3行唯一格: {len(uc3)}')
for ci, c in enumerate(uc3): log(f'  [{ci}] "{c.text.strip()[:40]}"')
if len(uc3) >= 2:
    set_cell_text(uc3[1], '完成定稿（ √ ），进行中（  ）\n完成百分比：95%')

# ── 第4行：目前已完成任务 ────────────────────────────────
r4 = tbl.rows[4]
seen = set(); uc4 = []
for c in r4.cells:
    if id(c._tc) not in seen:
        seen.add(id(c._tc)); uc4.append(c)
if len(uc4) >= 2:
    set_cell_text(uc4[1],
        '1. 系统需求分析与可行性分析\n'
        '2. 系统总体架构与功能模块设计\n'
        '3. 数据库 E-R 图设计及9张核心数据表建模\n'
        '4. 基于 Django + Bootstrap 5 的前后端全功能开发\n'
        '5. 五大功能模块全部实现（家庭组管理、药品管理、社区帖子、系统通知、安全管控）\n'
        '6. 功能测试与性能测试\n'
        '7. 论文各章节撰写并完成初稿'
    )

# ── 第5行：尚须完成的任务 ────────────────────────────────
r5 = tbl.rows[5]
seen = set(); uc5 = []
for c in r5.cells:
    if id(c._tc) not in seen:
        seen.add(id(c._tc)); uc5.append(c)
if len(uc5) >= 2:
    set_cell_text(uc5[1],
        '1. 根据指导教师意见对论文内容进行修改完善\n'
        '2. 论文格式与排版最终校对\n'
        '3. 完成论文答辩准备（PPT 制作、答辩演练）'
    )

# ── 第6行：存在的问题 ────────────────────────────────────
r6 = tbl.rows[6]
seen = set(); uc6 = []
for c in r6.cells:
    if id(c._tc) not in seen:
        seen.add(id(c._tc)); uc6.append(c)
if len(uc6) >= 2:
    set_cell_text(uc6[1],
        '1. 系统目前运行于本地环境，尚未完成云端部署与高并发场景测试\n'
        '2. 部分前端页面 UI 交互细节有待优化\n'
        '3. 论文图表规范及引用格式仍需进一步校对'
    )

# ── 第7行：采取的办法 ────────────────────────────────────
r7 = tbl.rows[7]
seen = set(); uc7 = []
for c in r7.cells:
    if id(c._tc) not in seen:
        seen.add(id(c._tc)); uc7.append(c)
if len(uc7) >= 2:
    set_cell_text(uc7[1],
        '1. 功能验证完成后，参照 Django 官方文档完成服务器部署\n'
        '2. 积极与指导教师沟通，按反馈逐步修改完善论文\n'
        '3. 对照学院论文撰写规范认真校对格式与引用'
    )

doc.save(r'd:\SoftWare\Code\bysj\中期检查自查表_已填写.docx')
log('\n✓ 保存完成：中期检查自查表_已填写.docx')

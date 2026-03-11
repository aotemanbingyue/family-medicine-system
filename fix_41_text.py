# -*- coding: utf-8 -*-
"""
恢复被误删的4.1第一段正文，插入在4.1标题[146]之后
"""
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy, sys

doc = Document(r'c:\Users\28041\Desktop\初稿_新摘要.docx')

def log(s):
    sys.stdout.buffer.write((s+'\n').encode('utf-8','replace'))

TEXT_152 = (
    '本系统采用成熟的 B/S（Browser/Server）架构，用户通过浏览器发起请求，'
    '后端服务器负责业务处理与数据管理，实现客户端与服务器的职责分离。'
    '前端基于 Bootstrap 5 框架进行响应式页面设计，可自适应 PC、平板及手机等多终端访问，'
    '无需额外安装客户端软件。后端采用 Django 框架提供的 MVT（Model-View-Template）设计模式，'
    '将数据建模、业务逻辑与页面渲染三个职责明确分离，便于模块化开发与后期维护。'
    '系统总体架构如图 4-1 所示。'
)

# 在 [152]（现在的第二段正文"在MVT架构中..."）之前插入第一段
ref_para = doc.paragraphs[152]
ref_elem = ref_para._element
parent = ref_elem.getparent()
pos = list(parent).index(ref_elem)

# 构造新段落（复制第152段的格式）
new_p = OxmlElement('w:p')
ref_pPr = ref_elem.find(qn('w:pPr'))
if ref_pPr is not None:
    new_p.append(copy.deepcopy(ref_pPr))

# 清除加粗
pPr = new_p.find(qn('w:pPr'))
new_r = OxmlElement('w:r')
rPr = OxmlElement('w:rPr')
new_r.append(rPr)
t = OxmlElement('w:t')
t.text = TEXT_152
t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
new_r.append(t)
new_p.append(new_r)

parent.insert(pos, new_p)
log('  第一段正文已恢复插入')

doc.save(r'c:\Users\28041\Desktop\初稿_新摘要.docx')
log('保存完成')

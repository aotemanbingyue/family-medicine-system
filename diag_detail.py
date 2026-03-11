# -*- coding: utf-8 -*-
"""详细查看图5-3/5-4/5-6/5-7周围实际排列"""
from docx import Document
from docx.oxml.ns import qn
import sys

doc = Document(r'c:\Users\28041\Desktop\初稿_新摘要.docx')

def has_img(p):
    return p._element.find('.//' + qn('w:drawing')) is not None

body = doc.element.body
para_idx = 0
items = []
for child in body:
    if child.tag == qn('w:p'):
        p = doc.paragraphs[para_idx]
        t = p.text.strip()
        img = has_img(p)
        items.append(('img' if img else 'para', para_idx, t[:60], child))
        para_idx += 1
    elif child.tag == qn('w:tbl'):
        items.append(('table', None, '[TABLE]', child))

# 打印220-270范围
for i, (typ, pidx, txt, _) in enumerate(items):
    if pidx is not None and 220 <= pidx <= 275:
        sys.stdout.buffer.write(f'[body{i:3d}][para{pidx:3d}] {typ:5s}  {txt}\n'.encode('utf-8','replace'))
    elif pidx is None and 'TABLE' in txt:
        # 找附近段落
        pass

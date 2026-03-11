# -*- coding: utf-8 -*-
from docx import Document
from docx.oxml.ns import qn
import sys

orig = Document(r'c:\Users\28041\Desktop\初稿.docx')

def has_img(p):
    return p._element.find('.//' + qn('w:drawing')) is not None

def get_rids(p):
    rids = []
    for elem in p._element.iter():
        embed = elem.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
        if embed:
            rids.append(embed)
    return rids

for i, p in enumerate(orig.paragraphs):
    t = p.text.strip()
    img = has_img(p)
    if 325 <= i <= 420:
        tag = 'IMG' if img else '   '
        rids = get_rids(p) if img else []
        rid_str = f' [{",".join(rids)}]' if rids else ''
        sys.stdout.buffer.write(f'[{i}]{tag}{rid_str} {t[:60]}\n'.encode('utf-8','replace'))

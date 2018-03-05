# -*- coding:utf-8 -*-
"""解析字体文件"""
from fontTools.ttLib import TTFont
import requests
import re
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

list_font = [ ' ', '一', '七', '三', '上', '下', '不', '中', '档', '比', '油', '泥', '灯', '九', '了', '二', '五',
				'低', '保', '光', '八', '公', '六', '养', '内', '冷', '副', '加', '动', '十', '电', '的', '皮', '盘', '真', '着', '路', '身',
				'软', '过', '近', '远', '里', '量', '长', '门', '问', '只', '右', '启', '呢', '味', '和', '响', '四', '地', '坏', '坐', '外',
				'多', '大', '好', '孩', '实', '小', '少', '短', '矮', '硬', '空', '级', '耗', '雨', '音', '高', '左', '开', '当', '很', '得',
				'性', '自', '手', '排', '控', '无', '是', '更', '有', '机', '来' ]

class Font(object):

    def __init__(self, url):
        self.file_path = "font.ttf"
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        ttf = requests.get("http:" + url, stream=True)
        with open(self.file_path, "wb") as pdf:
            for chunk in ttf.iter_content(chunk_size=1024):
                if chunk:
                    pdf.write(chunk)

    # 创建 self.font 属性
    def get_glyph_id(self, glyph):
        ttf = TTFont(self.file_path)
        # gly_list = ttf.getGlyphOrder()  # 获取 GlyphOrder 字段的值
        index = ttf.getGlyphID(glyph)
        # os.remove(self.file_path)
        return index

    def get_font(self, glyph):
        id = self.get_glyph_id(glyph)
        return list_font[id]

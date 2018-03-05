# -*- coding:utf-8 -*-
"""对混淆的js代码破解,获取想要的内容"""
from bs4 import BeautifulSoup
import re
import PyV8
from document import Global
# from decode_fontfile import DecodeFontFile
from font import Font
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class ScriptDecoder(object):
    """传入口碑的所有内容, 返回正常文本信息"""

    def split(self, content):
        """传入口碑内容,返回拆分后的列表"""
        return str(content).split('【')[1:]

    def get_title_comment_js(self, content):
        """获取标题和混淆的js代码"""
        # 获取小标题
        title = content.split("】")[0]
        # 获取加密的文本
        start = re.search('<!--@athm_BASE64@-->', content).span()[1]
        end = re.search('<!--@athm_js@-->', content).span()[0]
        comment = content[start: end].decode("utf-8")
        # 获取混淆的js代码
        soup = BeautifulSoup(content, "lxml")
        h_js = soup.find('script')
        # 将标题和混淆的js存入一个列表
        return [title, comment, h_js]

    def put_js(self, js):
        """组装js代码"""

        # 去掉多余字符,用切片也可以
        # if '<script>' in js:
        #     js = js.replace('<script>', "")
        # if '</script>' in js:
        #     js = js.replace('</script>', "")
        js = str(js)[8:-9]
        # 在开始处定义变量
        def_var = "var result = "
        js = def_var+js
        # 在指定位置定义数组
        first_point = js.index("{")
        def_arr = "var arr = [];"
        js = js[:first_point+1]+def_arr+js[first_point+1:]
        # 在指定位置给数组赋值
        regex = r"function\s*\w+\(\)\s*\{\s*(\w+)\s*=[\s\S]*?\);\s*(\w+)\s*=[\s\S]*?\);\s*(\w+)\s*=[\s\S]*?\);"
        tuple_groups = re.search(regex, js).groups()
        second_point = re.search(regex, js).span()[1]
        set_arr = "arr = ["+str(tuple_groups[0])+", "+str(tuple_groups[1])+"];"
        js = js[:second_point]+set_arr+js[second_point:]
        # 在指定位置return数组
        add_return = "return arr;"
        js = js.strip()
        js = js[:-13]+add_return+js[-13:]
        return js

    def run_js(self, js):
        """在v8中运行js,获得16进制数字和对应数字"""
        glob = Global()
        list_num16 = []
        list_index = []
        with PyV8.JSContext(glob) as ctext:
            ctext.eval(js)
            vars = ctext.locals
            js_array = vars.result
            for num16 in js_array[0]:
                list_num16.append(num16)
            for index in js_array[1]:
                list_index.append(index)
        return [list_num16, list_index]

    def replace(self, item, font_decoder):
        """用16进制数字替换掉段落中的span"""
        obj = self.get_title_comment_js(item)
        title = obj[0]                   #获取标题
        con = obj[1]                     #获取加密后段落
        js = self.put_js(obj[2])         #获取js后重新组装js
        list_num16_index = self.run_js(js)             #利用v8运行js,获得16进制数字和对应关系
        list_num16 = list_num16_index[0]
        list_num16 = list_num16[0].split(",")
        list_index = list_num16_index[1]
        regex = r"<span\s*class[\s\S]*?hs_kw(\d+)[\w\s\S]*?</span>"
        list_span = re.finditer(regex, con)
        for span in list_span:
            tag_span = span.group().encode('unicode_escape').decode('string_escape')
            index = list_index[int(span.group(1))]
            num16 = list_num16[int(index)]
            glyph = "uni"+num16.upper()
            # decode = DecodeFontFile()
            font = font_decoder.get_font(glyph)
            con = con.replace(tag_span, font)
        return {title: str(con)}

    def decode(self, content, font):
        # 传入完成口碑加密内容, 返回按标题分割的片断列表【A】，【B】，【C】
        items = self.split(content)
        output = {}
        for item in items:
            text = self.replace(item, font)
            output.update(text)
        return output

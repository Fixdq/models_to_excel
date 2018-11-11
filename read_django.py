#! /usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import re
import sys
import xlwt

"""
使用方式：
1:  在项目根目录下运行,Excel文件输出在根目录下
    python read_django  
2:  指定项目的根目录路径，,Excel文件输出在根目录下
    python read_django  "D:\fixdq\model_read"
3:  指定项目的根目录路径，,指定Excel文件输出路径
    python read_django  "D:\fixdq\model_read" "C:\Users\fegnt\Desktop"

"""

# 获取命令行参数
params = sys.argv
# 输出的excel文件名
excel_file_name = "models_display.xls"
# 当前项目所在路径
file_path = os.path.split(os.path.realpath(__file__))[0]
# 默认Excel文件输出的路径
excel_file = os.path.join(file_path, excel_file_name)

if len(params) == 2:
    # 指定的项目路径
    file_path = params[1]

if len(params) == 3:
    # 指定的项目路径
    file_path = params[1]
    # Excel文件输出的路径
    file_out_path = params[2]
    # 生成新的Excel路径
    excel_file = os.path.join(file_out_path, excel_file_name)

# 初始化 excel操作对象
file = xlwt.Workbook()
sheet = file.add_sheet('sheet01', cell_overwrite_ok=True)

# excel 写入 行计数器
r = 1

# 遍历文件夹
for root, dirs, files in os.walk(file_path):
    # 循序判断文件
    for file_name in files:
        # 获取models.py 模型文件
        if file_name == 'models.py':
            # 文件的全路径
            file_path = os.path.join(root, file_name)
            # 调用文件处理

            with open(file_path, 'r') as f:
                for line in f:
                    # 处理单行代码(去除所有空格)
                    line_strip = ''.join(line.split(r' '))
                    # 空白行处理
                    if len(line_strip) == 1: continue
                    # 获取model 类名
                    cls = re.search("^class([a-zA-z]+)", line_strip)
                    if cls and cls.group(1) != 'Meta':
                        print r  # 显示当前插入行数
                        r += 1
                        # 写入类名
                        sheet.write(r, 1, cls.group(1))
                        r += 1

                    # 获取model的field_name、field_type、field_verbose_name
                    res = re.search("([a-zA-z]+)=models\.([a-zA-z]+)\((.*?),", line_strip)
                    if res:
                        print r  # 显示当前插入行数
                        field_name = res.group(1)
                        field_type = res.group(2)
                        field_verbose_name = res.group(3)

                        # 将一行field字段信息写入
                        sheet.write(r, 1, field_name)
                        sheet.write(r, 2, field_type)
                        sheet.write(r, 3, field_verbose_name.decode('utf-8'))
                        r += 1
# 保存Excel文件
file.save(excel_file)

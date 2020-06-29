#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'wu'

import os
import sys
# sys.path.append('./new_loc/localizable/')
from localizable import *
import xlrd
import time

# 查找文件是否不存在，必须是文件形式
def file_not_exist(path):
    if not os.path.exists(path):
        return True
    if os.path.isdir(path):
        return True
    return False


# 查找根目录下所有的bundle文件夹
def all_bundles(path):
    bundles = []
    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            if dir_name.endswith('bundle'):
                bundle_path = os.path.join(path, dir_name)
                for bundle_r, bundle_dirs, bundle_files in os.walk(bundle_path):
                    have_en = bundle_dirs.count('en.lproj') > 0
                    have_zh_hans = bundle_dirs.count('zh-Hans.lproj') > 0
                    have_zh_hant = bundle_dirs.count('zh-Hant.lproj') > 0
                    if have_en and have_zh_hans and have_zh_hant:
                        bundles.append(dir_name)
        return bundles


# 查找根目录下所有的bundle文件夹
def all_excels(path):
    bundles = []
    for root, dirs, files in os.walk(path):
        for file_name in files:
            if file_name.endswith('xlsx'):
                bundles.append(file_name)
        return bundles


def query_loop(first_load):
    tip = '请输入进行的操作， A：校验   B：生成文件\n' if first_load else '请重新输入， A：校验   B：生成文件\n'
    value = input(tip).upper()
    if value == 'A':
        pass
    elif value == 'B':
        generate_file()
    else:
        print('输入有误')
    return value == 'A' or value == 'B'


def generate_file():
    root_path = os.path.abspath('..')
    bundles_path = os.path.join(root_path, 'bundles')
    all_excels_file = all_excels(root_path)
    if len(all_excels_file) == 0:
        print('没有Excel文件')
        exit(0)
    excel_tip = '有以下excel，请选择要解析的文件索引:\n'
    for idx in range(0, len(all_excels_file)):
        excel_tip = excel_tip + str(idx + 1) + ':  ' + all_excels_file[idx] + '\n'

    choosed_excel_index = 1
    if len(all_excels_file) > 1:
        choosed_excel_index = int(input(excel_tip))
        if choosed_excel_index > len(all_excels_file):
            print('索引不对，请重新选择', choosed_excel_index)
            choosed_excel_index = int(input(excel_tip))


    all_bundles_folder = all_bundles(bundles_path)
    if len(all_bundles_folder) == 0:
        print('没有Bundle文件')
        exit(0)

    excel_name = all_excels_file[choosed_excel_index - 1]
    excel_file_path = os.path.join(root_path, excel_name)
    excel_data = xlrd.open_workbook(excel_file_path, encoding_override='utf-8')
    print('excel_file_path', excel_file_path)
    all_language = Language.all_language()
    all_sheet = []

    sheets_in_excel = excel_data.sheets()
    for sheet_index in range(0, len(sheets_in_excel)):
        sheet_excel = sheets_in_excel[sheet_index]

        for colum in range(0, sheet_excel.ncols):
            colum_name = holy_string(sheet_excel.col_values(colum)[0])
            # colum_name = colum_name.replace('\n', '').replace('"', '\\"')

            for language in all_language:

                need_cache = False
                if language.lan_excel_colum_key == colum_name:
                    use_old = False
                    sheet_model = Sheet_info(sheet_excel.name)
                    for the_sheet in all_sheet:
                        if the_sheet.name == sheet_excel.name:
                            sheet_model = the_sheet
                            use_old = True
                    sheet_model.set_colum_value(language.lan_name, colum)
                    if not use_old:
                        need_cache = True
                    for sheet in all_sheet:
                        if sheet.name == colum_name:
                            need_cache = False
                if need_cache:
                    all_sheet.append(sheet_model)


    result_path = os.path.join(root_path, 'result')
    # 创建时间文件夹
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    localtime = time.localtime(time.time())
    cur_parse_folder_name = str(localtime.tm_hour) + '点' + str(localtime.tm_min) + '分' + str(
        localtime.tm_sec) + 's_' + str(localtime.tm_mon) + '月' + str(localtime.tm_mday) + '日'
    cur_parse_folder_path = os.path.join(result_path, cur_parse_folder_name)
    # 创建时间文件夹
    if not os.path.exists(cur_parse_folder_path):
        os.makedirs(cur_parse_folder_path)

    localtime = time.time()
    for bundle_name in all_bundles_folder:
        print('开始解析bundle：', bundle_name)
        bundle = Bundle(bundle_name, bundles_path)
        sheet_names = bundle.parse_sheet_names()
        loca_sheets = []
        for sheet_name in sheet_names:
            for sheet_model in all_sheet:
                if sheet_model.name == sheet_name:
                    loca_sheets.append(sheet_model)

        for sheet in loca_sheets:
            print(bundle_name, 'sheet名称', sheet.name, '信息', sheet.colum_info)

        localizable11 = Localizable(excel_data, bundle, loca_sheets, cur_parse_folder_path)
        localizable11.start_parse()

    cur_time = time.time()
    print('本地化结束, 耗时%.2f s' % (cur_time - localtime))


if __name__ == '__main__':
    generate_file()
    exit(0)
    stop_loop = False
    first_load = True
    while not stop_loop:
        stop_loop = query_loop(first_load)
        first_load = False

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'wu'

import os
import xlrd
import time
import sys

class Language:

    def __init__(self, lan_name, lan_excel_colum_key, des, ignore=False):
        self.lan_name = lan_name
        self.lan_excel_colum_key = lan_excel_colum_key
        self.des = des
        self.local_lines = []
        self.ignore = ignore
        self.use_substitute = False

        # lan_name: 语言的key， colum_excel：此语言在excel表中列的名称  des：不参与解析，阅读方便
        # ignore 是否忽略解析，写入源bundle对应语言文件，
        # use_substitute，是否使用替身，即英文找不到时是否需要尝试从源bundle对应语言
        # 获取所有语言数组

    @classmethod
    def language_colum_key(cls, name):
        all_language = Language.all_language()
        for language in all_language:
            if language.lan_name == name:
                return language.lan_excel_colum_key
        return None

    @classmethod
    def all_language(cls):
        lan_zh_hans = {'lan_name': 'zh-Hans', 'colum_excel_key': '简体中文', 'des': '简体中文', 'ignore': True}
        lan_zh_hant = {'lan_name': 'zh-Hant', 'colum_excel_key': '繁體中文', 'des': '繁体中文', 'ignore': False, 'use_substitute': True}
        lan_en = {'lan_name': 'en', 'colum_excel_key': '英文', 'des': '英文', 'ignore': True}
        lan_de = {'lan_name': 'de', 'colum_excel_key': 'DE    德语   Deutsch', 'des': '德语', 'ignore': False}
        lan_pt = {'lan_name': 'pt-BR', 'colum_excel_key': 'PT   葡萄牙语   Português', 'des': '葡萄牙语', 'ignore': False}

        lan_jp = {'lan_name': 'ja', 'colum_excel_key': 'JP   日语    日本語', 'des': '日本语', 'ignore': False}
        lan_ko = {'lan_name': 'ko', 'colum_excel_key': 'KR    韩语  한국어', 'des': '韩语', 'ignore': False}
        lan_fr = {'lan_name': 'fr', 'colum_excel_key': 'FR   法语 (法国)    Français', 'des': '法语', 'ignore': False}
        lan_es = {'lan_name': 'es', 'colum_excel_key': 'ES  西班牙语   Español', 'des': '西班牙语', 'ignore': False}
        lan_ru = {'lan_name': 'ru', 'colum_excel_key': 'RU   俄语  Русский', 'des': '俄语', 'ignore': False}

        lan_ar = {'lan_name': 'ar', 'colum_excel_key': '阿拉伯语 (埃及)', 'des': '阿拉伯语', 'ignore': False}
        lan_id = {'lan_name': 'id', 'colum_excel_key': 'ID  印度尼西亚语   Bahasa Indonesia', 'des': '印度尼西亚语', 'ignore': False}
        lan_it = {'lan_name': 'it', 'colum_excel_key': 'IT    意大利语   Italiano', 'des': '意大利语', 'ignore': False}
        lan_nl = {'lan_name': 'nl', 'colum_excel_key': 'NL    荷兰语   Nederlands', 'des': '荷兰语', 'ignore': False}
        lan_th = {'lan_name': 'th', 'colum_excel_key': 'TH   泰语   ภาษาไทย', 'des': '泰文', 'ignore': False}

        # languages_dicts = [lan_zh_hans, lan_zh_hant, lan_en, lan_de, lan_pt, lan_jp, lan_ko, lan_fr, lan_es, lan_ru, lan_ar, lan_id, lan_it, lan_nl, lan_th]
        languages_dicts = [lan_zh_hans, lan_zh_hant, lan_en, lan_de, lan_pt, lan_jp, lan_ko, lan_fr, lan_es, lan_ru, lan_it]
        languages_model = []
        for lan_dict in languages_dicts:
            model = Language(lan_dict['lan_name'], lan_dict['colum_excel_key'], lan_dict['des'], lan_dict['ignore'])
            use_substitute_v = lan_dict.get('use_substitute')
            if use_substitute_v is not None:
                model.use_substitute = lan_dict.get('use_substitute')
            languages_model.append(model)
        return languages_model


class Sheet_info:

    def __init__(self, name):
        self.name = name
        self.colum_info = {}

    def get_colum_value(self, key):
        return int(self.colum_info[key])

    def set_colum_value(self, key, value):
        self.colum_info[key] = value


class Bundle:

    def __init__(self, name, folder_in=os.path.abspath('..')):
        self.name = name
        self.folder_in = folder_in

    def parse_sheet_names(self):
        # if self.name == 'Login.bundle':
        #     return ['登录注册']
        # if self.name == 'CameraBundle.bundle':
        #     return ['相机']
        # if self.name == 'Editor.bundle':
        #     return ['编辑器']
        # if self.name == 'Filmic.bundle':
        #     return ['相机', '编辑器', '登录注册', '社区', 'ZY Cami Prime']
        # else:
        return ['相机', '编辑器', '登录注册', '社区', 'ZY Cami Prime']

    def bundle_path(self):
        return os.path.join(self.folder_in, self.name)

    def localizable_file_path(self, lan_name):
        folder_name = lan_name + '.lproj'
        folder_path = os.path.join(self.bundle_path(), folder_name)
        return os.path.join(folder_path, local_language_string())


def holy_string(string):
    return string.replace('\n', '').replace('"', '\\"')


def local_language_string():
    return 'Localizable.strings'


class Localizable:

    # base_lan表示以哪个语言为根语言（即以该语言内容为准开始查找）， bundle此次解析的bundle，此次解析的sheets数组
    def __init__(self, excel_data, bundle, sheets, cur_parse_folder_path, root_lan='en'):
        self.excel_data = excel_data
        self.bundle = bundle
        self.sheets = sheets
        self.root_lan = root_lan
        self.cur_parse_folder_path = cur_parse_folder_path

    def root_lan_colum_value(self, sheet_data):
        return self.lan_colum_value(sheet_data, self.root_lan)

    def lan_colum_value(self, sheet_data, lan_name):
        colum_str = Language.language_colum_key(lan_name)
        for colum in range(0, sheet_data.ncols):
            colum_name = holy_string(sheet_data.col_values(colum)[0])
            if colum_str == colum_name:
                return colum
        return None

    def parse_language_with_sheet_info(self, language, sheet_colum_info, line):
        have_find = False
        save_content = fetch_content_from_line(line)
        save_key = fetch_key_from_line(line)
#        print('save_content', save_content)
        sheet_data = self.excel_data.sheet_by_name(sheet_colum_info.name)
        root_lan_colum_value = self.root_lan_colum_value(sheet_data)
        other_lan_colum_value = self.lan_colum_value(sheet_data, language.lan_name)
        ret_string = line
        if not root_lan_colum_value:
            ret_string = line
        if not other_lan_colum_value:
            ret_string = line
        if root_lan_colum_value and other_lan_colum_value:
            for row in range(0, sheet_data.nrows):
                root_str = holy_string(sheet_data.cell_value(row, root_lan_colum_value))
                if save_content == root_str:
                    other_language_str = holy_string(sheet_data.cell_value(row, other_lan_colum_value))
                    ret_string = '"' + save_key + '"' + ' ' + '=' + ' ' + '"' + other_language_str + '"' + ';'
                    have_find = True
                    break
        ret_tup = (have_find, ret_string)
        return ret_tup

    # 开始解析
    def start_parse(self):
        root_path = os.path.abspath('..')
        cur_parse_folder_path = self.cur_parse_folder_path
        # 创建bundle
        new_bundle_path = os.path.join(cur_parse_folder_path, self.bundle.name)
        if not os.path.exists(new_bundle_path):
            os.makedirs(new_bundle_path)

        root_file_path = self.bundle.localizable_file_path('en')
        # print('根语言路径:', root_file_path)
        all_languages = Language.all_language()

        logs = []
        for the_language in all_languages:
            language_log = []
            tupule_log = (language_log, the_language.des)
            logs.append(tupule_log)
            language_proj_folder_name = the_language.lan_name + '.lproj'
            language_proj_folder_path = os.path.join(new_bundle_path, language_proj_folder_name)
            if not os.path.exists(language_proj_folder_path):
                os.makedirs(language_proj_folder_path)
            the_language.language_file_path = os.path.join(language_proj_folder_path, local_language_string())

            if the_language.ignore:
                lan_file_path = self.bundle.localizable_file_path(the_language.lan_name)
                print('需要忽略解析的语言:', the_language.des, lan_file_path)
                with open(lan_file_path, 'r') as read:
                    all_line = read.readlines()
                    for line in all_line:  # 依次读取每行
                        the_language.local_lines.append(line)
            else:
                print('正在解析语言:', the_language.des)
                with open(root_file_path, 'r') as read:
                    all_line = read.readlines()
                    for line in all_line:  # 依次读取每行
                        line = line.strip(' ').replace('\n', '')
                        if len(line) > 0 and line.startswith('"'):
                            found = False
                            for sheet_colum_info in self.sheets:
                                tup = self.parse_language_with_sheet_info(the_language, sheet_colum_info, line)
                                if tup[0]:
                                    the_language.local_lines.append(tup[1])
                                    found = True
                                    break
                            if not found:
                                # 是繁体的话找不到从源bundle中找，再找不到才用英文
                                have_fill_with_origin = False
                                if the_language.lan_name == 'zh-Hant':
                                    save_key = fetch_key_from_line(line)
                                    if not save_key:
                                        print('line == ', line)
                                    whole_key_str = '"'+save_key+'"'
                                    zhhans_file_path = self.bundle.localizable_file_path('zh-Hant')
                                    if os.path.exists(zhhans_file_path):
                                        with open(zhhans_file_path, 'r') as read_zhhans:
                                            all_line_hans = read_zhhans.readlines()
                                            for line_hans in all_line_hans:
                                                if whole_key_str in line_hans:
                                                    # print('从源bundle中匹配了', line)
                                                    the_language.local_lines.append(line_hans)
                                                    have_fill_with_origin = True
                                                    break
                                if not have_fill_with_origin:
                                    if language_log.count(line) == 0:
                                        language_log.append(line)
                                    the_language.local_lines.append(line)

                        else:
                            the_language.local_lines.append(line)

        # 开始写文件
        for the_language in all_languages:
            with open(the_language.language_file_path, 'w+') as f:
                if the_language.ignore:
                    f.writelines(line for line in the_language.local_lines)
                else:
                    f.writelines(line + '\n' for line in the_language.local_lines)

        log_file_name = 'log.txt'
        log_file_path = os.path.join(cur_parse_folder_path, log_file_name)

        with open(log_file_path, 'a+') as f:
            add_str = '\n\n\n' + self.bundle.name + '  没有找到对应翻译的行有\n\n'
            f.writelines(add_str)
            need_log = []
            for log_tup in logs:
                language_des = log_tup[1]
                log_lan = log_tup[0]

                have_print = False
                for log in log_lan:
                    if need_log.count(log) == 0:
                        if not have_print:
                            add_str = '\n\n' + language_des + '  没有找到的行有  ' + str(len(log_lan)) + '  个\n\n'
                            need_log.append(add_str)
                            have_print = True
                        need_log.append(log)

            f.writelines(line + '\n' for line in need_log)

    @classmethod
    def localizable_with_zh_hans_file(cls):
        localtime = time.time()
        print('开始处理本地化')
        root_path = os.path.abspath('..')
        bundle_name = 'Editor.bundle'
        bundle_path = os.path.join(root_path, bundle_name)
        if folder_not_exist(bundle_path):
            print('bundle表不存在', bundle_path)
            exit(0)
        zh_hans_lproj_path = os.path.join(bundle_path, 'zh-Hans.lproj')
        zh_hans_loca_path = os.path.join(zh_hans_lproj_path, local_language_string())

        excel_file_path = os.path.join(root_path, 'ZY Cami翻译文案6.4.xlsx')
        excel_data = excel_data_with_name(excel_file_path)
        sheet_names = list(excel_data.sheet_names())
        if len(excel_data.sheets()) == 0:
            print('excel中没有sheet')
            exit(0)
        need_sheet_name = '编辑器'
        if sheet_names.count(need_sheet_name) == 0:
            print('excel中没有要解析的表')
            exit(0)
        need_sheet = excel_data.sheet_by_name(need_sheet_name)

        colum_value_hans = -1
        colum_value_en = -1
        for colum in range(0, need_sheet.ncols):
            colum_name = need_sheet.col_values(colum)[0]
            if '简体中文' == colum_name:
                colum_value_hans = colum
            if 'DE    德语   Deutsch' == colum_name:
                colum_value_en = colum
        print(need_sheet.ncols)
        print('中文在', colum_value_hans, '列，英文在', colum_value_en)
        be_write_info_exist = []
        be_write_info_not_exist = []
        with open(zh_hans_loca_path, 'r') as read:
            all_line = read.readlines()
            print('有', len(all_line), '行翻译内容')
            for line in all_line:  # 依次读取每行
                line = line.strip(' ').replace('\n', '')
                if len(line) > 0 and line.startswith('"'):
                    have_exist = False
                    content = fetch_content_from_line(line)
                    for row in range(0, need_sheet.nrows):
                        zh_hans_str = need_sheet.cell_value(row, colum_value_hans).replace('\n', '').replace('"', '\\"')
                        other_language_str = need_sheet.cell_value(row, colum_value_en)
                        other_language_str = other_language_str.replace('\n', '').replace('"', '\\"')
                        if content == zh_hans_str:
                            key_str = fetch_key_from_line(line)
                            need_write = '"' + key_str + '"' + ' ' + '=' + ' ' + '"' + other_language_str + '"' + ';'
                            have_exist = True
                            be_write_info_exist.append(need_write)
                            break
                    if not have_exist:
                        be_write_info_not_exist.append(line)
                else:
                    be_write_info_exist.append(line)

        # 行内容存在与表中存放在 Localizable_exist，不存在放在
        loc_file_name_exist = 'Localizable_exist.strings'
        loc_file_name_not_exist = 'Localizable_not_exist.strings'
        loc_file_path_exist = os.path.join(root_path, loc_file_name_exist)
        loc_file_path_not_exist = os.path.join(root_path, loc_file_name_not_exist)
        with open(loc_file_path_exist, 'w+') as f:
            f.writelines(line + '\n' for line in be_write_info_exist)
        with open(loc_file_path_not_exist, 'w+') as f:
            f.writelines(line + '\n' for line in be_write_info_not_exist)

        cur_time = time.time()
        print('本地化结束, 耗时%.2f s' % (cur_time - localtime))


# 查找根目录下所有的bundle文件夹
def all_bundles(path):
    bundles = []
    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            if 'bundle' in dir_name:
                bundles.append(dir_name)
        return bundles


# 查找文件是否不存在，必须是文件形式
def file_not_exist(path):
    if not os.path.exists(path):
        return True
    if os.path.isdir(path):
        return True
    return False


# 查找文件夹是否不存在，必须是文件夹形式
def folder_not_exist(path):
    if not os.path.exists(path):
        return True
    if os.path.isfile(path):
        return True
    return False


def excel_data_with_name(excel_file_path):
    if file_not_exist(excel_file_path):
        return None
    excel_data = xlrd.open_workbook(excel_file_path, encoding_override='utf-8')
    return excel_data


def fetch_key_from_line(line_info):
    if not line_info.startswith('"'):
        return None
    arr = line_info.split('"')
    if len(arr) > 2:
        return arr[1]
    else:
        return None


def fetch_content_from_line(line_info):
    if not line_info.startswith('"'):
        return None
    arr = line_info.split('"')
    if len(arr) == 5:
        return arr[3]
    else:
        return None


if __name__ == '__main__':

    Localizable.localizable_with_zh_hans_file()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'wu'

import os
import time


# 检测路径下文件夹是否是bundle
def directory_is_bundle(directory_path):
    if not os.path.isdir(directory_path):
        return False
    for bundle_r, bundle_dirs, bundle_files in os.walk(directory_path):
        have_en = bundle_dirs.count('en.lproj') > 0
        have_zh_hans = bundle_dirs.count('zh-Hans.lproj') > 0
        have_zh_hant = bundle_dirs.count('zh-Hant.lproj') > 0
        if have_en and have_zh_hans and have_zh_hant:
            return True
    return False


# 需要忽略的文件夹
def need_ignore_directory_names():
    return ['Pods', 'ZYLibrary']

# 根据行信息获取key
def fetch_key_from_line(line_info):
    if not line_info.startswith('"'):
        return None
    arr = line_info.split('"')
    if len(arr) == 5:
        return arr[1]
    else:
        return None

# 查找目录下所有的bundle文件夹
def check_bundles(path):
    bundles = []
    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            bundle_path = os.path.join(path, dir_name)
            if dir_name.endswith('bundle'):
                if directory_is_bundle(bundle_path):
                    if bundles.count(bundle_path) == 0:
                        bundles.append(bundle_path)
            else:
                if need_ignore_directory_names().count(dir_name) == 0:
                    bundles_dir = check_bundles(bundle_path)
                    if len(bundles_dir) > 0:
                        for bundle in bundles_dir:
                            if bundles.count(bundle) == 0:
                                bundles.append(bundle)

    return bundles


def all_strings(path):
    strings_files = []
    for root, dirs, files in os.walk(path):
        for the_file in files:
            file_path = os.path.join(path, the_file)
            if file_path.endswith('strings'):
                strings_files.append(file_path)
    return strings_files


# 查找目录下所有的strings文件
def all_strings_files(path):
    strings_files = []
    for root, dirs, files in os.walk(path):
        for dir_name in dirs:
            bundle_path = os.path.join(path, dir_name)
            strings_files_temp = all_strings(bundle_path)
            if len(strings_files_temp) > 0:
                for the_file in strings_files_temp:
                    strings_files.append(the_file)
    return strings_files


def probe_strings_file_with_strings_file(strings_path, other_strings_path):
    this_lines = []
    other_lines = []
    total_result = True
    with open(strings_path, 'r') as read_this:
        this_lines = read_this.readlines()
    with open(other_strings_path, 'r') as read_other:
        other_lines = read_other.readlines()
    for this_line in this_lines:
        this_line = this_line.strip(' ').replace('\n', '')
        if len(this_line) > 0 and this_line.startswith('"'):
            line_result = False
            key_str = fetch_key_from_line(this_line)
            if key_str is None:
                continue
            # 带引号的key
            key_str_with_quotes = '"'+key_str+'"'

            for other_line in other_lines:
                other_line = other_line.strip(' ').replace('\n', '')
                if len(other_line) > 0 and other_line.startswith('"'):
                    if key_str_with_quotes in other_line:
                        line_result = True
                        break

            if not line_result:

                total_result = False
                folder_name = ''
                arr = other_strings_path.split('/')
                if len(arr) > 3:
                    folder_name = arr[-2]
                print(this_line, '\t在 ', folder_name, ' 中没有找到对应key')
    return total_result


# 分析单个strings文件，原理是和bundle中其他strings文件作比较
def probe_strings_file(file_path, bundle_path):
    print('\n开始分析strings文件：', file_path)
    # 先找到其他stringsFile
    other_files = all_strings_files(bundle_path)
    for file_p in other_files:
        if file_p == file_path:
            other_files.remove(file_p)
    # print('找到的其他     strings文件：')
    for strings_file in other_files:
        print('strings文件：', file_path, '和', strings_file)
        result = probe_strings_file_with_strings_file(file_path, strings_file)

        folder_name = ''
        arr = strings_file.split('/')
        if len(arr) > 3:
            folder_name = arr[-2]
        print('在', folder_name, '中', '验证通过' if result else '验证不通过')


def probe_bundle(bundle_path):
    print('\n\n\n开始分析bundle：', bundle)
    strings_files = all_strings_files(bundle_path)
    for strings_file in strings_files:
        probe_strings_file(strings_file, bundle_path)


if __name__ == '__main__':
    start_time = time.time()
    print('开始查询bundle数量......')
    bundles = check_bundles('.')

    if len(bundles) == 0:
        exit(0)

    for bundle_path in bundles:
        print(bundle_path)
    for bundle in bundles:
        probe_bundle(bundle)

    speend_time_look_for = '{:.2f}'.format(time.time() - start_time)
    print('总共找到', len(bundles), '个bundle', '耗时', speend_time_look_for, 's')



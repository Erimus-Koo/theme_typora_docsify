#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'Erimus'

import subprocess
import json
import zipfile
import os

# ═══════════════════════════════════════════════


# 获取最新的 release 版本号
def get_latest_version():
    result = subprocess.run(
        ['gh', 'release', 'view', '--json', 'tagName', '-q', '.tagName'],
        stdout=subprocess.PIPE)
    # print(f'{result.stdout = }')
    latest_version = result.stdout.decode('U8').strip()
    return latest_version


# 自增版本号
def increment_version(latest_version):
    # 分割主版本号、次版本号和修订号
    version_parts = latest_version.split('.')

    # 增加修订号
    version_parts[-1] = str(int(version_parts[-1]) + 1)

    # 合并版本号
    new_version = '.'.join(version_parts)
    return new_version


# 创建 zip 文件
def create_zip(source_files, output_filename):
    with zipfile.ZipFile(output_filename,
                         'w',
                         compression=zipfile.ZIP_DEFLATED) as zipf:
        for source_file in source_files:
            if os.path.isfile(source_file):
                zipf.write(source_file)
            else:
                for foldername, subfolders, filenames in os.walk(source_file):
                    for filename in filenames:
                        file_path = os.path.join(foldername, filename)
                        zipf.write(file_path)


def create_and_push_new_tag(tag_name, commit='HEAD'):
    # 创建新的标签
    subprocess.run(['git', 'tag', tag_name, commit], check=True)

    # 推送新的标签到远程仓库
    subprocess.run(['git', 'push', 'origin', tag_name], check=True)


# 创建 release
def create_release(version, zip_filename):
    release_notes = input('Input release notes:')
    subprocess.run([
        'gh', 'release', 'create', version, zip_filename, '-t', version, '-n',
        release_notes
    ])


def get_commit_hash(reference):
    result = subprocess.run(['git', 'rev-parse', reference],
                            stdout=subprocess.PIPE,
                            check=True)
    return result.stdout.decode('U8').strip()


def check_new_commit(latest_version):
    subprocess.run(['git', 'fetch', '--tags'])
    latest_version_commit_hash = get_commit_hash(latest_version)
    head_commit_hash = get_commit_hash('HEAD')
    return latest_version_commit_hash != head_commit_hash


def main():
    latest_version = get_latest_version()
    print(f'{latest_version = }')

    if not check_new_commit(latest_version):
        print('No new commits, skipping release creation.')
        return

    new_version = increment_version(latest_version)
    input_new_version = input(f'Your new release version is: {new_version}\n' +
                              'Press enter to accept or input a new one...')
    new_version = input_new_version.strip() or new_version
    print(f'{new_version = }')

    source_files = ['typora-docsify.css', 'typora-docsify']
    zip_filename = f'theme_typora_docsify_{new_version}.zip'
    create_zip(source_files, zip_filename)

    # create_and_push_new_tag(new_version)
    create_release(new_version, zip_filename)


# ═══════════════════════════════════════════════

if __name__ == '__main__':

    main()
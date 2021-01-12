# -*- coding: utf-8 -*-
# @Time : 2021/1/11 18:33
# @Author : khm

import hashlib

'''对url进行压缩操作'''
def get_md5(url):
    # 先判断下编码是不是合适的
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

if __name__ == "__main__":
    print(get_md5("http://jobbole.com".encode("utf-8")))
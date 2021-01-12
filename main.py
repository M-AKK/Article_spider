# -*- coding: utf-8 -*-
# @Time : 2021/1/6 21:50
# @Author : khm

from scrapy.cmdline import execute

import sys
import os

#print (os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy","crawl","jobbole"])
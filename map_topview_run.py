#!
# coding:utf-8
# --------------------------------------------------------
# heatmap and pathflow
# Copyright (c) 2017 vmaxx
# Written by fang
# --------------------------------------------------------

from lib import map_Topview_class as mtd
import argparse
import time
import sys,os
import logging

def parse_args():
    """ Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="heatmap_topview")
    parser.add_argument(
        "-propertyID", help="propertyID",
        default="49",required=False)
    parser.add_argument(
        "-starttime", help="starttime 2017-09-09 18:30:00",
        default="2018-03-06 08:00:00",required=False)
    parser.add_argument(
        "-endtime", help="endtime 2017-08-23 19:30:00",
        default="2018-03-08 22:00:00",required=False)
    return parser.parse_args()

def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

def run():
    codeRootdir = cur_file_dir()
    mapTOPview_Obj = mtd.MapTopviewDraw(codeRootdir)
    start = time.time()
    Heatpath = mapTOPview_Obj.runHeat_topview_ford("21")
    end1 = time.time()

    return Heatpath

if __name__ == "__main__":
    path = run()


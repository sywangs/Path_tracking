from __future__ import division
import numpy as np
import math

init = np.zeros((44,34))

width = 12
height = 8

#tan = delta col - delta row ,means a rat of width for function
tan =  0.5
#row direction
dir = 1

#start position
squre_start_co = 20
squre_start_ro= 20

#function start
start_co_ = squre_start_co
start_ro_ = squre_start_ro


def move_row(delta_row):
    if tan > 0:
        dir_row = dir
        dir_co = - dir_row
    else:
        dir_row = - dir
        dir_co = dir_row

    if tan == 0:
        return (start_ro_ + delta_row * dir_row,squre_start_co - 1)

    tan_row = - 1 / tan



    need_add = False
    if math.fabs(tan_row) >= 1:
        b = squre_start_co - tan_row * squre_start_ro
        start_ro_pre = int(math.floor((start_co_ + int(max(delta_row -1,0)) * dir_co - b) / tan_row))

        start_co = start_co_ + delta_row * dir_co
        start_ro = int(math.floor((start_co - b) / tan_row))

        if not start_ro_pre - start_ro == 0:
            need_add = True

        return (start_ro,start_co,need_add)

    if math.fabs(tan_row) <= 1:
        b = squre_start_co - tan_row * squre_start_ro
        start_co_pre = int(math.floor(tan_row * (start_co_ + int(max(delta_row -1,0)) * dir_row) + b))

        start_ro = start_ro_ + delta_row * dir_row
        start_co = int(math.floor(tan_row * start_ro + b))

        if not start_co - start_co_pre == 0:
            need_add = True

        return (start_ro,start_co,need_add)


def move_col(start_ro_Row,start_co_Row,delta,need_add):
    if tan > 0:
        dir_row = dir
        dir_co = dir_row
    else:
        dir_row = dir
        dir_co = - dir_row


    data = []
    if tan == 0:
        return (start_ro_Row,start_co_Row + delta * dir)

    if math.fabs(tan) >= 1:
        b = start_co_Row - tan * start_ro_Row
        start_ro_pre = int(math.floor((start_co_Row + int(max(delta -1,0)) * dir_co - b) / tan))

        start_co =  start_co_Row + delta * dir_co
        start_ro = int(math.floor((start_co - b) / tan))
        data.append((start_ro,start_co))

        if need_add and not start_ro_pre - start_ro == 0:
            data.append((start_ro_pre,start_co))
        return data

    if math.fabs(tan) <= 1:
        b = start_co_Row - tan * start_ro_Row
        start_co_pre = int(math.floor(tan * (start_ro_Row + int(max(delta -1,0))  * dir_row) + b))

        start_ro = start_ro_Row + delta * dir_row
        start_co = int(math.floor(tan * start_ro + b))
        data.append((start_ro,start_co))

        if need_add and not start_co_pre - start_co == 0:
            data.append((start_ro,start_co_pre))
        return data


i = 1
for delta in range(height):
    (start_ro,start_co,need_add) = move_row(delta)
    for delta_co in range(width):
        data = move_col(start_ro,start_co,delta_co,need_add)
        i = i + 1
        for (ro_inner,co_inner) in data:
            init[ro_inner][co_inner] = i


cc = init












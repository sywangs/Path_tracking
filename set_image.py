import numpy as np
import math

init = np.zeros((44,34))

width = 12
height = 8

tan = 2

squre_start_co = 20
squre_start_ro= 20

range_co = int((width ** 2/ (1 + tan ** 2)) ** 0.5)
range_ro = int((height ** 2/ (1 + tan ** 2)) ** 0.5)

start_co_ = squre_start_co
start_ro_ = squre_start_ro


i = 0
for delta_height in range(range_ro):
    start_ro = start_ro_ + delta_height
    start_co = start_co_ - int(math.floor(tan * delta_height))
    for delta_width in range(range_co):
        i = i + 1
        ro_inner = start_ro + int(math.floor(tan * delta_width))
        co_inner = start_co + delta_width
        init[ro_inner][co_inner] = i


cc = init












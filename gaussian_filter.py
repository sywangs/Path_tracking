import numpy as np
from numba import jit
import math
import time
import matplotlib.pyplot as plt

import cv2
from distribution import parse_det_txt
import os


# coor = np.zeros([10,10])
# coor[0,0]=6
# coor[9,9]=10
# coor_cp = coor.copy()


def gaussian_filter(winsize,sigma):
    winsize = int(winsize)
    radius = math.floor(winsize/2)
    filter = np.zeros((winsize,winsize))
    # summ = 0.0

    for i in range(winsize):
        for j in range(winsize):
            internal = math.exp(-(((i-radius)**2+(j-radius)**2)/(2*sigma**2)))
            filter[i,j] = internal
    #         summ = summ+filter[i,j]
    # filter = filter/summ
    return filter,radius



@jit(nopython=True)
def cover_guassian(coor,kernal,radius):

    coor_cp = coor.copy()
    people_coor = np.where(coor > 0)
    h,w = coor_cp.shape

    for centre_y, centre_x in zip(people_coor[0], people_coor[1]):

        for ny, i in enumerate(range(int(centre_y-radius),int(centre_y+radius+1))):
            if (i < 0) | (i > (h-1)):
                continue
            for nx, ii in enumerate(range(int(centre_x-radius),int(centre_x+radius+1))):
                if (ii < 0) | (ii > (w-1)):
                    continue

                coor_cp[i,ii] = coor_cp[i,ii] + kernal[ny,nx] *1000 * coor[centre_y,centre_x]


    return coor_cp

######################################################################################################################

if __name__ == '__main__':

    coor = parse_det_txt('495-1')

    winsize = 151
    sigma = 30
    tic = time.time()
    kernal,radius = gaussian_filter(winsize,sigma)
    print('time consume:'+str(time.time()-tic))

    tic = time.time()
    aa = cover_guassian(coor,kernal,radius)
    print('time consume: ' + str(time.time()-tic))



    topimg = cv2.imread('./img/huanqiulama.png')

    fig = plt.figure()
    fig.dpi = 200.
    fig.set_size_inches([1920/200,1080/200])
    ax = fig.add_axes([0., 0., 1., 1.])
    ax.imshow(topimg)

    plt.imshow(aa, alpha=0.4, cmap='jet')
    plt.show()

    




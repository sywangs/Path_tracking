import numpy as np
import math
from numba import jit
import matplotlib.pyplot as plt

def gaussian_filter(winsize, sigma):
    winsize = int(winsize)
    radius = math.floor(winsize / 2)
    filter = np.zeros((winsize, winsize))

    for i in range(winsize):
        for j in range(winsize):
            internal = math.exp(-(((i - radius) ** 2 + (j - radius) ** 2) / (2 * sigma ** 2)))
            filter[i, j] = internal

    return filter, radius

# @jit(nopython=True)
def cover_bk_guassian(bkimg,c_yx, detcount, kernal, radius):
    h, w, _ = bkimg.shape
    overlay = np.zeros([h, w], dtype=np.int)

    def normalize_v(input, r_min=10, r_max=100):
        input = input.astype(np.float)
        m = input.min()
        range = input.max() - m
        if m != input.max():
            input = (input - m) / range
            range2 = r_max - r_min
            normalized = (input * range2) + r_min
            normalized = normalized.astype(np.int)
            return normalized
        else:
            return input

    # detcount = normalize_v(np.asarray(detcount), 1000, 5000)

    if not len(detcount) == 0:

        for yx, factor in zip(c_yx,detcount):
            centre_x = int(np.floor(yx[1] * w))
            centre_y = int(np.floor(yx[0] * h))

            for i, ny in zip(range(int(centre_y - radius), int(centre_y + radius + 1)), range(int(radius*2))):
                if (i < 0) | (i > (h - 1)):
                    continue
                for ii, nx in zip(range(int(centre_x - radius), int(centre_x + radius + 1)), range(int(radius*2))):
                    if (ii < 0) | (ii > (w - 1)):
                        continue
                    else:
                        overlay[i, ii] = overlay[i, ii] + int((kernal[ny, nx] * 1000 * factor))

    return overlay

def cover_guassian(coor, kernal, radius):

    coor_cp = coor.copy()
    people_coor = np.where(coor > 0)
    h, w = coor_cp.shape

    for centre_y, centre_x in zip(people_coor[0], people_coor[1]):

        for i, ny in zip(range(int(centre_y - radius), int(centre_y + radius + 1)), range(int(radius*2+1))):
            if (i < 0) | (i > (h - 1)):
                continue
            for ii, nx in zip(range(int(centre_x - radius), int(centre_x + radius + 1)), range(int(radius*2+1))):
                if (ii < 0) | (ii > (w - 1)):
                    continue

                coor_cp[i, ii] = coor_cp[i, ii] + kernal[ny, nx] * 1000 * coor[centre_y, centre_x]

    return coor_cp

def plot(bkimg,overlay,codeRootdir):

    h, w, _ = bkimg.shape
    fig = plt.figure()
    fig.dpi = 200.
    fig.set_size_inches([w / fig.dpi, h / fig.dpi])
    ax = fig.add_axes([0., 0., 1., 1.])
    ax.imshow(bkimg)

    overlay_clip = np.ma.masked_where(overlay < 0, overlay)
    all_im = plt.imshow(overlay_clip, alpha=0.7, cmap='rainbow')

    # color_bar
    cx = fig.add_axes([0.95, 0.5, 0.02, 0.3])  # colorbar show cite(x,y,w,h)
    fig.colorbar(all_im, cax=cx, alpha=0.7)
    plt.axis('off')

    fig.savefig(codeRootdir + "/result/map_topview.png", dpi=fig.dpi)

    return codeRootdir + "/result/map_topview.png"

def run(bkimg, camera_list, camera_det,rootdir, winsize, sigma):

    f,r = gaussian_filter(winsize,sigma)
    if len(camera_list)==0 or len(camera_det)==0:
        print('camera_list/detection list is empty')
        h, w, _ = bkimg.shape
        overlay = np.zeros([h, w], dtype=np.int)
    else:
        overlay = cover_bk_guassian(bkimg,camera_list,camera_det,f,r)
    return plot(bkimg,overlay,rootdir)

#!/usr/bin/python
# coding:utf-8

# export display := 0
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import mysql.connector
import shutil
import commands as cm
import cv2
import time
import json
import datetime
import sys
import new_topview


class MapTopviewDraw(object):
    def __init__(self,codeRootdir):
        self.codeRootdir = codeRootdir
        self.localpath = self.codeRootdir+"/cache_/graph/"
        self.winsize = 1001
        self.sigma = 200

        # read configure file, got the db param, img information.
        cfgStr = ""
        try:
            with open(self.codeRootdir+"/param/param.json", "r") as f:
                lines = f.readlines()
                for line in lines:
                    cfgStr = cfgStr + line
        except BaseException, e:
            print e
            # logging.error('__init__:' + e)

        cfgObj = json.loads(cfgStr)
        self.img_height = int(cfgObj["imgheight"])
        self.img_width = int(cfgObj["imgwidth"])
        self.img_scale = int(cfgObj["imgscale"])
        self.db = cfgObj["db"]
        self.dbHost = cfgObj["dbHost"]
        self.dbUserName = cfgObj["dbUserName"]
        self.dbPwd = cfgObj["dbPwd"]
        self.storageAccount = cfgObj["storageAccount"]
        self.accountKey = cfgObj["accountKey"]
        self.AZURE_BINARY = cfgObj["AZURE_BINARY"]

        if self.img_scale != 0:
            self.img_height = int(int(self.img_height) / int(self.img_scale))
            self.img_width = int(int(self.img_width) / int(self.img_scale))
        # self.img_height = 480
        # self.img_width = 640


    def selectMapandDown(self,propertyID):
        start = time.time()
        try:
            conn = mysql.connector.connect(host=self.dbHost, user=self.dbUserName, password=self.dbPwd, database=self.db)
            cursor = conn.cursor()
            command = "SELECT floor_plane_url FROM `floor` WHERE id=" + str(propertyID)
            # print command

            cursor.execute(command)
        except:
            print "sql error"
            # logging.error('selectMapandDown:sql error')
            return 0

        line_map = cursor.fetchone()
        if not line_map is None:
            length_line = len(line_map)

            cursor.close()
            if length_line > 0:
                # i_line = random.randint(0, length_line-1)
                map_url = line_map[0]
                if not map_url is None:

                    try:
                        os.chdir(self.codeRootdir + "/cache_/bk")
                        command = "wget -O " +str(propertyID) +"property.jpg "+ map_url
                        (status, output) = cm.getstatusoutput(command)
                        os.chdir("..")
                        os.chdir("..")
                    except:
                        pass
                        # logging.warning('map_url is not image')


        conn.commit()
        cursor.close()
        conn.close()

        end2 = time.time()
        # print('down load every cost %.4f seconds\n' % (end2 - end1))
        # logging.warning('selectMapandDown:' + ' cost %.4f seconds\n' % (end2 - start))


    def read_background(self,propertyID):
        bkpath = self.codeRootdir+"/cache_/bk/" + str(propertyID) + "property.jpg"
        if not os.path.exists(bkpath):
            bkpath = self.codeRootdir+"/cache_/bk/default_white.jpg"
        try:
            image = cv2.imread(bkpath)
            if image is None:
                image = cv2.imread(self.codeRootdir + "/cache_/bk/default_white.jpg")
                im = cv2.resize(image, (self.img_width, self.img_height), interpolation=cv2.INTER_CUBIC)

            else:
                im = cv2.resize(image, (self.img_width, self.img_height), interpolation=cv2.INTER_CUBIC)
        except:
            image = cv2.imread("image/Finally.png")
            im = cv2.resize(image, (self.img_width, self.img_height), interpolation=cv2.INTER_CUBIC)

        imRGB = cv2.cvtColor(im,cv2.COLOR_BGR2RGB)

        return imRGB


    def selectCameraDet(self,propertyID,starttime,endtime):
        start = time.time()
        try:
            conn = mysql.connector.connect(host=self.dbHost, user=self.dbUserName, password=self.dbPwd, database=self.db)
            cursor = conn.cursor()
            command = "SELECT id,position_x,position_y FROM `camera` WHERE property_id=" + str(propertyID)

            cursor.execute(command)
        except:
            # logging.error('selectCameraDet:sql error')
            return 0

        cameraS = cursor.fetchall()

        length_site = len(cameraS)
        return_length = 0
        camera_list = []
        camera_det=[]
        for i in range(0,length_site):
            camera = cameraS[i]
            camID = camera[0]
            if not camera[1] is None:
                if not camera[2] is None:
                    try:
                        position_x = float(camera[1])
                        position_y = float(camera[2])
                        cam_t = [position_y,position_x]
                    except:
                        continue

                    try:
                        command = "SELECT SUM(detcount) FROM `heatmap` WHERE cameraID=" + str(
                            camID) + " and type=1" + " and timestamp between \'" + starttime + "\' and \'" + endtime + "\'"
                        cursor.execute(command)
                    except:
                        # logging.er/ror('selectCameraDet:sql error')
                        return 0

                    detcount = cursor.fetchone()
                    if not detcount is None:
                        length_det = len(detcount)

                        if length_det > 0:
                            # i_line = random.randint(0, length_line-1)
                            i_line = 0
                            detcount_t = detcount[0]
                            if detcount_t is None:
                                detcount_i = 0
                            else:
                                detcount_i = int(detcount_t)

                            if not detcount_i == 0:
                                camera_list.append(cam_t)
                                camera_det.append(detcount_i)





        end2 = time.time()
        # print('down load every cost %.4f seconds\n' % (end2 - end1))
        # logging.warning('selectCameraDet:' + ' cost %.4f seconds\n' % (end2 - start))

        conn.commit()
        cursor.close()
        conn.close()

        return camera_list,camera_det

    def cur_file_dir(self):
        path = sys.path[0]
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            return os.path.dirname(path)

    def h_topview(self,topimg, c_yx, detcount):

        h, w, _ = topimg.shape
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
        if not len(detcount) == 0:
            norm_det = normalize_v(np.asarray(detcount))
            # norm_det = norm_det+200

            detcount = normalize_v(np.asarray(detcount), 1000, 5000)
            # detcount = detcount + 100

            for yx, count, v in zip(c_yx, detcount, norm_det):
                r_x = int(np.floor(yx[1] * w))
                r_y = int(np.floor(yx[0] * h))
                mean = [r_x, r_y]
                cov = [[int(v)*30, 0], [0, int(v)*30]]
                factor = int(count)
                x, y = np.random.multivariate_normal(mean, cov, factor ** 2).T
                for rx, cy in zip(x, y):
                    rx = int(rx)
                    cy = int(cy)
                    if (0 <= rx < w) and (0 <= cy < h):
                        overlay[cy, rx] += 100
                    else:
                        continue

        # reverse image to the original size
        fig = plt.figure()
        fig.dpi = 200.
        fig.set_size_inches([w / fig.dpi, h / fig.dpi])
        ax = fig.add_axes([0., 0., 1., 1.])
        ax.imshow(topimg)

        overlay_clip = np.ma.masked_where(overlay < 0, overlay)
        all_im = plt.imshow(overlay_clip, alpha=0.4,cmap='rainbow')

        # color_bar
        cx = fig.add_axes([0.95, 0.5, 0.02, 0.3])  # colorbar show cite(x,y,w,h)
        fig.colorbar(all_im, cax=cx,alpha=0.4)
        plt.axis('off')

        fig.savefig(self.codeRootdir+"/cache_/result/map_topview.png", dpi=fig.dpi)

        return self.codeRootdir+"/cache_/result/map_topview.png"

    def h_topview_b(self,topimg, c_yx, detcount):

        h, w, _ = topimg.shape
        overlay = np.zeros([h, w], dtype=np.int)

        # detmin = int(50 * 1.0 / self.img_scale)
        # detmax = int(500 * 1.0/ self.img_scale)

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
        if not len(detcount) == 0:
            norm_det = normalize_v(np.asarray(detcount))
            # norm_det = norm_det+200

            detcount = normalize_v(np.asarray(detcount), 1000, 5000)
            detcount = detcount + 100

            for yx, count, v in zip(c_yx, detcount, norm_det):
                r_x = int(np.floor(yx[1] * w))
                r_y = int(np.floor(yx[0] * h))
                mean = [r_x, r_y]
                cov = [[int(v)*80, 0], [0, int(v)*80]]
                factor = int(count)
                x, y = np.random.multivariate_normal(mean, cov, factor ** 2).T
                for rx, cy in zip(x, y):
                    rx = int(rx)
                    cy = int(cy)
                    if (0 <= rx < w) and (0 <= cy < h):
                        overlay[cy, rx] += 100
                    else:
                        continue

        # reverse image to the original size
        fig = plt.figure()
        fig.dpi = 200.
        fig.set_size_inches([w / fig.dpi, h / fig.dpi])
        ax = fig.add_axes([0., 0., 1., 1.])
        ax.imshow(topimg)

        overlay_clip = np.ma.masked_where(overlay < 0, overlay)
        all_im = plt.imshow(overlay_clip, alpha=0.4,cmap='rainbow')

        # color_bar
        cx = fig.add_axes([0.95, 0.5, 0.02, 0.3])  # colorbar show cite(x,y,w,h)
        fig.colorbar(all_im, cax=cx,alpha=0.4)
        plt.axis('off')

        fig.savefig(self.codeRootdir+"/cache_/result/map_topview.png", dpi=fig.dpi)

        return self.codeRootdir+"/cache_/result/map_topview.png"

    def runHeat_topview(self,propertyID, starttime, endtime):
        start_d1 = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S')
        end_d1 = datetime.datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S')

        Heatpath = self.codeRootdir+"/cache_/result/map_topview_default.png"
        print "start1"
        try:
            if end_d1 > start_d1:
                self.selectMapandDown(propertyID)
                bkimg = self.read_background(propertyID)
                print "start2"
                # camera_list, camera_det = self.selectCameraDet(propertyID, startT, endT)

                camera_list = []
                camera_det = []

                #1
                cam_t = [0.1602, 0.0868]
                camera_list.append(cam_t)
                camera_det.append(6800)

                start = time.time()
                print "start3"
                Heatpath = self.h_topview(bkimg, camera_list, camera_det)
                print "start4"
                end2 = time.time()
                # logging.warning('demoHeat_topview: ' + 'compute cost %.4f seconds\n' % (end2 - start))

            else:
                print "End time need is greater than the start time. endtime > starttime "
                # logging.warning('demo_draw:' + ' End time need is greater than the start time. endtime > starttime')
        except:
            Heatpath = self.codeRootdir + "/cache_/result/map_topview_default.png"

        cam_bk = self.codeRootdir+"/cache_/bk/" + str(propertyID) + "property.jpg"

        return Heatpath

    def runHeat_topview_ford(self,propertyID):

        Heatpath = self.codeRootdir+"/Result"
        print "start1"
        bkimg = self.read_background(propertyID)
        print "start2"
        camera_list=[]
        camera_det=[]
        cam_t = [569.0/1724,165.0/1461.0]
        camera_list.append(cam_t)
        camera_det.append(65000000)


        start = time.time()
        print "start3"
        Heatpath = new_topview.run(bkimg, camera_list, camera_det, self.codeRootdir, self.winsize, self.sigma)
        print "start4"
        end2 = time.time()

        cam_bk = self.codeRootdir+"/cache_/bk/" + str(propertyID) + "property.jpg"

        return Heatpath

    def runHeat_topview_ford_wk2(self,propertyID, starttime, endtime):
        start_d1 = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S')
        end_d1 = datetime.datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S')

        startT = start_d1.strftime("%Y-%m-%d %H:%M:%S")
        endT = end_d1.strftime("%Y-%m-%d %H:%M:%S")

        Heatpath = self.codeRootdir+"/cache_/result/map_topview_default.png"
        print "start1"
        try:
            if end_d1 > start_d1:
                # self.selectMapandDown(propertyID)
                bkimg = self.read_background(propertyID)
                print "start2"
                camera_list, camera_det = self.selectCameraDet(propertyID, startT, endT)
                # camera_list=[]
                # camera_det=[]

                # # 1  y x
                cam_t = [0.9333,0.7672]
                camera_list.append(cam_t)
                camera_det.append(65000000)


                start = time.time()
                print "start3"
                # Heatpath = self.h_topview_b(bkimg, camera_list, camera_det)
                Heatpath = new_topview.run(bkimg, camera_list, camera_det, self.codeRootdir, self.winsize, self.sigma)
                print "start4"
                end2 = time.time()
                # logging.warning('demoHeat_topview: ' + 'compute cost %.4f seconds\n' % (end2 - start))

            else:
                print "End time need is greater than the start time. endtime > starttime "
                # logging.warning('demo_draw:' + ' End time need is greater than the start time. endtime > starttime')
        except:
            print "start555"
            Heatpath = self.codeRootdir + "/cache_/result/map_topview_default.png"

        cam_bk = self.codeRootdir+"/cache_/bk/" + str(propertyID) + "property.jpg"
        # if os.path.exists(cam_bk):
        #     os.remove(cam_bk)

        # print('compute cost %.4f seconds\n' % (end2 - start))

        return Heatpath

    def runHeat_topview_qujiang(self,propertyID, starttime, endtime):
        start_d1 = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S')
        end_d1 = datetime.datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S')

        startT = start_d1.strftime("%Y-%m-%d %H:%M:%S")
        endT = end_d1.strftime("%Y-%m-%d %H:%M:%S")

        Heatpath = self.codeRootdir+"/cache_/result/map_topview_default.png"
        print "start1"
        try:
            if end_d1 > start_d1:
                self.selectMapandDown(propertyID)
                bkimg = self.read_background(propertyID)
                print "start2"
                # camera_list, camera_det = self.selectCameraDet(propertyID, startT, endT)

                camera_list = []
                camera_det = []
                # cam_t = [position_y, position_x]
                # cam_t = [0.1573, 0.3562]
                # camera_list.append(cam_t)
                # camera_det.append(2000000)


                start = time.time()
                print "start3"
                Heatpath = self.h_topview(bkimg, camera_list, camera_det)
                print "start4"
                end2 = time.time()
                # logging.warning('demoHeat_topview: ' + 'compute cost %.4f seconds\n' % (end2 - start))

            else:
                print "End time need is greater than the start time. endtime > starttime "
                # logging.warning('demo_draw:' + ' End time need is greater than the start time. endtime > starttime')
        except:
            Heatpath = self.codeRootdir + "/cache_/result/map_topview_default.png"

        cam_bk = self.codeRootdir+"/cache_/bk/" + str(propertyID) + "property.jpg"
        # if os.path.exists(cam_bk):
        #     os.remove(cam_bk)

        # print('compute cost %.4f seconds\n' % (end2 - start))

        return Heatpath

    def runHeat_topview_everyday(self,propertyID, starttime, endtime):
        start_d1 = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S')
        end_d1 = datetime.datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S')

        startT = start_d1.strftime("%Y-%m-%d %H:%M:%S")
        endT = end_d1.strftime("%Y-%m-%d %H:%M:%S")

        Heatpath = self.codeRootdir+"/cache_/result/map_topview_default.png"
        print "start1"
        try:
            if end_d1 > start_d1:
                self.selectMapandDown(propertyID)
                bkimg = self.read_background(propertyID)
                print "start2"
                camera_list, camera_det = self.selectCameraDet(propertyID, startT, endT)

                # cam_t = [position_y, position_x]
                # cam_t = [0.1573, 0.3562]
                # camera_list.append(cam_t)
                # camera_det.append(2000000)
                #
                # cam_t = [0.1246, 0.4225]
                # camera_list.append(cam_t)
                # camera_det.append(3000000)
                #
                # cam_t = [0.1157, 0.5598]
                # camera_list.append(cam_t)
                # camera_det.append(1500000)
                #
                # cam_t = [0.1098, 0.3821]
                # camera_list.append(cam_t)
                # camera_det.append(5000000)

                cam_t = [0.1205, 0.0575]
                camera_list.append(cam_t)
                camera_det.append(2000000)

                cam_t = [0.4337, 0.1133]
                camera_list.append(cam_t)
                camera_det.append(3000000)

                cam_t = [0.1205, 0.2053]
                camera_list.append(cam_t)
                camera_det.append(1500000)

                cam_t = [0.2229, 0.0599]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.3584, 0.0476]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.4337, 0.0698]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.5030, 0.0386]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.5452, 0.1133]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.5813, 0.1297]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                # 2
                cam_t = [0.4127, 0.1667]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.4880, 0.1568]
                camera_list.append(cam_t)
                camera_det.append(6000000)

                cam_t = [0.4458, 0.1913]
                camera_list.append(cam_t)
                camera_det.append(7000000)

                cam_t = [0.5090, 0.2291]
                camera_list.append(cam_t)
                camera_det.append(6000000)

                cam_t = [0.7349, 0.1453]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.8163, 0.1946]
                camera_list.append(cam_t)
                camera_det.append(6000000)

                cam_t = [0.7681, 0.2397]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.1255, 0.2488]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.4488, 0.2578]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                # 10
                cam_t = [0.6988, 0.2701]
                camera_list.append(cam_t)
                camera_det.append(2000000)

                cam_t = [0.8524, 0.3333]
                camera_list.append(cam_t)
                camera_det.append(3000000)

                cam_t = [0.9494, 0.3580]
                camera_list.append(cam_t)
                camera_det.append(1500000)

                cam_t = [0.7741, 0.3604]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.1506, 0.3268]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.2651, 0.3637]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.1958, 0.4745]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.2831, 0.4573]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.3886, 0.4491]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                # 19
                cam_t = [0.4940, 0.4614]
                camera_list.append(cam_t)
                camera_det.append(2000000)

                cam_t = [0.1928, 0.5287]
                camera_list.append(cam_t)
                camera_det.append(3000000)

                cam_t = [0.2771, 0.5402]
                camera_list.append(cam_t)
                camera_det.append(1500000)

                cam_t = [0.3795, 0.5468]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.4910, 0.5386]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.6566, 0.5016]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.5994, 0.5567]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.9006, 0.5427]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.9006, 0.5698]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                # 28
                cam_t = [0.6747, 0.6535]
                camera_list.append(cam_t)
                camera_det.append(2000000)

                cam_t = [0.8283, 0.7430]
                camera_list.append(cam_t)
                camera_det.append(3000000)

                cam_t = [0.5813, 0.6593]
                camera_list.append(cam_t)
                camera_det.append(1500000)

                cam_t = [0.4428, 0.6166]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.3434, 0.5977]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.3765, 0.6700]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.1988, 0.6929]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.1988, 0.7496]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.0994, 0.7603]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                # 37
                cam_t = [0.3404, 0.6987]
                camera_list.append(cam_t)
                camera_det.append(2000000)

                cam_t = [0.5241, 0.7397]
                camera_list.append(cam_t)
                camera_det.append(3000000)

                cam_t = [0.7500, 0.7282]
                camera_list.append(cam_t)
                camera_det.append(1500000)

                cam_t = [0.7500, 0.7660]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.7952, 0.7890]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.8102, 0.8103]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.7741, 0.8481]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.5151, 0.7635]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.4849, 0.7824]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                # 46
                cam_t = [0.4398, 0.8120]
                camera_list.append(cam_t)
                camera_det.append(2000000)

                cam_t = [0.5090, 0.8465]
                camera_list.append(cam_t)
                camera_det.append(3000000)

                cam_t = [0.1777, 0.8112]
                camera_list.append(cam_t)
                camera_det.append(1500000)

                cam_t = [0.1900, 0.8793]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.4187, 0.8448]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.8253, 0.8637]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.7681, 0.9655]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.6777, 0.9819]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                cam_t = [0.1500, 0.8785]
                camera_list.append(cam_t)
                camera_det.append(5000000)

                # 55
                cam_t = [0.7711, 0.2463]
                camera_list.append(cam_t)
                camera_det.append(9000000)

                cam_t = [0.7259, 0.1429]
                camera_list.append(cam_t)
                camera_det.append(7000000)

                start = time.time()
                print "start3"
                Heatpath = self.h_topview(bkimg, camera_list, camera_det)
                print "start4"
                end2 = time.time()
                # logging.warning('demoHeat_topview: ' + 'compute cost %.4f seconds\n' % (end2 - start))

            else:
                print "End time need is greater than the start time. endtime > starttime "
                # logging.warning('demo_draw:' + ' End time need is greater than the start time. endtime > starttime')
        except:
            Heatpath = self.codeRootdir + "/cache_/result/map_topview_default.png"

        cam_bk = self.codeRootdir+"/cache_/bk/" + str(propertyID) + "property.jpg"
        # if os.path.exists(cam_bk):
        #     os.remove(cam_bk)

        # print('compute cost %.4f seconds\n' % (end2 - start))

        return Heatpath

    def runHeat_topview_old(self,propertyID, starttime, endtime):
        start_d1 = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S')
        end_d1 = datetime.datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S')

        startT = start_d1.strftime("%Y-%m-%d %H:%M:%S")
        endT = end_d1.strftime("%Y-%m-%d %H:%M:%S")

        Heatpath = self.codeRootdir+"/cache_/result/map_topview_default.png"
        print "start1"
        try:
            if end_d1 > start_d1:
                self.selectMapandDown(propertyID)
                bkimg = self.read_background(propertyID)
                print "start2"
                camera_list, camera_det = self.selectCameraDet(propertyID, startT, endT)


                start = time.time()
                print "start3"
                Heatpath = self.h_topview(bkimg, camera_list, camera_det)
                print "start4"
                end2 = time.time()
                # logging.warning('demoHeat_topview: ' + 'compute cost %.4f seconds\n' % (end2 - start))

            else:
                print "End time need is greater than the start time. endtime > starttime "
                # logging.warning('demo_draw:' + ' End time need is greater than the start time. endtime > starttime')
        except:
            Heatpath = self.codeRootdir + "/cache_/result/map_topview_default.png"

        cam_bk = self.codeRootdir+"/cache_/bk/" + str(propertyID) + "property.jpg"
        # if os.path.exists(cam_bk):
        #     os.remove(cam_bk)

        # print('compute cost %.4f seconds\n' % (end2 - start))

        return Heatpath




#coding:utf-8

from PIL import Image
import cv2
import numpy as np
from base_functions import load_img_by_gdal
import matplotlib.pyplot as plt
import gdal
import sys


# input_src_file = '/home/omnisky/PycharmProjects/data/test/paper/label/yujiang_test_label.png'
input_src_file ='/home/omnisky/PycharmProjects/data/originaldata/4bands/test/BJ200132D04320180302F_Clip1.png'
# clip_src_file = '/home/omnisky/PycharmProjects/data/test/paper/new/yujiang_test_label.png'
clip_src_file = '/home/omnisky/PycharmProjects/data/originaldata/4bands/test/BJ200132D04320180302F_17000l.png'

window_size = 10000
h_clip = 17000

if __name__=='__main__':
    # img = load_img_by_gdal(input_src_file)
    dataset = gdal.Open(input_src_file)
    if dataset==None:
        print("Open file failed:{}".format(input_src_file))
        sys.exit(-1)
    # assert (ret==0)
    height = dataset.RasterYSize
    width = dataset.RasterXSize
    im_bands = dataset.RasterCount
    d_type = dataset.GetRasterBand(1).DataType
    img = dataset.ReadAsArray(0,0,width,height)
    del dataset

    # x = np.random.randint(0, height-window_size-1)
    # y = np.random.randint(0, width - window_size - 1)
    x =0
    y=0

    if im_bands ==1:
        output_img = img[x:x + window_size, y:y + window_size]
        # output_img = img[100:5000+100, 100:5500+100]
        output_img = np.array(output_img, np.uint16)
        # output_img[output_img > 2] = 127
        tp = output_img
        tp[tp>2]=0
        print(np.unique(tp))
        output_img = np.array(output_img, np.uint8)
        plt.imshow(output_img)
        plt.show()
        cv2.imwrite(clip_src_file, output_img)  # for label clip
    else:
        # output_img = img[:, x:x + window_size, y:y + window_size]
        output_img = img[:, :, :h_clip]
        plt.imshow(output_img[0])
        plt.show()
        driver = gdal.GetDriverByName("GTiff")
        # outdataset = driver.Create(clip_src_file, window_size, window_size, im_bands, d_type)
        outdataset = driver.Create(clip_src_file, h_clip, height, im_bands, d_type)
        if outdataset == None:
            print("create dataset failed!\n")
            sys.exit(-2)
        if im_bands == 1:
            outdataset.GetRasterBand(1).WriteArray(output_img)
        else:
            for i in range(im_bands):
                outdataset.GetRasterBand(i + 1).WriteArray(output_img[i])
        del outdataset









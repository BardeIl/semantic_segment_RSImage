# coding=utf-8

import cv2
import random
import os
import numpy as np
from tqdm import tqdm
import sys

seed = 1
np.random.seed(seed)

img_w = 256
img_h = 256

image_sets = ['1.png', '2.png', '3.png', '4.png', '5.png']

FLAG_USING_UNET = True
segnet_labels = [0, 1, 2, 3, 4]
unet_labels = [0, 1]

input_src_path = '../data/originaldata/unet/roads/src/'
input_label_path = '../data/originaldata/unet/roads/label/'
output_path = '../data/traindata/unet/roads/'

"""for segnet train data"""
# source_path = '../data/originaldata/segnet/'
# output_path = '../data/traindata/segnet/'


def gamma_transform(img, gamma):
    gamma_table = [np.power(x / 255.0, gamma) * 255.0 for x in range(256)]
    gamma_table = np.round(np.array(gamma_table)).astype(np.uint8)
    return cv2.LUT(img, gamma_table)

def gamma_transform(img, gamma):
    gamma_table = [np.power(x / 255.0, gamma) * 255.0 for x in range(256)]
    gamma_table = np.round(np.array(gamma_table)).astype(np.uint8)
    return cv2.LUT(img, gamma_table)

def random_gamma_transform(img, gamma_vari):
    log_gamma_vari = np.log(gamma_vari)
    alpha = np.random.uniform(-log_gamma_vari, log_gamma_vari)
    gamma = np.exp(alpha)
    return gamma_transform(img, gamma)


def rotate(xb, yb, angle):
    M_rotate = cv2.getRotationMatrix2D((img_w / 2, img_h / 2), angle, 1)
    xb = cv2.warpAffine(xb, M_rotate, (img_w, img_h))
    yb = cv2.warpAffine(yb, M_rotate, (img_w, img_h))
    return xb, yb


def blur(img):
    img = cv2.blur(img, (3, 3));
    return img


def add_noise(img):
    for i in range(200):  # 添加点噪声
        temp_x = np.random.randint(0, img.shape[0])
        temp_y = np.random.randint(0, img.shape[1])
        img[temp_x][temp_y] = 255
    return img


def data_augment(xb, yb):
    if np.random.random() < 0.25:
        xb, yb = rotate(xb, yb, 90)
    if np.random.random() < 0.25:
        xb, yb = rotate(xb, yb, 180)
    if np.random.random() < 0.25:
        xb, yb = rotate(xb, yb, 270)
    if np.random.random() < 0.25:
        xb = cv2.flip(xb, 1)  # flipcode > 0：沿y轴翻转
        yb = cv2.flip(yb, 1)

    if np.random.random() < 0.25:
        xb = random_gamma_transform(xb, 1.0)

    if np.random.random() < 0.25:
        xb = blur(xb)

    if np.random.random() < 0.2:
        xb = add_noise(xb)

    return xb, yb

"""check some invalid labels or NoData values"""
def check_invalid_labels(img):

    valid_labels=[0,1]

    if FLAG_USING_UNET:
        valid_labels = unet_labels
    else:
        valid_labels = segnet_labels

    row, column = img.shape
    for i in range(row):
        for j in range(column):
            assert (img[i,j] in valid_labels)


""" check the size of src_img and label_img"""
def check_src_label_size(srcimg, labelimg):
    row_src, column_src,_ = srcimg.shape
    row_label, column_label = labelimg.shape
    assert (row_src==row_label and column_src==column_src)



def get_file(file_path, file_type='.png'):
    L=[]
    for root,dirs,files in os.walk(file_path):
        for file in files:
            if os.path.splitext(file)[1]==file_type:
                L.append(os.path.join(root,file))
    return L




def creat_dataset(image_num=50000, mode='original'):

    print('creating dataset...')

    print('\ncreating dataset...')


    src_files = get_file(input_src_path)
    image_each = image_num/len(src_files)

    # image_each = image_num / len(image_sets)

    g_count = 0
    # for i in tqdm(range(len(image_sets))):
    for scr_file in tqdm(src_files):
        count = 0
        # src_img = cv2.imread(source_path + 'src/' + image_sets[i])  # 3 channels
        # label_img = cv2.imread(source_path + 'label/' + image_sets[i], cv2.IMREAD_GRAYSCALE)  # single channel

        src_img = cv2.imread(scr_file)
        label_file = input_label_path+os.path.split(scr_file)[1]

        if not os.path.isfile(label_file):
            print("Have no file:".format(label_file))
            sys.exit(-1)

        label_img = cv2.imread(label_file, cv2.IMREAD_GRAYSCALE)

        check_src_label_size(src_img, label_img)

        X_height, X_width, _ = src_img.shape

        while count < image_each:
            random_width = random.randint(0, X_width - img_w - 1)
            random_height = random.randint(0, X_height - img_h - 1)
            src_roi = src_img[random_height: random_height + img_h, random_width: random_width + img_w, :]
            label_roi = label_img[random_height: random_height + img_h, random_width: random_width + img_w]

            """check some invalid labels or NoData values"""
            check_invalid_labels(label_roi)

            """Cut down the pure background image with 80% probability"""
            if len(np.unique(label_roi)) < 2:
                if np.unique(label_roi)[0] ==0:
                    if np.random.random()< 0.8:
                        continue

            if mode == 'augment':
                src_roi, label_roi = data_augment(src_roi, label_roi)

            visualize = np.zeros((256, 256)).astype(np.uint8)
            visualize = label_roi * 50

            cv2.imwrite((output_path + 'visualize/%d.png' % g_count), visualize)
            cv2.imwrite((output_path + 'src/%d.png' % g_count), src_roi)
            cv2.imwrite((output_path + 'label/%d.png' % g_count), label_roi)
            count += 1
            g_count += 1


if __name__ == '__main__':
    creat_dataset(mode='augment')
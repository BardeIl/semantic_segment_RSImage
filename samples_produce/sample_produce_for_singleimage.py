# coding=utf-8

import cv2
import random
import os
import numpy as np
from tqdm import tqdm
import sys

from ulitities.base_functions import get_file

# seed = 1
# np.random.seed(seed)

img_w = 256
img_h = 256

valid_labels=[0,1,2]

FLAG_BINARY = False
# FLAG_BINARY = True



label_file = '../../data/originaldata/sat_urban_rgb/label/shuangliu_11.png'
src_file = '../../data/originaldata/sat_urban_rgb/src/shuangliu_11.png'


output_base = '../../data/traindata/sat_urban_rgb/'
# output_label_path = os.path.join(output_path, 'label')


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


""" check the size of src_img and label_img"""
def check_src_label_size(srcimg, labelimg):
    row_src, column_src,_ = srcimg.shape
    row_label, column_label = labelimg.shape
    assert (row_src==row_label and column_src==column_src)


"""check some invalid labels or NoData values"""
def check_invalid_labels(img, labels):
    local_labels = np.unique(img)
    for ll in local_labels:
        assert(ll in labels)


def creat_dataset_multiclass(labelfile, srcfile, base_path, image_num=5000, mode='original'):

    print('\ncreating dataset...')
    target_dir = os.path.join(base_path, 'label')
    if not os.path.isdir(target_dir):
        print("samples save path does not exist: {}".format(target_dir))
        sys.exit(-3)

    _, baseNO = get_file(target_dir)

    g_count = baseNO+1

    count = 0

    src_img = cv2.imread(src_file)

    label_img = cv2.imread(label_file, cv2.IMREAD_GRAYSCALE)

    """Check image size and invalid labels"""
    check_src_label_size(src_img, label_img)
    # check_invalid_labels(label_img, valid_labels)

    X_height, X_width, _ = src_img.shape

    while count < image_num:
        random_width = random.randint(0, X_width - img_w - 1)
        random_height = random.randint(0, X_height - img_h - 1)
        src_roi = src_img[random_height: random_height + img_h, random_width: random_width + img_w, :]
        label_roi = label_img[random_height: random_height + img_h, random_width: random_width + img_w]

        """ignore nodata area"""
        FLAG_HAS_NODATA = False
        tmp = np.unique(label_roi)
        for tt in tmp:
            if tt not in valid_labels:
                FLAG_HAS_NODATA = True
                continue

        if FLAG_HAS_NODATA == True:
            continue

        """ignore whole background area"""
        if len(np.unique(label_roi)) < 2:
            if 0 in np.unique(label_roi):
                continue

        if mode == 'augment':
            src_roi, label_roi = data_augment(src_roi, label_roi)

        visualize = label_roi * 50

        cv2.imwrite((base_path + '/visualize/%d.png' % g_count), visualize)
        cv2.imwrite((base_path + '/src/%d.png' % g_count), src_roi)
        cv2.imwrite((base_path + '/label/%d.png' % g_count), label_roi)
        count += 1
        g_count += 1


def creat_dataset_binary(labelfile, srcfile, base_path, image_num=5000, mode='original'):
    print('\ncreating dataset...')
    target_dir = os.path.join(base_path, 'roads', 'label')
    if not os.path.isdir(target_dir):
        print("samples save path does not exist: {}".format(target_dir))
        sys.exit(-3)

    _, baseNO= get_file(target_dir)

    src_img = cv2.imread(srcfile)

    label_img = cv2.imread(labelfile, cv2.IMREAD_GRAYSCALE)

    """Check image size and invalid labels"""
    check_src_label_size(src_img, label_img)
    # check_invalid_labels(label_img, valid_labels)

    X_height, X_width, _ = src_img.shape

    print("\n1: produce road labels---------------------")
    index = np.where(label_img == 1)  # 1: roads
    road_label = np.zeros((X_height, X_width), np.uint8)
    road_label[index] = 1

    print(np.unique(road_label))
    g_count = baseNO +1
    count = 0
    while count < image_num:
        random_width = random.randint(0, X_width - img_w - 1)
        random_height = random.randint(0, X_height - img_h - 1)
        src_roi = src_img[random_height: random_height + img_h, random_width: random_width + img_w, :]
        label_roi = road_label[random_height: random_height + img_h, random_width: random_width + img_w]

        """ignore nodata area"""
        FLAG_HAS_NODATA = False
        tmp = np.unique(label_img[random_height: random_height + img_h, random_width: random_width + img_w])
        for tt in tmp:
            if tt not in valid_labels:
                FLAG_HAS_NODATA = True
                continue

        if FLAG_HAS_NODATA == True:
            continue

        """ignore whole background area"""
        if len(np.unique(label_roi)) < 2:
            if 0 in np.unique(label_roi):
                continue

        if mode == 'augment':
            src_roi, label_roi = data_augment(src_roi, label_roi)

        visualize = label_roi * 50


        cv2.imwrite((base_path + '/roads/visualize/%d.png' % g_count), visualize)
        cv2.imwrite((base_path + '/roads/src/%d.png' % g_count), src_roi)
        cv2.imwrite((base_path + '/roads/label/%d.png' % g_count), label_roi)
        count += 1
        g_count += 1

    print("\n2: produce buildings labels---------------------")
    index = np.where(label_img == 2)  # 1: buildings
    building_label = np.zeros((X_height, X_width), np.uint8)
    building_label[index] = 1

    target_dir = os.path.join(base_path, 'buildings', 'label')
    if not os.path.isdir(target_dir):
        print("samples save path does not exist: {}".format(target_dir))
        sys.exit(-3)

    _, baseNO = get_file(target_dir)

    g_count = baseNO + 1
    count = 0
    while count < image_num:
        random_width = random.randint(0, X_width - img_w - 1)
        random_height = random.randint(0, X_height - img_h - 1)
        src_roi = src_img[random_height: random_height + img_h, random_width: random_width + img_w, :]
        label_roi = building_label[random_height: random_height + img_h, random_width: random_width + img_w]

        """ignore nodata area"""
        FLAG_HAS_NODATA = False
        tmp = np.unique(label_img[random_height: random_height + img_h, random_width: random_width + img_w])
        for tt in tmp:
            if tt not in valid_labels:
                FLAG_HAS_NODATA = True
                continue

        if FLAG_HAS_NODATA == True:
            continue

        """ignore whole background area"""
        if len(np.unique(label_roi)) < 2:
            if 0 in np.unique(label_roi):
                continue

        if mode == 'augment':
            src_roi, label_roi = data_augment(src_roi, label_roi)

        visualize = label_roi * 50

        cv2.imwrite((base_path + '/buildings/visualize/%d.png' % g_count), visualize)
        cv2.imwrite((base_path + '/buildings/src/%d.png' % g_count), src_roi)
        cv2.imwrite((base_path + '/buildings/label/%d.png' % g_count), label_roi)
        count += 1
        g_count += 1

if __name__ == '__main__':
    if not os.path.isfile(label_file):
        print("label file does not exist: {}".format(label_file))
        sys.exit(-1)

    if not os.path.isfile(src_file):
        print("src file does not exist: {}".format(src_file))
        sys.exit(-2)

    if FLAG_BINARY == True:
        output_path = os.path.join(output_base, 'binary')
    else:
        output_path = os.path.join(output_base, 'multiclass')


    if FLAG_BINARY==True:
        print("Produce labels for binary classification")
        creat_dataset_binary(label_file, src_file, output_path, 5000, mode='augment')
    else:
        print("produce labels for multiclass")
        creat_dataset_multiclass(label_file,src_file, output_path, 10000, mode='augment')
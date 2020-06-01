    # -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 08:50:23 2018

@author: zjj
"""
from __future__ import division
import os
from PIL import Image
from torch.utils import data
import csv
from imblearn.over_sampling import RandomOverSampler
import numpy as np
from torchvision import transforms as T
import torch
from torch.utils.data import DataLoader


def get_processed_datas(list_root):
    txt_list = open(list_root, 'r').read().splitlines()
    sample_num = len(txt_list)
    image_list = ['' for l in range(sample_num)]
    label_list = ['' for l in range(sample_num)]
    name_list = ['' for l in range(sample_num)]
    for i in range(sample_num):
        s = txt_list[i].split(' ')
        image_list[i] = s[0]
        name_list[i] = os.path.basename(os.path.splitext(s[0])[0])
        if open(s[1], 'r').read()[:2]=='10':   #yes
            label_list[i] = 0
        else:
            label_list[i] = 1
    return image_list, label_list, name_list


def upsample(data,label):
    ros = RandomOverSampler(random_state=0)
    data = list(np.array(data).reshape(-1,1))
    X_resampled, y_resampled = ros.fit_sample(data, label)
    X_resampled, y_resampled = list(X_resampled.reshape(-1)), list(y_resampled)
    return X_resampled, list(y_resampled)


class Dataset2(data.Dataset):
    def __init__(self,imgs,labels,transforms=None):
        self.imgs = imgs
        self.labels = labels
        self.transforms = transforms

    def __getitem__(self,index):
        img_path = self.imgs[index]
        img = Image.open(img_path)
        label = self.labels[index]
        if self.transforms:
            img = self.transforms(img)
        return img, label
    
    def __len__(self):
        return len(self.imgs)



### include cropped img
def get_processed_datas2(list_root):
    txt_list = open(list_root, 'r').read().splitlines()
    sample_num = len(txt_list)
    image_list = ['' for l in range(sample_num)]
    cropimage_list = ['' for l in range(sample_num)]
    label_list = ['' for l in range(sample_num)]
    name_list = ['' for l in range(sample_num)]
    for i in range(sample_num):
        s = txt_list[i].split(' ')
        image_list[i] = s[0]
        cropimage_list[i] = s[0].replace('images', 'crop_images')
        name_list[i] = os.path.basename(os.path.splitext(s[0])[0])
        if open(s[1], 'r').read()[:2]=='10':   #yes
            label_list[i] = 0
        else:
            label_list[i] = 1
    return image_list, label_list, name_list, cropimage_list

def upsample2(data,label,cdata):
    ros = RandomOverSampler(random_state=0)
    data1 = np.array(data).reshape(-1,1)
    data2 = np.array(cdata).reshape(-1,1)
    data = list(np.concatenate((data1,data2),axis=1))
    X_resampled, y_resampled = ros.fit_sample(data, label)
    X_resampled1 = list(X_resampled[:,0]) #images
    X_resampled2 = list(X_resampled[:,1]) #crop images
    y_resampled = list(y_resampled)
    return X_resampled1, y_resampled, X_resampled2


class Dataset3(data.Dataset):
    def __init__(self,imgs,labels,cropimgs,transforms=None):
        self.imgs = imgs
        self.labels = labels
        self.cropimgs = cropimgs
        self.transforms = transforms

    def __getitem__(self,index):
        img_path = self.imgs[index]
        img = Image.open(img_path)
        label = self.labels[index]
        cropimg_path = self.cropimgs[index]
        cropimg = Image.open(cropimg_path)
        if self.transforms:
            img = self.transforms(img)
            cropimg = self.transforms(cropimg)
        return img, label, cropimg
    
    def __len__(self):
        return len(self.imgs)
#### #######################################


### include cam
def get_processed_datas3(list_root):
    txt_list = open(list_root, 'r').read().splitlines()
    sample_num = len(txt_list)
    image_list = ['' for l in range(sample_num)]
    cropimage_list = ['' for l in range(sample_num)]
    label_list = ['' for l in range(sample_num)]
    name_list = ['' for l in range(sample_num)]
    for i in range(sample_num):
        s = txt_list[i].split(' ')
        image_list[i] = s[0]
        cropimage_list[i] = s[0].replace('images', 'cam').replace('.jpg','.npz')
        name_list[i] = os.path.basename(os.path.splitext(s[0])[0])
        if open(s[1], 'r').read()[:2]=='10':   #yes
            label_list[i] = 0
        else:
            label_list[i] = 1
    return image_list, label_list, name_list, cropimage_list


class Dataset4(data.Dataset):
    def __init__(self,imgs,labels,cropimgs,transforms=None):
        self.imgs = imgs
        self.labels = labels
        self.cropimgs = cropimgs
        self.transforms = transforms

    def __getitem__(self,index):
        img_path = self.imgs[index]
        img = Image.open(img_path)
        label = self.labels[index]
        cropimg_path = self.cropimgs[index]
        cropimg = np.load(cropimg_path)['cam']
        if self.transforms:
            img = self.transforms(img)

        cropimg = torch.from_numpy(cropimg)
        return img, label, cropimg
    
    def __len__(self):
        return len(self.imgs)
#### #######################################


class Test_Dataset(data.Dataset):
   
    def __init__(self,imgs,transforms=None):
        self.imgs = imgs
        self.transforms = transforms

    def __getitem__(self,index):
        img_path = self.imgs[index]
        img = Image.open(img_path)
        if self.transforms:
            img = self.transforms(img)
        return img       

    def __len__(self):
        return len(self.imgs)



def get_mean_std(dataset, ratio=0.01):
    """Get mean and std by sample ratio
    """
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=int(len(dataset)*ratio), 
                                             shuffle=True, num_workers=10)
    train = iter(dataloader).next()[0]   # 一个batch的数据
    mean = np.mean(train.numpy(), axis=(0,2,3))
    std = np.std(train.numpy(), axis=(0,2,3))
    return mean, std




##### triplet dataset ############
from tqdm import tqdm
class TripletFaceDataset(data.Dataset):
    def __init__(self, imgs, labels, n_triplets, transform=None):
        self.n_triplets = n_triplets
        self.imgs = imgs
        self.labels = labels
        self.transform = transform
        print('Generating {} triplets'.format(self.n_triplets))
        self.training_triplets = self.generate_triplets(self.imgs, self.labels, self.n_triplets, 2)


    @staticmethod
    def generate_triplets(imgs, labels, num_triplets, n_classes):
        def create_indices(_imgs, _labels):
            inds = dict()
            for idx in range(len(_imgs)):
                img_path = _imgs[idx]
                label = _labels[idx]
                if label not in inds:
                    inds[label] = []
                inds[label].append(img_path)
            return inds


        triplets = []
        # Indices = array of labels and each label is an array of indices
        indices = create_indices(imgs, labels)

        for x in tqdm(range(num_triplets)):
            c1 = np.random.randint(0, n_classes)
            c2 = np.random.randint(0, n_classes)
            while len(indices[c1]) < 2:
                c1 = np.random.randint(0, n_classes)

            while c1 == c2:
                c2 = np.random.randint(0, n_classes)
            if len(indices[c1]) == 2:  # hack to speed up process
                n1, n2 = 0, 1
            else:
                n1 = np.random.randint(0, len(indices[c1]))
                n2 = np.random.randint(0, len(indices[c1]))
                while n1 == n2:
                    n2 = np.random.randint(0, len(indices[c1]))
            if len(indices[c2]) ==1:
                n3 = 0
            else:
                n3 = np.random.randint(0, len(indices[c2]))

            triplets.append([indices[c1][n1], indices[c1][n2], indices[c2][n3],c1,c2])
        return triplets


    def __getitem__(self, index):

        '''
        Args:
            index: Index of the triplet or the matches - not of a single image
        Returns:
        '''

        def transform(img_path):
            """Convert image into numpy array and apply transformation
               Doing this so that it is consistent with all other datasets
               to return a PIL Image.
            """

            img = Image.open(img_path)
            return self.transform(img)

        # Get the index of each image in the triplet
        a, p, n,c1,c2 = self.training_triplets[index]

        # transform images if required
        img_a, img_p, img_n = transform(a), transform(p), transform(n)

        return img_a, img_p, img_n,c1,c2



    def __len__(self):
        return len(self.training_triplets)




if __name__ == '__main__':
    #### calculate mean and std of the dataset
    # list_root = '/data/zjj/focus/lists/face/training.txt'
    # imgs,labels,name_list = get_processed_datas(list_root)
    # imgs,labels = upsample(imgs,labels)
    # transform = T.ToTensor()
    # dataset = Dataset2(imgs,labels,transforms=transform)
    # mean, std = get_mean_std(dataset, ratio=0.1)
    # print('mean:', mean)
    # print('std:', std)
# mean: [0.44518387 0.38825074 0.34499285]
# std: [0.29860568 0.27573788 0.27095458]


    #### construct triplet list
    make_triplet_list()










import os
import random
import argparse


def voc_segmentation(segfilepath, saveBasePath, trainval_percent=0.9, train_percent=0.8):
    random.seed(0)
    path = os.path.join(segfilepath, "mask_output")
    temp_seg = os.listdir(path)
    total_seg = [seg for seg in temp_seg if seg.endswith(".png")]

    num = len(total_seg)
    list_indices = list(range(num))
    tv = int(num * trainval_percent)
    tr = int(tv * train_percent)
    trainval = random.sample(list_indices, tv)
    train = random.sample(trainval, tr)

    print("train and val size", tv)
    print("train size", tr)

    with open(os.path.join(saveBasePath, 'trainval.txt'), 'w') as ftrainval, \
            open(os.path.join(saveBasePath, 'test.txt'), 'w') as ftest, \
            open(os.path.join(saveBasePath, 'train.txt'), 'w') as ftrain, \
            open(os.path.join(saveBasePath, 'val.txt'), 'w') as fval:

        for i in list_indices:
            name = total_seg[i][:-4] + '\n'
            if i in trainval:
                ftrainval.write(name)
                if i in train:
                    ftrain.write(name)
                else:
                    fval.write(name)
            else:
                ftest.write(name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='VOC Segmentation')
    parser.add_argument('--segfilepath', type=str, required=True, help='Path to segmentation files')
    parser.add_argument('--saveBasePath', type=str, required=True, help='Path to save output files')
    parser.add_argument('--trainval_percent', type=float, default=0.9, help='Percentage of trainval split')
    parser.add_argument('--train_percent', type=float, default=0.8, help='Percentage of train split from trainval')

    args = parser.parse_args()

    voc_segmentation(args.segfilepath, args.saveBasePath, args.trainval_percent, args.train_percent)

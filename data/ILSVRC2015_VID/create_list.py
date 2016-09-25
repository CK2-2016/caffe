import os
from random import shuffle
import cv2

home_dir = os.path.expanduser('~')
cur_dir = os.path.dirname(os.path.realpath(__file__))
# The root directory which holds all information of the dataset

data_dir = '{}/datasets/ILSVRC2015'.format(home_dir)
imageset_dir = 'ImageSets/VID'
image_dir = 'Data/VID'
image_type = 'JPEG'

anno_dir = 'Annotations/VID'
anno_type = 'xml'


def get_image_size_by_imread(im_file):
    im = cv2.imread(im_file)
    return im.shape[0], im.shape[1]


def process_trainval_set(subset, target_file, image_sets, ignore_cache=True):
    """
    For trainval set, they have ground truth files
    Therefore, the result text file should contain both image path & anno path
    """
    if ignore_cache or not os.path.exists(target_file):
        im_files = []
        anno_files = []
        for dataset in image_sets:
            print 'Processed {}'.format(dataset)
            imageset_file = os.path.join(data_dir, imageset_dir, dataset + '.txt')
            f = open(imageset_file, 'r')

            lines = f.readlines()
            if subset == 'val' or subset == 'test':
                lines = [line.strip('\n').split('/')[0] for line in lines]
                folder_names = sorted(list(set(lines)))
            else:
                folder_names = [line.strip('\n').split(' ')[0] for line in lines]

            for folder_name in folder_names:
                anno_folder = os.path.join(data_dir, anno_dir, subset, folder_name)
                anno_file_names = sorted(os.listdir(anno_folder))
                for anno_file_name in anno_file_names:
                    file_name = anno_file_name.split('.')[0]
                    im_file = os.path.join(image_dir, subset, folder_name, file_name + '.' + image_type)
                    anno_file = os.path.join(anno_dir, subset, folder_name, file_name + '.' + anno_type)
                    assert os.path.exists(os.path.join(data_dir, im_file))
                    assert os.path.exists(os.path.join(data_dir, anno_file))
                    im_files.append(im_file)
                    anno_files.append(anno_file)
        # Shuffle among all the images
        idx = range(len(im_files))
        shuffle(idx)
        with open(target_file, 'w') as f:
            for i in idx:
                f.write('{} {}\n'.format(im_files[i], anno_files[i]))


def process_test_set(subset, target_file, image_sets, ignore_cache=True):
    """
    For test set, they don't have ground truth file
    And we also need a list contain image sizes
    """
    if ignore_cache or not os.path.exists(target_file):
        im_files = []
        im_width_list = []
        im_height_list = []
        target_name_size_file = os.path.join(cur_dir, subset + '_name_size.txt')

        for dataset in image_sets:
            print 'Processed {}'.format(dataset)
            imageset_file = os.path.join(data_dir, imageset_dir, dataset + '.txt')
            f = open(imageset_file, 'r')
            lines = f.readlines()
            cnt = 0
            for line in lines:
                cnt += 1
                if cnt % 1000 == 0:
                    print '{} / {}'.format(cnt, len(lines))
                im_name = line.strip('\n').split(' ')[0]
                # Note here the im_file doesn't contain data_dir
                im_file = os.path.join(image_dir, subset, im_name + '.' + image_type)
                height, width = get_image_size_by_imread(os.path.join(data_dir, im_file))
                im_files.append(im_file)
                im_width_list.append(width)
                im_height_list.append(height)

        with open(target_file, 'w') as f:
            for i in xrange(len(im_files)):
                f.write('{} 0\n'.format(im_files[i]))
        with open(target_name_size_file, 'w') as f:
            for i in xrange(len(im_width_list)):
                f.write('{} {} {}\n'.format(im_files[i], im_height_list[i], im_width_list[i]))


# define target file names
train_list_file = '{}/train.txt'.format(cur_dir)
val_list_file = '{}/val.txt'.format(cur_dir)
val_name_size_file = '{}/val_name_size.txt'.format(cur_dir)

train_im_sets = ['train_1', 'train_2', 'train_3', 'train_4', 'train_5',
                 'train_6', 'train_7', 'train_8', 'train_9', 'train_10',
                 'train_11', 'train_12', 'train_13', 'train_14', 'train_15',
                 'train_16', 'train_17', 'train_18', 'train_19', 'train_20',
                 'train_21', 'train_22', 'train_23', 'train_24', 'train_25',
                 'train_26', 'train_27', 'train_28', 'train_29', 'train_30']

process_trainval_set('train', train_list_file, train_im_sets, ignore_cache=False)

val_im_sets = ['val']

process_test_set('val', val_list_file, val_im_sets, ignore_cache=False)

process_trainval_set('val', val_list_file, val_im_sets, ignore_cache=True)
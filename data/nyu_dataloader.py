from torch.utils.data import Dataset
from PIL import Image
import numpy as np
from data.common import get_patch,arugment
 

class NYU_v2_datset(Dataset):
    """NYUDataset."""

    def __init__(self, root_dir, scale=8, train=True, transform=None):
        """
        Args:
            root_dir (string): Directory with all the images.
            scale (float): dataset scale
            train (bool): train or test
            transform (callable, optional): Optional transform to be applied on a sample.

        """
        self.root_dir = root_dir
        self.transform = transform
        self.scale = scale
        self.train = train

        if train:
            self.depths = np.load('%s/train_depth_split.npy' % root_dir)
            self.images = np.load('%s/train_images_split.npy' % root_dir)
            self.segs = np.load('%s/train_Seg.npy' % root_dir)
            self.norms = np.load('%s/train_Normal.npy' % root_dir)
        else:
            self.depths = np.load('%s/test_depth.npy' % root_dir)
            self.images = np.load('%s/test_images_v2.npy' % root_dir)
            self.segs = np.load('%s/test_Seg.npy' % root_dir)
            self.norms = np.load('%s/test_Normal.npy' % root_dir)

    def __len__(self):
        return self.depths.shape[0]

    def __getitem__(self, idx):
        depth = self.depths[idx]
        image = self.images[idx]
        seg = self.segs[idx]
        ns = self.norms[idx]
        if self.train:
            image, depth,seg, ns = get_patch(img=image, gt=np.expand_dims(depth, 2), seg=np.expand_dims(seg, 2), ns=ns,
                                          patch_size=256)
            image, depth,seg, ns = arugment(img=image, gt=depth, seg=seg, ns=ns)
        h, w = depth.shape[:2]
        s = self.scale
        lr = np.array(Image.fromarray(depth.squeeze()).resize((w // s, h // s), Image.BICUBIC))
            
        if self.transform:
            image = self.transform(image).float()
            seg = self.transform(seg).float()
            ns = self.transform(ns).float()
            depth = self.transform(depth).float()
            lr = self.transform(np.expand_dims(lr, 2)).float()

        sample = {'guidance': image, 'lr': lr, 'gt': depth, 'seg': seg, 'ns': ns}

        return sample

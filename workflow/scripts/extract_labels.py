import h5py
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
import skimage.io as io
import fire

def get_slice(x):
    """
    Gets tuple of slices from string
    :param x a string representing a slice tuple
    :return: the slice tuple

    Example:
    >> get_slice('[0:1,2:4,4:6]')
    (slice(0,1,None), slice(2,4,None),slice(4,6,None)
    """
    s = [slice(*[int(i) for i in v.strip('[]').split(':')]) for v in x.split(',')]
    return s

def extract_labels(file_path_ilp, fol_path_out,
                   suffix='_label.tiff',
                   default_img_shape=(250,250,1)):
    """
    Extracts the labels from an ilastik project
    :param file_path_ilp: Path to ilastik file
    :param fol_path_out: Output path where labels should be written to
    :param default_img_shape: Default size of the images
    :return: True in case of success
    """
    fol_path_out = Path(fol_path_out)
    fol_path_out.mkdir(parents=True, exist_ok=True)
    with h5py.File(file_path_ilp, 'r') as f:
        labels = f['/PixelClassification/LabelSets']
        lanes = f['Input Data']['infos']
        fns = []
        for label, lane in zip(labels.values(),lanes.values()):
            name = lane['Raw Data/nickname'][()].decode('UTF-8')
            fns.append(name)
            if 'shape' in lane['Raw Data'].keys():
                shape = list(lane[('Raw Data/shape')])[:2]+[1]
            else:
                shape = default_img_shape
            # This assumes not more than 255 labels were used
            labarr = np.zeros(shape, dtype='uint8')
            for val in label.values():
                s = get_slice(val.attrs['blockSlice'])
                labarr[s] += val[:]
            if labarr is None:
                continue
            if np.sum(labarr[:]>0):
                io.imsave(fol_path_out / f'{name}{suffix}',
                          labarr)

if __name__ == '__main__':
  fire.Fire(extract_labels)

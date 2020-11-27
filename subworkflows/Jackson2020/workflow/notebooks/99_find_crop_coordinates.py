# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.5.2
#   kernelspec:
#     display_name: Python [conda env:multiplexed_segmentation]
#     language: python
#     name: conda-env-multiplexed_segmentation-py
# ---

# %%
import tifffile
from pathlib import Path as P
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from skimage.feature import match_template

import pandas as pd


import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 300


# %%
class C:
    fol_path_crops = P('/home/vitoz/Data/SegData/basel_zuri/ilastik_random_combined')
    fol_path_full = P('/home/vitoz/Data/SegData/basel_zuri/analysis_stacks')


# %%
file_paths_crop = list(C.fol_path_crops.glob('*_ilastik2_crop250.tiff'))
file_paths_full = [C.fol_path_full / fn.name.replace('_crop250.tiff', '.tiff') for fn in file_paths_crop]

# %%

# %%
file_paths_full[0]

# %%
assert all([fn.exists() for fn in file_paths_full])

# %%
fp_crop = file_paths_crop[1]
fp_full = file_paths_full[1]

# %%



# %%
im_crop = tifffile.imread(str(fp_crop),out = 'memmap')[-1]
im_full = tifffile.imread(str(fp_full),out = 'memmap')[-1]

# %%

# %%

# %%
result = match_template(im_full, im_crop)
ij = np.unravel_index(np.argmax(result), result.shape)
x, y = ij[::-1]

# %%
result.max()

# %%
fig = plt.figure(figsize=(8, 3))
ax1 = plt.subplot(1, 4, 1)
ax2 = plt.subplot(1, 4, 2)
ax4 = plt.subplot(1, 4, 3)
ax3 = plt.subplot(1, 4, 4, sharex=ax2, sharey=ax2)

ax1.imshow(im_crop, cmap=plt.cm.gray,norm=colors.PowerNorm(gamma=1/2))
ax1.set_axis_off()
ax1.set_title('template')

ax2.imshow(im_full, cmap=plt.cm.gray, norm=colors.PowerNorm(gamma=1/2))
#ax2.set_axis_off()
ax2.set_title('image')
# highlight matched region
hcoin, wcoin = im_crop.shape
rect = plt.Rectangle((x, y), wcoin, hcoin, edgecolor='r', facecolor='none')
ax2.add_patch(rect)


ax4.imshow(im_full[y:(y+hcoin), x:(x+wcoin)], cmap=plt.cm.gray, norm=colors.PowerNorm(gamma=1/2))
ax4.set_axis_off()
ax4.set_title('image')

ax3.imshow(result)
ax3.set_axis_off()
ax3.set_title('`match_template`\nresult')
# highlight matched region
ax3.autoscale(False)
ax3.plot(x, y, 'o', markeredgecolor='r', markerfacecolor='none', markersize=10)

plt.show()


# %%
def get_crop_coordinates(img_crop, img_full):
    result = match_template(img_full, img_crop)
    ij = np.unravel_index(np.argmax(result), result.shape)
    x, y = ij[::-1]
    w, h = img_crop.shape
    return x, y, w, h, result.max()



# %%
# %%time
out_list = []
for fn_crop, fn_full in zip(file_paths_crop, file_paths_full):
    im_crop = tifffile.imread(str(fn_crop),out = 'memmap')[-1]
    im_full = tifffile.imread(str(fn_full),out = 'memmap')[-1]
    x, y, w, h, score = get_crop_coordinates(im_crop, im_full)
    out_list.append({
        'basename': fn_full.name.replace('_ilastik2.tiff',''),
        'x': x,
        'y': y,
        'w': w,
        'h': h,
        'score': score
    })
    print(out_list[-1])


# %%
pd.DataFrame(out_list).to_csv('../../resources/manual_coordinates.csv', index=False)

# %%

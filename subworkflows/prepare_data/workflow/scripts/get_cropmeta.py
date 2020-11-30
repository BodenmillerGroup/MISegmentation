import pathlib

import tifffile


def get_wh(fn):
    with tifffile.TiffFile(fn) as im:
        w, h = reversed(im.shape[1:])
    return w, h

if __name__ == '__main__':
    sm = snakemake
    re_basic = re.compile(sm.params.re_basic)
    re_crop = re.compile(sm.params.re_crop)
    re_suffix = re.compile(sm.params.re_suffix)
    fol_labs = Path(sm.input.fol_labels)
    file_dict = {fp.name: re_basic.match(fp.name).groupdict()
                 for fp in fol_labs.glob('*_label.tiff')}
    for fn, dic in file_dict.items():
        crop_match = re_crop.match(dic['cropname'])
        if crop_match is not None:
            dic.update(**crop_match.groupdict())
        suffix_match = re_suffix.match(dic['suffix'])
        if suffix_match is not None:
            dic.update(**suffix_match.groupdict())
        dic['filename'] = fn
        if (dic.get('w', None) is None
            or dic.get('h', None) is None):
            dic['w'], dic['h'] = get_wh(fn)

    fn_manual_coordinates = pathlib.Path(sm.params.fn_manual_coordinates)
    dat_crops = pd.DataFrame(file_dict).T
    if fn_manual_coordinates.exists():
        dat_m_crops = pd.read_csv(fn_manual_crop_coordinates)
        dat_crops['coord_origin'] = 'name'
        dat_m_crops['coord_origin'] = 'matching'
        dat_crops = dat_crops.set_index('basename', drop=False)
        dat_m_crops = dat_m_crops.set_index('basename', drop=False)
        dat_crops.update(dat_m_crops, overwrite=True)
    dat_crops.to_csv(sm.output.fn_cropmeta, index=False)


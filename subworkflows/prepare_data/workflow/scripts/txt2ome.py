from imctools.io.txt.txtparser import TxtParser

def ome_from_txt(fn_txt, fn_ome):
    with TxtParser(
        fn_txt
    ) as parser:
        ac = parser.get_acquisition_data()
        ac.save_ome_tiff(fn_ome)

if __name__ == '__main__':
    import argparse
    import pathlib
    parser = argparse.ArgumentParser(description='Convert txt folder to ome')
    parser.add_argument('input_folder', type=str,
                        help='Input folder')
    parser.add_argument('output_folder', type=str,
                        help='Output folder')

    args = parser.parse_args()

    fol_input = pathlib.Path(args.input_folder)
    fol_output = pathlib.Path(args.output_folder)
    for fn in fol_input.rglob('*.txt'):
        fn_out = fol_output / f'{fn.stem}_a0.ome.tiff'
        ome_from_txt(fn, fn_out)

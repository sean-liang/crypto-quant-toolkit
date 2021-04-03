import argparse
from commons.argparse_commons import ParseKwargs
from commons.io import load_by_ext, save_by_ext


def convert_h5_to_parquet(input_path, output_path, in_params, out_params):
    in_params = in_params if in_params else {}
    out_params = out_params if out_params else {}
    print('read: ', input_path)
    df = load_by_ext(input_path, **in_params)
    print('write: ', output_path)
    save_by_ext(output_path, df, **out_params)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='convert dataframe file format, supported formats: .csv, .h5, .parquet')
    parser.add_argument('input', help='input file')
    parser.add_argument('output', help='output file')
    parser.add_argument('--input-config', nargs='*', action=ParseKwargs)
    parser.add_argument('--output-config', nargs='*', action=ParseKwargs)
    args = parser.parse_args()

    convert_h5_to_parquet(args.input, args.output, args.input_config, args.output_config)

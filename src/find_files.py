import argparse
import os
import os.path

from abstract.file_data import FileFinder
from formats.bmp_data import create_bmp_finder
from formats.hf_data import create_hf_finders
from formats.quicktime_data import create_quicktime_finders
from formats.riff_data import create_riff_finders
from formats.text_data import create_text_finder


# Deliberately does not include 'txt'
ALL_TYPES = [
    'jpg', 'png', 'gm81', 'gif', 'pdf', 'avi', 'wav', 'mp4', 'm4a', 'm4v',
    'mov', 'bmp',
]


def find_files(chunk_path, output_path, types):
    _, chunk_name = os.path.split(chunk_path)

    file_finders: list[FileFinder] = [
        *create_hf_finders(output_path, chunk_name, types),
        *create_riff_finders(output_path, chunk_name, types),
        *create_quicktime_finders(output_path, chunk_name, types),
        create_bmp_finder(output_path, chunk_name),
        create_text_finder(output_path, chunk_name),
    ]
    
    with open(chunk_path, mode='rb') as f:
        sector = f.read(512)
        while len(sector) > 0:
            found = False
            finder: FileFinder
            for finder in file_finders:
                found = finder.find_file(f, sector)
                if found:
                    break
            sector = f.read(512)


def setup() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str)
    parser.add_argument('outpath', type=str)
    parser.add_argument('-t', '--types', default=[],
                        type=lambda x: x.split(','))
    parser.add_argument('-a', '--all', action='store_true')
    return parser.parse_args()


def main(args: argparse.Namespace):
    types = ALL_TYPES if args.all else args.types
    find_files(args.filename, args.outpath, types)


if __name__ == '__main__':
    args = setup()
    main(args)

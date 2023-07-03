import argparse
import os
import os.path

from abstract.file_data import FileData
from formats.bmp_data import create_bmp_finder
from formats.hf_data import create_hf_types
from formats.quicktime_data import create_quicktime_types
from formats.riff_data import create_riff_types
from formats.text_data import create_text_finder


# Deliberately does not include 'txt'
ALL_TYPES = [
    'jpg', 'png', 'gm81', 'gif', 'pdf', 'avi', 'wav', 'mp4', 'm4a', 'm4v',
    'mov', 'bmp',
]


def find_files(chunk_path, output_path, types):
    _, chunk_name = os.path.split(chunk_path)

    file_finders: list[FileData] = [
        *create_hf_types(output_path, chunk_name, types),
        *create_riff_types(output_path, chunk_name, types),
        *create_quicktime_types(output_path, chunk_name, types),
        create_bmp_finder(output_path, chunk_name),
        create_text_finder(output_path, chunk_name),
    ]

    text_output_path = os.path.join(output_path, 'TEXT', chunk_name)
    os.makedirs(text_output_path, exist_ok=True)
    
    with open(chunk_path, mode='rb') as f:
        sector = f.read(512)
        while len(sector) > 0:
            found = False
            finder: FileData
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

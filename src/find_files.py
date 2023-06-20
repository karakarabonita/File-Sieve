import argparse
import os
import os.path

from formats.bmp_data import find_bmp_file, BMP_START
from formats.hf_data import create_hf_types
from formats.quicktime_data import create_quicktime_types
from formats.riff_data import create_riff_types
from formats.text_data import find_text_file


# Deliberately does not include 'txt'
ALL_TYPES = [
    'jpg', 'png', 'gm81', 'gif', 'pdf', 'avi', 'wav', 'mp4', 'm4a', 'm4v',
    'mov', 'bmp',
]


def find_files(chunk_path, output_path, types):
    _, chunk_name = os.path.split(chunk_path)

    hf_types = create_hf_types(output_path, chunk_name, types)
    indices = {hf_type: 0 for hf_type in hf_types}

    riff_types = create_riff_types(output_path, chunk_name, types)
    indices = {**indices, **{riff_type: 0 for riff_type in riff_types}}

    quicktime_types = create_quicktime_types(output_path, chunk_name, types)
    indices = {
        **indices, **{quicktime_type: 0 for quicktime_type in quicktime_types}
    }
    
    bmp_output_path = os.path.join(output_path, 'BMPs', chunk_name)
    os.makedirs(bmp_output_path, exist_ok=True)
    indices[BMP_START] = 0

    text_output_path = os.path.join(output_path, 'TEXT', chunk_name)
    os.makedirs(text_output_path, exist_ok=True)
    indices['txt'] = 0
    
    with open(chunk_path, mode='rb') as f:
        sector = f.read(512)
        while len(sector) > 0:
            found = False
            for hf_type in hf_types:
                found = hf_type.find_file(
                    f, sector, indices[hf_type])
                if found:
                    indices[hf_type] += 1
                    break
            
            for riff_type in riff_types:
                found = riff_type.find_file(
                    f, sector, indices[riff_type])
                if found:
                    indices[riff_type] += 1
                    break
            
            for quicktime_type in quicktime_types:
                found = quicktime_type.find_file(
                    f, sector, indices[quicktime_type])
                if found:
                    indices[quicktime_type] += 1
                    break
            
            if 'bmp' in types and not found:
                found = find_bmp_file(
                    f, sector, indices[BMP_START], 'bmp', bmp_output_path)
                if found:
                    indices[BMP_START] += 1
            
            if 'txt' in types and not found:
                found = find_text_file(
                    f, sector, indices['txt'], 'txt', text_output_path)
                if found:
                    indices['txt'] += 1
            sector = f.read(512)


def setup() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('outpath')
    return parser.parse_args()


def main(args: argparse.Namespace):
    find_files(args.filename, args.outpath, ALL_TYPES)


if __name__ == '__main__':
    args = setup()
    main(args)

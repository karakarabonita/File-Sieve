import os
import os.path

from formats.bmp_data import find_bmp_file, BMP_START
from formats.hf_data import HFData
from formats.quicktime_data import QuickTimeData
from formats.riff_data import RIFFData
from formats.text_data import find_text_file
from formats.zip_data import ZIPData


JPEG_START = b'\xff\xd8\xff'
JPEG_END = b'\xff\xd9'
PNG_START = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
PNG_END = b'\x49\x45\x4E\x44\xAE\x42\x60\x82'
GM81_START = b'\x91\xD5\x12\x00\x2A\x03\x00\x00'
GM81_END = b'Extension Packages\x00\x00\x00\x00'
GIF_START = b'GIF8'
GIF_END = b';'
PDF_START = b'%PDF'
PDF_END = b'%%EOF'


def create_hf_types(output_path, chunk_name, types):
    hf_types = [
        HFData(JPEG_START, JPEG_END, 'jpg', 
               os.path.join(output_path, 'JPEGs', chunk_name)),
        HFData(PNG_START, PNG_END, 'png',
               os.path.join(output_path, 'PNGs', chunk_name)),
        HFData(GM81_START, GM81_END, 'gm81',
               os.path.join(output_path, 'GM81s', chunk_name)),
        HFData(GIF_START, GIF_END, 'gif',
               os.path.join(output_path, 'GIFs', chunk_name)),
        HFData(PDF_START, PDF_END, 'pdf',
               os.path.join(output_path, 'PDFs', chunk_name)),
    ]
    return list(filter(lambda hf_type: hf_type.ext in types, hf_types))


AVI_TYPE = b'AVI '
WAV_TYPE = b'WAVE'


def create_riff_types(output_path, chunk_name, types):
    riff_types = [
        RIFFData(AVI_TYPE, 'avi',
                 os.path.join(output_path, 'AVIs', chunk_name)),
        RIFFData(WAV_TYPE, 'wav',
                 os.path.join(output_path, 'WAVs', chunk_name)),
    ]
    return list(filter(lambda riff_type: riff_type.ext in types, riff_types))


MP4_SUB_TYPES = [
    b'avc1', b'iso2', b'isom', b'mmp4', b'mp41', b'mp42', b'mp71', b'msnv',
    b'ndas', b'ndsc', b'ndsh', b'ndsm', b'ndsp', b'ndss', b'ndxc', b'ndxh',
    b'ndxm', b'ndxp', b'ndxs',
]
M4A_SUB_TYPES = [b'M4A ']
MOV_SUB_TYPES = [b'qt  ']
M4V_SUB_TYPES = [b'M4V ']


def create_quicktime_types(output_path, chunk_name, types):
    quicktime_types = [
        QuickTimeData(MP4_SUB_TYPES, 'mp4',
                      os.path.join(output_path, 'MP4s', chunk_name)),
        QuickTimeData(M4A_SUB_TYPES, 'm4a',
                      os.path.join(output_path, 'M4As', chunk_name)),
        QuickTimeData(MOV_SUB_TYPES, 'mov',
                      os.path.join(output_path, 'MOVs', chunk_name)),
        QuickTimeData(M4V_SUB_TYPES, 'm4v',
                      os.path.join(output_path, 'M4Vs', chunk_name)),
    ]
    return list(filter(
        lambda quicktime_type: quicktime_type.ext in types, quicktime_types))


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
                    f, sector, indices[hf_type], chunk_path)
                if found:
                    indices[hf_type] += 1
                    break
            
            for riff_type in riff_types:
                found = riff_type.find_file(
                    f, sector, indices[riff_type], chunk_path)
                if found:
                    indices[riff_type] += 1
                    break
            
            for quicktime_type in quicktime_types:
                found = quicktime_type.find_file(
                    f, sector, indices[quicktime_type], chunk_path)
                if found:
                    indices[quicktime_type] += 1
                    break
            
            if 'bmp' in types and not found:
                found = find_bmp_file(
                    f, sector, indices[BMP_START], 'bmp', chunk_path,
                    bmp_output_path)
                if found:
                    indices[BMP_START] += 1
            
            if 'txt' in types and not found:
                found = find_text_file(
                    f, sector, indices['txt'], 'txt', chunk_path,
                    text_output_path)
                if found:
                    indices['txt'] += 1
            sector = f.read(512)

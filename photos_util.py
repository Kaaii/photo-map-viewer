"""
photos_util.py

File contains helper functions for reading EXIF metadata from photos.
Convert coordinates from GPS Info of photos to decimal format.
Constructs DataFrame containing information about photos.
"""

import pandas as pd
import numpy as np

from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
import pillow_heif
import base64
pillow_heif.register_heif_opener()
#from exif import Image

import os
from pathlib import Path
from datetime import datetime


def get_photos_from_path(directory_path: Path, extensions=['.jpg', '.jpeg', '.heic']) -> list:
    """Returns list of file paths from `directory_path` that have an extension in `extensions`.
    Default extensions: .jpg, .jpeg, .heic
    
    If `directory_path` is not a valid path, returns None.
    """
    if not os.path.exists(directory_path):
        print(f"{directory_path} is not a valid path.")
        return None
    photos = [directory_path/p for p in os.listdir(directory_path) if Path(p).suffix.lower() in extensions]
    return photos


def get_image(filepath: str):
    """Returns Image from filepath"""
    return Image.open(filepath)


def get_exif(image):
    """Returns EXIF data from image file"""
    return image.getexif()


def get_labeled_exif(exif):
    """Returns dictionary of TAG names to the values from exif metadata"""
    return {TAGS.get(key, key): value for key, value in exif.items()}


def get_gps_info(exif):
    """Returns dictionary of gps metadata from 'GPSInfo' tag in EXIF metadata"""
    for key, value in TAGS.items():
        if value == "GPSInfo":
            gps_info = exif.get_ifd(key)
            return {GPSTAGS.get(key, key): value for key, value in gps_info.items()}
    return None
    
    
#Credit: https://gist.github.com/pavelcherepan/49421ab64b78c5a9eee620789a5b44fa#file-coords-py
def convert_coords_to_decimal(coords: tuple[float,...], ref: str) -> float:
    """Covert a tuple of coordinates in the format (degrees, minutes, seconds)
    and a reference to a decimal representation.
    Args:
        coords (tuple[float,...]): A tuple of degrees, minutes and seconds
        ref (str): Hemisphere reference of "N", "S", "E" or "W".
    Returns:
        float: A signed float of decimal representation of the coordinate.
    """
    if ref.upper() in ['W', 'S']:
        mul = -1
    elif ref.upper() in ['E', 'N']:
        mul = 1
    else:
        print("Incorrect hemisphere reference. "
              "Expecting one of 'N', 'S', 'E' or 'W', "
              f'got {ref} instead.')
    # make sure coords are made of floats
    coords = [float(i) for i in coords]
        
    return mul * (coords[0] + coords[1] / 60 + coords[2] / 3600)  


def construct_df(photos: list) -> pd.DataFrame:
    """Returns DataFrame using a list of photo filepaths (jpg, jpeg, or heic only).
    Columns: filename, datetime, latitude, longitude, day"""
    df=pd.DataFrame()
    i=0
    for photo in photos:
        if photo.suffix.lower() not in ['.jpg', '.jpeg', '.heic']:
            # skip non-jpg files
            continue
        img = get_image(photo)
        img_exif = get_exif(img)
        img_tags = get_labeled_exif(img_exif)
        img_gps = get_gps_info(img_exif)
        try:
            latitude = convert_coords_to_decimal(img_gps['GPSLatitude'], img_gps['GPSLatitudeRef'])
            longitude = convert_coords_to_decimal(img_gps['GPSLongitude'], img_gps['GPSLongitudeRef'])
            date = datetime.strptime(img_tags['DateTime'], '%Y:%m:%d %H:%M:%S')
            d = {
                'filename': Path(photo).name,
                'datetime': date,
                # 'gps_latitude': img_gps['GPSLatitude'],
                # 'gps_longitude': img_gps['GPSLongitude'],
                # 'gps_latitude_ref': img_gps['GPSLatitudeRef'],
                # 'gps_longitude_ref': img_gps['GPSLongitudeRef']
                'latitude': latitude,
                'longitude': longitude,
                'day': date.day
            }
        except KeyError:
            # skip photos that could not be added
            continue
        #df = df.append(d, ignore_index=True)
        df = pd.concat([df, pd.DataFrame(d, index=[i])])
        i+=1
    print("Number of photos added vs total:", i, len(photos)) # number that went through 
    return df
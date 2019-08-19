"""
Searches for images in a list of directories and finds images with duplicates across the
directories.

Uses dash to compare images
Implements Python Multiprocessing to speed up job

Usage:
    Input directory paths inside the directories variable (L:107)

    python image_duplicate.py
"""
import json
import logging
import os
import time
from multiprocessing import Manager, Lock, Process
from typing import Dict

import memory_profiler
from PIL import Image

logging.basicConfig(
    filemode='w',
    filename='logs.log',
    format='%(asctime)s %(name)s  %(levelname)s  %(message)s',
    level=logging.INFO
)


# https://blog.iconfinder.com/detecting-duplicate-images-using-python-cb240b05a3b6
def dhash(image, hash_size=72):
    # Grayscale and shrink the image in one step.
    image = Image.open(image)

    image = image.convert('L').resize(
        (hash_size + 1, hash_size),
        Image.ANTIALIAS,
    )

    # Compare adjacent pixels.
    difference = []
    for row in range(hash_size):
        for col in range(hash_size):
            pixel_left = image.getpixel((col, row))
            pixel_right = image.getpixel((col + 1, row))
            difference.append(pixel_left > pixel_right)

    # Convert the binary array to a hexadecimal string.
    decimal_value = 0
    hex_string = []

    for index, value in enumerate(difference):
        if value:
            decimal_value += 2 ** (index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
            decimal_value = 0
    return ''.join(hex_string)


def get_directory_items(directory: str):
    for curr_dir, dirs, items in os.walk(directory):
        for item in items:
            yield os.path.join(curr_dir, item)


def get_image(file: str) -> bool:
    try:
        return Image.open(file)
    except Exception:
        logging.exception(f"Not an image: {file}")
        return None


def process(file: str, processed: Dict):
    image_a = get_image(file)

    if image_a is None:
        return False

    try:
        hashed = dhash(file)

        if hashed in processed:
            logging.debug(f"Duplicate: {hashed}")

            data = processed.get(hashed)
            data['counter'] += 1
            data['items'] += [file]

            processed[hashed] = data
        else:
            processed[hashed] = {
                "counter": 1,
                "items": [file]
            }

    except Exception as e:
        logging.exception(f"Problem: {file}")


if __name__ == "__main__":
    start = time.time()
    logging.info('Memory (Before): ' + str(memory_profiler.memory_usage()) + 'MB')

    directories = []

    with Manager() as manager:
        results = manager.dict({})
        lock = Lock()

        procs = []
        for directory in directories:
            for item_a in get_directory_items(directory):
                _, ext = os.path.splitext(item_a)

                if ext[1:].lower() not in ['jpg', 'png', 'gif', 'bmp', 'tif', 'tiff']:
                    continue

                proc = Process(target=process, args=(item_a, results))
                proc.start()

                procs.append(proc)

        for p in procs:
            p.join()

        end_time = time.time() - start

        json.dump({k: v for k, v in dict(results).items() if v['counter'] > 1}, open('results.json', 'w'), indent=4)

    logging.info('Memory (After) : ' + str(memory_profiler.memory_usage()) + 'MB')
    logging.info(f"Took {end_time}s")

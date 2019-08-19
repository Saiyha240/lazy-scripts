"""
Test Python's Multiprocessing with data sharing

Reads all the files in a directory and stores their md5 hash on list
"""
import hashlib
import json
import multiprocessing
import os
import time
from typing import Dict

DIRECTORY = ''


def process(file: str, db: Dict) -> None:
    md5_digest = hashlib.md5(open(file, 'rb').read()).hexdigest()
    db[md5_digest] = file


if __name__ == '__main__':
    with multiprocessing.Manager() as manager:
        data = manager.dict({})

        procs = []
        for current_dir, folders, files in os.walk(DIRECTORY):
            for file in files:
                full_path = os.path.join(current_dir, file)
                md5_digest = hashlib.md5(open(full_path, 'rb').read()).hexdigest()
                data[md5_digest] = full_path
                time.sleep(0.500)

        print(json.dumps(dict(data), indent=4, sort_keys=True))

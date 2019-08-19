"""
Gets all the file extensions in a list of directories

Implements Python Multiprocessing to speed up job

Usage:
    Input directory paths inside the directories variable (L:39)

    python file_extensions.py
"""
import json
import multiprocessing
import os
import time

import memory_profiler
from python_duplicate.image_duplicate import get_directory_items


def find_extensions(file, data, lock: multiprocessing.Lock):
    f, e = os.path.splitext(file)

    lock.acquire()

    try:
        if e in data:
            data[e] += 1
        else:
            data[e] = 1
    finally:
        lock.release()


if __name__ == "__main__":
    start = time.time()
    print('Memory (Before): ' + str(memory_profiler.memory_usage()) + 'MB')

    directories = []

    with multiprocessing.Manager() as manager:
        lock = multiprocessing.Lock()
        data = manager.dict({})

        procs = []
        for directory in directories:
            for item_a in get_directory_items(directory):
                _, ext = os.path.splitext(item_a)

                proc = multiprocessing.Process(target=find_extensions, args=(item_a, data, lock))
                proc.start()

                procs.append(proc)

        for p in procs:
            p.join()

        json.dump(dict(data), open('extensions.json', 'w'), indent=4)

    end_time = time.time() - start

    print('Memory (After) : ' + str(memory_profiler.memory_usage()) + 'MB')
    print(f"Took {end_time}s")

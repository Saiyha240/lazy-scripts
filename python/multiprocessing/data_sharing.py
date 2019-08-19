"""
Test Python's Multiprocessing with data sharing across processes

Reads all the files in a directory and stores their md5 hash on list
"""
import hashlib
import json
import multiprocessing
import os

DIRECTORY = ''


def process(file: str, db) -> None:
    md5_digest = hashlib.md5(open(file, 'rb').read()).hexdigest()

    if md5_digest in db:
        db[md5_digest] += [file]
    else:
        db[md5_digest] = [file]


if __name__ == '__main__':
    with multiprocessing.Manager() as manager:
        data = manager.dict({})

        procs = []
        for current_dir, folders, files in os.walk(DIRECTORY):
            for file in files:
                full_path = os.path.join(current_dir, file)
                proc = multiprocessing.Process(target=process, args=(full_path, data))
                proc.start()

                procs.append(proc)

        for p in procs:
            p.join()

        print(json.dumps(dict(data), indent=4, sort_keys=True))

"""
Test Python's Multiprocessing
"""
import multiprocessing
import os


def worker1(name: str):
    print(f"Worker1 {name}: {os.getpid()}")


def worker2(name: str):
    print(f"Worker1 {name}: {os.getpid()}")


if __name__ == '__main__':
    print(f"Main process: {os.getpid()}")

    p1 = multiprocessing.Process(target=worker1, args=('a',))
    p2 = multiprocessing.Process(target=worker2, args=('b',))

    p1.start()
    p2.start()

    print("ID of process p1: {}".format(p1.pid))
    print("ID of process p2: {}".format(p2.pid))

    p1.join()
    p2.join()

    print("Both finished")

    print("Process p1 is alive: {}".format(p1.is_alive()))
    print("Process p2 is alive: {}".format(p2.is_alive()))

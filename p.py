from multiprocessing import Process
import time


i = 0


def a(i):
    print(i)


if __name__ == '__main__':
    cpu = 4

    workers = [Process(target=a, kwargs={'i': _}) for _ in range(cpu)]

    for worker in workers:
        worker.start()
        time.sleep(2)

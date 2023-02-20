# Standard Library
import time

direction = "minimize"


class RunTime:
    _start_time = None
    _end_time = None

    def start(self):
        self._start_time = time.perf_counter()

    def end(self):
        self._end_time = time.perf_counter()

    def quality(self):
        return self._end_time - self._start_time

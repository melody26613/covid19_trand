import threading
import sys
import time

class SpinnerThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(SpinnerThread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def join(self, *args, **kwargs):
        self.stop()
        super(SpinnerThread,self).join(*args, **kwargs)

    def spinning_cursor(self):
        while True:
            for cursor in '|/-\\':
                yield cursor

    def run(self):
        spinner = self.spinning_cursor()
        while not self._stop_event.is_set():
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            time.sleep(0.5)
            sys.stdout.write('\b')
        print("spinner stopped")

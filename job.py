from threading import Thread
import time


class Job:
    def process(self):
        raise NotImplementedError

    def finish(self):
        pass


class AsyncExecute(Thread):
    def __init__(self, job: Job, refresh_time=0.1):
        Thread.__init__(self)
        self.job = job
        self.stop = False
        self.refresh_time = refresh_time

    def run(self):
        self.stop = False
        while not self.stop:
            self.job.process()
            time.sleep(0.1)

    def join(self, timeout=None):
        self.stop = True
        Thread.join(self, timeout)


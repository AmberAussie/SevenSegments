import driver
import time
from threading import Thread


class PrintObject:
    def __init__(self, start_digit: int=0, nbr_digit: int=None):
        if nbr_digit is None:
            nbr_digit = 4-start_digit
        self.nbr_digit = nbr_digit
        self.start_digit = start_digit

    def print(self, drv: driver.Driver_7Seg):
        raise NotImplementedError


class BaseAnim(PrintObject):
    def __init__(self, nbr_step: int, step_time: float, start_digit: int=0, nbr_digit: int=None):
        super(BaseAnim, self).__init__(start_digit, nbr_digit)
        self.nbr_step = nbr_step
        self.step = 0
        self.step_time = step_time
        self.next_update = 0

    def progress(self):
        now = time.time()
        if self.next_update < now:
            self.next_update = now + self.step_time
            self.step += 1
            self.step %= self.nbr_step
            return True
        return False


class WheelAnim(BaseAnim):
    def __init__(self, digit: int, step_time: float=0.2):
        super(WheelAnim, self).__init__(4, step_time, digit, 1)

    def print(self, drv: driver.Driver_7Seg):
        if self.step == 0:
            drv.write_seg(self.start_digit, drv.SEG_A)
        elif self.step == 1:
            drv.write_seg(self.start_digit, drv.SEG_B)
        elif self.step == 2:
            drv.write_seg(self.start_digit, drv.SEG_G)
        elif self.step == 3:
            drv.write_seg(self.start_digit, drv.SEG_F)


class TextAnim(BaseAnim):
    def __init__(self, txt: str, start_digit: int=0, nbr_digit: int=None, step_time: float=0.7):
        super(TextAnim, self).__init__(len(txt), step_time, start_digit, nbr_digit)
        self.txt = txt

    def print(self, drv: driver.Driver_7Seg):
        drv.set_cursor(self.start_digit)
        sub_txt = self.txt[self.step:]
        sub_txt += ' ' * (self.nbr_digit-len(sub_txt)) # feed with spaces
        sub_txt = sub_txt[:self.nbr_digit]
        drv.print(sub_txt)


class Simple7SegAsnyc(Thread):
    def __init__(self, drv: driver.Driver_7Seg):
        self.stop = False
        self.drv = drv
        self.anim= []
        Thread.__init__(self)
        self.start()

    def print_anim(self, anim: []):
        self.anim = anim

    def run(self):
        self.stop = False
        while not self.stop:
            for anim in self.anim:
                if anim.progress():
                    anim.print(self.drv)
            time.sleep(0.1)

    def join(self, timeout=None):
        self.stop = True
        Thread.join(self, timeout)


if __name__ == '__main__':
    drv = driver.SerialDriver_7Seg(('/dev/ttyUSB0', 9600))
    helper = Simple7SegAsnyc(drv)

    anims = []
    anims.append(TextAnim('123456', 1, 2))
    anims.append(WheelAnim(0))
    anims.append(WheelAnim(3))

    helper.print_anim(anims)
    time.sleep(10)
    helper.join()
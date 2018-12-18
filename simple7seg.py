import driver
import time
from job import Job, AsyncExecute


class PrintObject:
    def __init__(self, start_digit: int=0, nbr_digit: int=None):
        if nbr_digit is None:
            nbr_digit = 4-start_digit
        self.nbr_digit = nbr_digit
        self.start_digit = start_digit

    def need_print(self):
        raise NotImplementedError

    def print(self, drv: driver.Driver_7Seg):
        raise NotImplementedError


class BaseStatic(PrintObject):
    def __init__(self, start_digit: int=0, nbr_digit: int=None):
        super(BaseStatic, self).__init__(start_digit, nbr_digit)
        self.redraw=True

    def need_print(self):
        return self.redraw

    def print(self, drv: driver.Driver_7Seg):
        self.redraw = False


class Percentage(BaseStatic):
    def __init__(self, max_value: int):
        self.max_value = max_value
        self.first = True
        self.percent = 0
        super(Percentage, self).__init__(0, 4)

    def print_percent_sign(self, drv):
        drv.write_dot(drv.DOT_APOSTROPHE | drv.DOT_DIGIT4)
        drv.write_seg(3, drv.SEG_G)

    def update(self, i):
        self.percent = i * 100.0 / self.max_value
        self.redraw = True

    def print(self, drv: driver.Driver_7Seg):
        if self.first:
            self.print_percent_sign(drv)
            self.first = False
        drv.set_cursor(0)
        super(Percentage, self).print(drv)
        drv.print('%3d' % self.percent)


class BaseAnim(PrintObject):
    def __init__(self, nbr_step: int, step_time: float, start_digit: int=0, nbr_digit: int=None):
        super(BaseAnim, self).__init__(start_digit, nbr_digit)
        self.nbr_step = nbr_step
        self.step = 0
        self.step_time = step_time
        self.next_update = 0

    def need_print(self):
        now = time.time()
        if self.next_update < now:
            self.next_update = now + self.step_time
            return True
        return False

    def print(self, drv: driver.Driver_7Seg):
        self.step += 1
        self.step %= self.nbr_step


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
        super(WheelAnim, self).print(drv)


class TextAnim(BaseAnim):
    def __init__(self, txt: str, start_digit: int=0, nbr_digit: int=None, step_time: float=0.7):
        if len(txt) > 4:
            nb_step = len(txt)
        else:
            nb_step = 1
        super(TextAnim, self).__init__(nb_step, step_time, start_digit, nbr_digit)
        self.txt = txt

    def print(self, drv: driver.Driver_7Seg):
        drv.set_cursor(self.start_digit)
        sub_txt = self.txt[self.step:]
        sub_txt += ' ' * (self.nbr_digit-len(sub_txt)) # feed with spaces
        sub_txt = sub_txt[:self.nbr_digit]
        drv.print(sub_txt)
        super(TextAnim, self).print(drv)


class Simple7Seg(Job):
    """ Base class for helper with more than one printable object """
    def __init__(self, driver_settings):
        self.do_clear = True
        self.drv = driver.driver_factory(driver_settings)
        self.anim= []

    def print_anim(self, anim: []):
        self.anim = anim
        self.do_clear = True

    def process(self):
        if self.do_clear:
            self.drv.clear()
            self.do_clear = False

        for anim in self.anim:
            if anim.need_print():
                anim.print(self.drv)


if __name__ == '__main__':
    from settings import Settings
    helper = Simple7Seg(Settings.Driver)
    task = AsyncExecute(helper)
    task.start()

    progress = Percentage(15)
    helper.print_anim([progress])
    for i in range(15):
        progress.update(i)
        time.sleep(0.4)

    anims = []
    anims.append(TextAnim('123456', 1, 2))
    anims.append(WheelAnim(0))
    anims.append(WheelAnim(3))
    helper.print_anim(anims)
    time.sleep(10)

    task.join()

from roboarm import Arm
from .const import ACTION_TIMEOUT


class Controller(object):
    """Arm controller"""

    def __call__(self, options, arm_queue):
        self.arm = Arm()
        self._queue = arm_queue
        self.loop()

    def loop(self):
        """Arm controlling loop"""
        while True:
            try:
                part, action = self._queue.get()
                self.perform(part, action)
            except Exception:
                continue

    def perform(self, part_name, action_name):
        """Perform action on arm"""
        part = getattr(self.arm, part_name)
        action = getattr(part, action_name)

        if part_name == 'led':
            action()
        else:
            action(timeout=ACTION_TIMEOUT)


arm_target = Controller()

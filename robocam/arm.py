import json
import redis
from roboarm import Arm
from .const import ACTION_TIMEOUT, REDIS_ARM_CHANNEL


class Controller(object):
    """Arm controller"""

    def __init__(self):
        self._init_arm()
        self._init_redis()

    def _init_arm(self):
        self.arm = Arm()

    def _init_redis(self):
        self._redis = redis.Redis()
        self._pubsub = self._redis.pubsub()
        self._pubsub.subscribe([REDIS_ARM_CHANNEL])

    def run(self):
        """Arm controlling loop"""
        for msg in self._pubsub.listen():
            try:
                part, action = json.loads(msg['data'])
                self.perform(part, action)
            except Exception as e:
                print e
                continue

    def perform(self, part_name, action_name):
        """Perform action on arm"""
        part = getattr(self.arm, part_name)
        action = getattr(part, action_name)

        if part_name == 'led':
            action()
        else:
            action(timeout=ACTION_TIMEOUT)


def main():
    controller = Controller()
    controller.run()

from multiprocessing import Process, Queue, Value
from argparse import ArgumentParser
import os
import sys
from .const import FIFO_PATH
from .arm import arm_target
from .camera import camera_target
from .web import web_target
from .gpio import DistanceTarget


class Robocam(object):
    """Robocam app"""

    def run(self):
        self._parse_options()
        self._create_fifo()
        self._create_shared()
        self._run_procs()

    def _parse_options(self):
        """Parse options"""
        parser = ArgumentParser(prog='ROBOCAM!')
        parser.add_argument('--port', type=int, default=8080)
        parser.add_argument('--host', type=str, default='')
        parser.add_argument('--debug', type=bool, default=False)
        parser.add_argument('--echo_pin', type=int, default=17)
        parser.add_argument('--trig_pin', type=int, default=4)
        self._options = parser.parse_args(sys.argv[1:])

    def _create_fifo(self):
        """Create or replace fifo"""
        if os.path.exists(FIFO_PATH):
            os.unlink(FIFO_PATH)
        os.mkfifo(FIFO_PATH)

    def _create_shared(self):
        """Create shared"""
        self._distance = Value('f', 0)
        self._arm_queue = Queue()
        self._camera_queue = Queue()

    def _run_procs(self):
        """Run procs"""
        self._procs = [
            Process(target=arm_target, args=(self._options, self._arm_queue)),
            Process(target=camera_target, args=(self._options, self._camera_queue)),
            Process(target=DistanceTarget, args=(self._options, self._distance)),
            Process(target=web_target, args=(
                self._options, self._camera_queue, self._arm_queue, self._distance,
            )),
        ]

        for proc in self._procs:
            proc.start()


def main():
    app = Robocam()
    app.run()

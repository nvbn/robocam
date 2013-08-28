import subprocess
import os
from .const import FIFO_PATH, DEFAULT_ATTRS


def main():
    if os.path.exists(FIFO_PATH):
        os.unlink(FIFO_PATH)
    os.mkfifo(FIFO_PATH)

    proc = subprocess.Popen('raspistill -vf -t 3600000 {} -n -o {}'.format(
        DEFAULT_ATTRS, FIFO_PATH
    ), shell=True)
    proc.wait()

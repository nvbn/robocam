from Queue import Empty
import subprocess
from .const import FIFO_PATH, DEFAULT_ATTRS


class Camera(object):
    """Camera obj"""

    def __init__(self, attrs):
        """Camera object"""
        self._attrs = attrs

    def _get_command(self):
        """Get command"""
        return 'raspistill -vf -t 3600000 {} -n -o {}'.format(
            self._attrs, FIFO_PATH,
        )

    def run(self):
        """Run cammera process"""
        self._proc = subprocess.Popen(
            self._get_command(), shell=True,
        )

    def stop(self):
        """Kill proc"""
        self._proc.kill()

    def is_run(self):
        """Check is run"""
        return self._proc.poll() is None


class CameraTarget(object):
    """Camera target"""

    def __init__(self):
        self._attrs = DEFAULT_ATTRS

    def __call__(self, options, camera_queue):
        self._queue = camera_queue
        self.create_camera()
        self.loop()

    def loop(self):
        """Target loop"""
        while True:
            try:
                if self.has_changes():
                    self.restart()
            except Exception:
                continue

    def has_changes(self):
        """Check has changes"""
        try:
            self._attrs = self._queue.get(timeout=1)
            has_changes = True
        except Empty:
            has_changes = False

        if not self._camera.is_run():
            has_changes = True
        return has_changes

    def restart(self):
        """Restart camera"""
        if self._camera.is_run():
            self._camera.stop()
        self.create_camera()

    def create_camera(self):
        """Create camera"""
        self._camera = Camera(self._attrs)
        self._camera.run()


camera_target = CameraTarget()

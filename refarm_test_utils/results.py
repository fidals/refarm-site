import time
from unittest.runner import TextTestResult


class TimedResult(TextTestResult):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_timings = []
        self._test_started_at = 0

    def startTest(self, *args, **kwargs):
        self._test_started_at = time.time()
        super().startTest(*args, **kwargs)

    def addSuccess(self, test):
        elapsed = time.time() - self._test_started_at
        name = self.getDescription(test)
        self.test_timings.append((name, elapsed))
        super().addSuccess(test)

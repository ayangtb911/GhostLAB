from testing.test_case import TestCase
from testing.test_result import TestResult


class CPUUsageTest(TestCase):

    def __init__(self, name, node, max_cpu):

        super().__init__(name, node)

        self.max_cpu = max_cpu

    def run(self):

        if self.node.cpu_usage <= self.max_cpu:

            return TestResult(
                self.name,
                True,
                f"CPU usage is {self.node.cpu_usage}% "
                f"(limit: {self.max_cpu}%)"
            )

        return TestResult(
            self.name,
            False,
            f"CPU usage is {self.node.cpu_usage}% "
            f"(limit: {self.max_cpu}%)"
        )
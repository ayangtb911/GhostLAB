from testing.test_result import TestResult


class TestCase:

    def __init__(self, name, node):
        self.name = name
        self.node = node

    def run(self):

        return TestResult(
            self.name,
            False,
            "Base test was not implemented"
        )
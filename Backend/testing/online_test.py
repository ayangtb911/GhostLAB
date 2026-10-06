from testing.test_case import TestCase
from testing.test_result import TestResult


class OnlineTest(TestCase):

    def run(self):

        if self.node.status == "ONLINE":

            return TestResult(
                self.name,
                True,
                f"{self.node.node_id} is online"
            )

        return TestResult(
            self.name,
            False,
            f"{self.node.node_id} is offline"
        )
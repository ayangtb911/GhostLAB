class TestResult:

    def __init__(self, test_name, passed, message):
        self.test_name = test_name
        self.passed = passed
        self.message = message

    def show(self):

        if self.passed:
            status = "PASS"
        else:
            status = "FAIL"

        print(f"[{status}] {self.test_name}")
        print(f"       {self.message}")
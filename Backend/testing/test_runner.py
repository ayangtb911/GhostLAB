class TestRunner:

    def __init__(self):
        self.tests = []

    def add_test(self, test):
        self.tests.append(test)

    def run_all(self):

        results = []

        for test in self.tests:

            result = test.run()

            results.append(result)

        return results
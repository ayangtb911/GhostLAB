from concurrent.futures import ThreadPoolExecutor
import threading


class ParallelTestRunner:

    def __init__(self, workers=3):
        self.tests = []
        self.workers = workers

    def add_test(self, test):
        self.tests.append(test)

    def run_test(self, test):

        print(f"[START] {test.name} | Worker: {threading.current_thread().name}")

        result = test.run()

        print(f"[DONE] {test.name} | Worker: {threading.current_thread().name}")

        return result

    def run_all(self):

        with ThreadPoolExecutor(max_workers=self.workers) as executor:

            results = list(
                executor.map(
                    self.run_test,
                    self.tests
                )
            )

        return results
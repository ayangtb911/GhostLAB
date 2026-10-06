import heapq


class TestScheduler:

    def __init__(self):
        self.tests = []
        self.dependencies = {}

    def add_test(self, test, priority):
        heapq.heappush(self.tests, (-priority, test))
        self.dependencies[test] = []

    def add_dependency(self, test, depends_on):
        self.dependencies[test].append(depends_on)

    def get_dependencies(self, test):
        return self.dependencies[test]

    def get_order(self):

        # Store priority of every test
        priority_map = {}

        for priority, test in self.tests:
            priority_map[test] = -priority

        # Number of dependencies for each test
        indegree = {}

        for test in self.dependencies:
            indegree[test] = len(self.dependencies[test])

        # Reverse graph
        dependents = {}

        for test in self.dependencies:
            dependents[test] = []

        for test in self.dependencies:
            for dependency in self.dependencies[test]:
                dependents[dependency].append(test)

        # Tests that are ready to run
        ready = []

        for test in self.dependencies:
            if indegree[test] == 0:
                heapq.heappush(
                    ready,
                    (-priority_map[test], test)
                )

        ordered_tests = []

        # Topological sorting
        while ready:

            priority, test = heapq.heappop(ready)

            ordered_tests.append(test)

            for dependent in dependents[test]:

                indegree[dependent] -= 1

                if indegree[dependent] == 0:
                    heapq.heappush(
                        ready,
                        (-priority_map[dependent], dependent)
                    )

        # Detect circular dependencies
        if len(ordered_tests) != len(self.dependencies):
            raise ValueError("Circular dependency detected")

        return ordered_tests
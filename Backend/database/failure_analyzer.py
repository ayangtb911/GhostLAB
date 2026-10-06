from database.database_manager import DatabaseManager


class FailureAnalyzer:

    def __init__(self):
        self.db = DatabaseManager()

    def show_failures(self):

        failures = self.db.get_failures()

        print("\n--- FAILURE ANALYSIS ---")

        if not failures:
            print("No failures recorded.")
            return

        for failure in failures:

            node_id = failure[0]
            failure_type = failure[1]

            print(
                f"Node {node_id} experienced {failure_type}"
            )
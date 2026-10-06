from database.database_manager import DatabaseManager


class ChaosEngine:

    def __init__(self):
        self.failures = []
        self.db = DatabaseManager()

    def inject_failure(self, node, failure_type):

        print(f"\n[CHAOS] Injecting {failure_type} into {node.node_id}")

        if failure_type == "CRASH":
            node.stop()
            print(f"[CHAOS] {node.node_id} has crashed!")

        elif failure_type == "TIMEOUT":
            print(f"[CHAOS] {node.node_id} is responding slowly...")

        elif failure_type == "DROP":
            print(f"[CHAOS] Message to {node.node_id} was dropped!")

        self.failures.append({
            "node": node.node_id,
            "type": failure_type
        })

        self.db.save_failure(
            node.node_id,
            failure_type
        )
from Backend.database.database_manager import DatabaseManager


# ============================================================
# GHOSTLAB MAIN SIMULATOR
# ============================================================

db = DatabaseManager()


ENVIRONMENTS = {
    "AUTOMOTIVE": [
        ("Battery", "HIGH"),
        ("Engine", "HIGH"),
        ("Brake", "HIGH"),
        ("Transmission", "HIGH"),
        ("ECU", "HIGH"),
        ("Lighting", "LOW"),
        ("Infotainment", "LOW"),
        ("Cooling System", "MEDIUM"),
        ("Steering", "HIGH"),
    ],

    "PC": [
        ("Power Supply", "HIGH"),
        ("CPU", "HIGH"),
        ("RAM", "HIGH"),
        ("GPU", "MEDIUM"),
        ("Storage", "MEDIUM"),
        ("Network Adapter", "MEDIUM"),
        ("Operating System", "HIGH"),
        ("Cooling System", "MEDIUM"),
        ("Motherboard", "HIGH"),
    ],

    "AIRCRAFT": [
        ("Battery", "HIGH"),
        ("Engine", "HIGH"),
        ("Flight Computer", "HIGH"),
        ("Navigation", "HIGH"),
        ("Radar", "HIGH"),
        ("Hydraulic System", "HIGH"),
        ("Landing Gear", "HIGH"),
        ("Communication", "MEDIUM"),
        ("Fuel System", "HIGH"),
    ]
}


DEPENDENCIES = {
    "AUTOMOTIVE": [
        ("Battery", "Lighting"),
        ("Battery", "Infotainment"),
        ("Engine", "Transmission"),
        ("Engine", "Cooling System"),
        ("ECU", "Engine"),
    ],

    "PC": [
        ("Power Supply", "Motherboard"),
        ("Motherboard", "CPU"),
        ("Motherboard", "RAM"),
        ("Motherboard", "GPU"),
        ("Operating System", "Network Adapter"),
        ("CPU", "Cooling System"),
    ],

    "AIRCRAFT": [
        ("Battery", "Flight Computer"),
        ("Flight Computer", "Navigation"),
        ("Flight Computer", "Radar"),
        ("Engine", "Hydraulic System"),
        ("Fuel System", "Engine"),
    ]
}


# ============================================================
# CREATE DEFAULT SYSTEM
# ============================================================

def create_default_system(environment="AUTOMOTIVE"):

    existing_nodes = db.get_nodes()

    if existing_nodes:
        print("Existing GHOSTLAB system found.")
        return

    print("No nodes found.")
    print(f"Creating default {environment} system...\n")

    nodes = ENVIRONMENTS[environment]

    for index, (node_type, priority) in enumerate(nodes, start=1):

        node_id = f"{environment}_{index:02d}"

        db.save_node(
            node_id=node_id,
            node_type=node_type,
            status="ONLINE",
            health=100,
            cpu_usage=20,
            memory_usage=30,
            priority=priority,
            environment=environment
        )

        print(f"Created: {node_id} -> {node_type}")

    # Add dependencies
    for parent_type, child_type in DEPENDENCIES[environment]:

        parent_id = None
        child_id = None

        for index, (node_type, _) in enumerate(nodes, start=1):

            if node_type == parent_type:
                parent_id = f"{environment}_{index:02d}"

            if node_type == child_type:
                child_id = f"{environment}_{index:02d}"

        if parent_id and child_id:

            existing_dependencies = db.get_dependencies()

            already_exists = any(
                d["parent_node"] == parent_id
                and d["child_node"] == child_id
                for d in existing_dependencies
            )

            if not already_exists:
                db.add_dependency(parent_id, child_id)

    print("\nDefault system created successfully.\n")


# ============================================================
# TEST FUNCTIONS
# ============================================================

def test_node_status(node):
    if node["status"] == "ONLINE":
        return "PASS", "Node is online."

    return "FAIL", "Node is offline."


def test_node_health(node):
    if node["health"] >= 50:
        return "PASS", f"Health level is {node['health']}%."

    return "FAIL", f"Health level is critically low: {node['health']}%."


def test_cpu(node):
    if node["cpu_usage"] <= 90:
        return "PASS", f"CPU usage is {node['cpu_usage']}%."

    return "FAIL", f"CPU usage is too high: {node['cpu_usage']}%."


def test_memory(node):
    if node["memory_usage"] <= 90:
        return "PASS", f"Memory usage is {node['memory_usage']}%."

    return "FAIL", f"Memory usage is too high: {node['memory_usage']}%."


def test_failures(node):

    failures = db.get_node_failures(node["node_id"])

    active_failures = [
        failure
        for failure in failures
        if failure["active"]
    ]

    if not active_failures:
        return "PASS", "No active failures detected."

    failure_names = ", ".join(
        failure["failure_type"]
        for failure in active_failures
    )

    return "FAIL", f"Active failures: {failure_names}"


# ============================================================
# RUN TESTS
# ============================================================

def run_tests():

    print("\n========================================")
    print("        GHOSTLAB TEST EXECUTION")
    print("========================================\n")

    run_id = db.create_run()

    print(f"Run ID: {run_id}\n")

    nodes = db.get_nodes()

    if not nodes:
        print("No nodes available for testing.")
        return

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for node in nodes:

        print("----------------------------------------")
        print(f"Testing: {node['node_id']}")
        print(f"Type: {node['node_type']}")
        print("----------------------------------------")

        tests = [
            (
                "Node Availability",
                test_node_status
            ),
            (
                "Health Check",
                test_node_health
            ),
            (
                "CPU Usage Test",
                test_cpu
            ),
            (
                "Memory Usage Test",
                test_memory
            ),
            (
                "Failure Detection",
                test_failures
            )
        ]

        for test_name, test_function in tests:

            status, message = test_function(node)

            total_tests += 1

            if status == "PASS":
                passed_tests += 1
            else:
                failed_tests += 1

            db.save_test(
                f"{test_name} - {node['node_id']}"
            )

            db.save_result(
                f"{test_name} - {node['node_id']}",
                status,
                message
            )

            print(
                f"[{status}] "
                f"{test_name}: "
                f"{message}"
            )

    # ========================================================
    # DEPENDENCY TESTING
    # ========================================================

    print("\n========================================")
    print("        DEPENDENCY ANALYSIS")
    print("========================================\n")

    dependencies = db.get_dependencies()

    node_map = {
        node["node_id"]: node
        for node in nodes
    }

    for dependency in dependencies:

        parent_id = dependency["parent_node"]
        child_id = dependency["child_node"]

        if parent_id not in node_map:
            continue

        if child_id not in node_map:
            continue

        parent = node_map[parent_id]
        child = node_map[child_id]

        test_name = (
            f"Dependency: "
            f"{parent_id} -> {child_id}"
        )

        if parent["status"] == "ONLINE":

            status = "PASS"
            message = (
                f"Parent {parent_id} is online. "
                f"Dependency available."
            )

        else:

            status = "FAIL"
            message = (
                f"Parent {parent_id} is offline. "
                f"{child_id} may be affected."
            )

        total_tests += 1

        if status == "PASS":
            passed_tests += 1
        else:
            failed_tests += 1

        db.save_test(test_name)

        db.save_result(
            test_name,
            status,
            message
        )

        print(f"[{status}] {message}")

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n========================================")
    print("             TEST SUMMARY")
    print("========================================")

    print(f"Total Tests : {total_tests}")
    print(f"Passed      : {passed_tests}")
    print(f"Failed      : {failed_tests}")

    if total_tests > 0:

        success_rate = (
            passed_tests / total_tests
        ) * 100

        print(
            f"Success Rate: "
            f"{success_rate:.1f}%"
        )

    print("========================================\n")

    db.save_event(
        "TEST_RUN",
        (
            f"Test run completed. "
            f"Total={total_tests}, "
            f"Passed={passed_tests}, "
            f"Failed={failed_tests}"
        )
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("========================================")
    print("             GHOSTLAB")
    print(" Virtual System Testing & Diagnostics")
    print("========================================")
    print()

    create_default_system()

    run_tests()

    print("GHOSTLAB execution completed.")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Backend.database.database_manager import DatabaseManager

app = FastAPI(title="GHOSTLAB API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

db = DatabaseManager()


# ============================================================
# ENVIRONMENTS
# ============================================================

ENVIRONMENTS = {
    "AUTOMOTIVE": [
        "Battery",
        "Engine",
        "Brake",
        "Transmission",
        "ECU",
        "Lighting",
        "Infotainment",
        "Cooling System",
        "Steering"
    ],

    "PC": [
        "Power Supply",
        "CPU",
        "RAM",
        "GPU",
        "Storage",
        "Network Adapter",
        "Operating System",
        "Cooling System",
        "Motherboard"
    ],

    "AIRCRAFT": [
        "Battery",
        "Engine",
        "Flight Computer",
        "Navigation",
        "Radar",
        "Hydraulic System",
        "Landing Gear",
        "Communication",
        "Fuel System"
    ]
}


# ============================================================
# NODE PRIORITIES
# ============================================================

NODE_PRIORITIES = {
    "Battery": "CRITICAL",
    "Power Supply": "CRITICAL",
    "Engine": "CRITICAL",
    "CPU": "CRITICAL",
    "Flight Computer": "CRITICAL",

    "ECU": "HIGH",
    "GPU": "HIGH",
    "RAM": "HIGH",
    "Navigation": "HIGH",
    "Hydraulic System": "HIGH",
    "Fuel System": "HIGH",
    "Brake": "HIGH",
    "Steering": "HIGH",
    "Operating System": "HIGH",
    "Landing Gear": "HIGH",

    "Transmission": "MEDIUM",
    "Storage": "MEDIUM",
    "Network Adapter": "MEDIUM",
    "Radar": "MEDIUM",
    "Cooling System": "MEDIUM",
    "Communication": "MEDIUM",

    "Lighting": "LOW",
    "Infotainment": "LOW"
}


# ============================================================
# FAILURES
# ============================================================

FAILURES = [
    "CRASH",
    "TIMEOUT",
    "NETWORK",
    "HIGH_CPU",
    "HIGH_MEMORY",
    "SENSOR_FAULT"
]


FAILURE_INFO = {
    "CRASH": {
        "description": "Node completely stops operating.",
        "status": "OFFLINE"
    },

    "TIMEOUT": {
        "description": "Node stops responding within the expected time.",
        "status": "DEGRADED"
    },

    "NETWORK": {
        "description": "Network communication failure.",
        "status": "DEGRADED"
    },

    "HIGH_CPU": {
        "description": "CPU usage becomes critically high.",
        "status": "WARNING"
    },

    "HIGH_MEMORY": {
        "description": "Memory usage becomes critically high.",
        "status": "WARNING"
    },

    "SENSOR_FAULT": {
        "description": "Sensor provides invalid or unreliable data.",
        "status": "DEGRADED"
    }
}


# ============================================================
# DEPENDENCIES
# ============================================================

DEPENDENCIES = {

    "AUTOMOTIVE": [
        ("Battery", "Lighting"),
        ("Battery", "Infotainment"),
        ("Engine", "Transmission"),
        ("Engine", "Cooling System"),
        ("ECU", "Engine")
    ],

    "PC": [
        ("Power Supply", "Motherboard"),
        ("Motherboard", "CPU"),
        ("Motherboard", "RAM"),
        ("Motherboard", "GPU"),
        ("Operating System", "Network Adapter"),
        ("CPU", "Cooling System")
    ],

    "AIRCRAFT": [
        ("Battery", "Flight Computer"),
        ("Flight Computer", "Navigation"),
        ("Flight Computer", "Radar"),
        ("Engine", "Hydraulic System"),
        ("Fuel System", "Engine")
    ]
}


PRIORITY_RANK = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def sync_dependencies():

    nodes = {
        n["node_id"]: n
        for n in db.get_nodes()
    }

    for environment, pairs in DEPENDENCIES.items():

        for parent_type, child_type in pairs:

            parents = [
                n for n in nodes.values()
                if n["environment"] == environment
                and n["node_type"] == parent_type
            ]

            children = [
                n for n in nodes.values()
                if n["environment"] == environment
                and n["node_type"] == child_type
            ]

            for parent in parents:

                for child in children:

                    db.add_dependency(
                        parent["node_id"],
                        child["node_id"]
                    )


def active_failures(node_id):

    return [
        f
        for f in db.get_node_failures(node_id)
        if f["active"]
    ]


def parents_of(node_id):

    return [
        d["parent_node"]
        for d in db.get_dependencies()
        if d["child_node"] == node_id
    ]


def node_blocked(node_id):

    node = db.get_node(node_id)

    if not node:
        return True

    if active_failures(node_id):
        return True

    for parent in parents_of(node_id):

        parent_node = db.get_node(parent)

        if parent_node and parent_node["status"] != "ONLINE":
            return True

    return False


def refresh_dependents(parent_id):

    queue = [parent_id]
    seen = set()

    while queue:

        parent = queue.pop(0)

        if parent in seen:
            continue

        seen.add(parent)

        parent_node = db.get_node(parent)

        unavailable = bool(
            parent_node
            and parent_node["status"] != "ONLINE"
        )

        for child in db.get_children(parent):

            if unavailable:

                if not active_failures(child):

                    db.update_node_status(
                        child,
                        "OFFLINE"
                    )

                    db.save_event(
                        "DEPENDENCY",
                        f"{child} powered OFF because {parent} is unavailable"
                    )

            else:

                if (
                    not active_failures(child)
                    and not any(
                        (db.get_node(p) or {}).get("status") != "ONLINE"
                        for p in parents_of(child)
                    )
                ):

                    db.update_node_status(
                        child,
                        "ONLINE"
                    )

                    db.save_event(
                        "DEPENDENCY",
                        f"{child} restored because its dependencies are online"
                    )

            queue.append(child)


def restore_node_state(node_id):

    failures = active_failures(node_id)

    if failures:

        failure_type = failures[-1]["failure_type"]

        info = FAILURE_INFO.get(
            failure_type,
            {}
        )

        db.update_node_status(
            node_id,
            info.get("status", "DEGRADED")
        )

        return

    if node_blocked(node_id):

        db.update_node_status(
            node_id,
            "OFFLINE"
        )

    else:

        db.update_node_status(
            node_id,
            "ONLINE"
        )

    db.update_node_metrics(
        node_id,
        health=100,
        cpu_usage=0,
        memory_usage=0
    )


def failure_options(node_type):

    options = [
        "CRASH",
        "TIMEOUT"
    ]

    if node_type in {
        "Network Adapter",
        "Communication",
        "Navigation",
        "Radar",
        "Operating System"
    }:

        options += [
            "NETWORK"
        ]

    if node_type in {
        "CPU",
        "GPU",
        "RAM",
        "Motherboard",
        "Operating System",
        "Engine",
        "ECU"
    }:

        options += [
            "HIGH_CPU",
            "HIGH_MEMORY"
        ]

    if node_type in {
        "ECU",
        "Engine",
        "Battery",
        "Navigation",
        "Radar",
        "Hydraulic System",
        "Landing Gear",
        "Communication",
        "Fuel System",
        "Steering"
    }:

        options += [
            "SENSOR_FAULT"
        ]

    return list(dict.fromkeys(options))


# ============================================================
# BASIC API
# ============================================================

@app.get("/")
def home():

    return {
        "message": "GHOSTLAB API is running"
    }


@app.get("/status")
def status():

    return {
        "status": "ONLINE",
        "system": "GHOSTLAB"
    }


# ============================================================
# ENVIRONMENTS
# ============================================================

@app.get("/environments")
def get_environments():

    return list(
        ENVIRONMENTS.keys()
    )


@app.get("/environments/{environment}")
def get_environment_nodes(environment: str):

    environment = environment.upper()

    if environment not in ENVIRONMENTS:

        return {
            "success": False,
            "message": "Environment not found"
        }

    return ENVIRONMENTS[environment]


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/dashboard")
def dashboard():

    sync_dependencies()

    return {
        "nodes": db.get_nodes(),
        "results": db.get_results(),
        "failures": db.get_failures(),
        "events": db.get_events()
    }


# ============================================================
# NODES
# ============================================================

@app.get("/nodes")
def get_nodes():

    sync_dependencies()

    return db.get_nodes()


@app.get("/nodes/{node_id}")
def get_node(node_id: str):

    node = db.get_node(node_id)

    if not node:

        return {
            "success": False,
            "message": "Node not found"
        }

    return {
        "success": True,
        "node": node,
        "failures": db.get_node_failures(node_id)
    }


@app.get("/nodes/{node_id}/failures")
def get_node_failures(node_id: str):

    if not db.get_node(node_id):

        return []

    return db.get_node_failures(node_id)


@app.post("/nodes")
def add_node(node: dict):

    node_id = str(
        node.get("node_id", "")
    ).strip()

    node_type = node.get(
        "node_type",
        "ECU"
    )

    environment = str(
        node.get(
            "environment",
            "AUTOMOTIVE"
        )
    ).upper()

    if not node_id:

        return {
            "success": False,
            "message": "Node ID is required"
        }

    if environment not in ENVIRONMENTS:

        return {
            "success": False,
            "message": "Invalid environment"
        }

    if node_type not in ENVIRONMENTS[environment]:

        return {
            "success": False,
            "message": f"{node_type} is not available in {environment}"
        }

    if db.get_node(node_id):

        return {
            "success": False,
            "message": f"{node_id} already exists"
        }

    db.save_node(
        node_id,
        node_type,
        "OFFLINE",
        100,
        0,
        0,
        NODE_PRIORITIES.get(
            node_type,
            "MEDIUM"
        ),
        environment
    )

    db.save_event(
        "NODE_CREATED",
        f"{node_id} created in {environment}"
    )

    sync_dependencies()

    return {
        "success": True,
        "message": f"{node_id} created successfully",
        "node": db.get_node(node_id)
    }


@app.put("/nodes/{node_id}")
def update_node(
    node_id: str,
    node: dict
):

    if not db.get_node(node_id):

        return {
            "success": False,
            "message": "Node not found"
        }

    node_type = node.get(
        "node_type"
    )

    if not node_type:

        return {
            "success": False,
            "message": "Node type is required"
        }

    db.update_node(
        node_id,
        node_type
    )

    db.save_event(
        "NODE_UPDATED",
        f"{node_id} updated"
    )

    return {
        "success": True,
        "message": f"{node_id} updated successfully"
    }


@app.delete("/nodes/{node_id}")
def delete_node(node_id: str):

    if not db.get_node(node_id):

        return {
            "success": False,
            "message": "Node not found"
        }

    db.delete_node(
        node_id
    )

    db.save_event(
        "NODE_DELETED",
        f"{node_id} deleted"
    )

    return {
        "success": True,
        "message": f"{node_id} deleted successfully"
    }


# ============================================================
# NODE POWER
# ============================================================

@app.post("/nodes/{node_id}/power")
def power_node(
    node_id: str,
    data: dict
):

    node = db.get_node(node_id)

    if not node:

        return {
            "success": False,
            "message": "Node not found"
        }

    action = str(
        data.get(
            "action",
            "ON"
        )
    ).upper()

    if action == "OFF":

        db.update_node_status(
            node_id,
            "OFFLINE"
        )

        db.save_event(
            "POWER_OFF",
            f"{node_id} powered OFF"
        )

        refresh_dependents(
            node_id
        )

        return {
            "success": True,
            "message": f"{node_id} powered off"
        }

    if action == "ON":

        failures = active_failures(
            node_id
        )

        if failures:

            return {
                "success": False,
                "message": (
                    f"{node_id} cannot start. "
                    f"Active failure: "
                    f"{', '.join(f['failure_type'] for f in failures)}"
                )
            }

        blocked = [
            p
            for p in parents_of(node_id)
            if (
                db.get_node(p) or {}
            ).get("status") != "ONLINE"
        ]

        if blocked:

            return {
                "success": False,
                "message": (
                    f"{node_id} cannot start. "
                    f"Dependency {blocked[0]} is offline."
                )
            }

        db.update_node_status(
            node_id,
            "ONLINE"
        )

        db.update_node_metrics(
            node_id,
            health=100
        )

        db.save_event(
            "POWER_ON",
            f"{node_id} powered ON"
        )

        refresh_dependents(
            node_id
        )

        return {
            "success": True,
            "message": f"{node_id} powered on"
        }

    return {
        "success": False,
        "message": "Invalid power action"
    }


# ============================================================
# ENVIRONMENT POWER
# ============================================================

@app.post("/environment/power")
def power_environment(data: dict):

    environment = str(
        data.get(
            "environment",
            "AUTOMOTIVE"
        )
    ).upper()

    action = str(
        data.get(
            "action",
            "ON"
        )
    ).upper()

    nodes = [
        n
        for n in db.get_nodes()
        if n["environment"] == environment
    ]

    if not nodes:

        return {
            "success": False,
            "message": f"No nodes found in {environment}"
        }

    if action == "OFF":

        for node in nodes:

            db.update_node_status(
                node["node_id"],
                "OFFLINE"
            )

        db.save_event(
            "POWER_ALL_OFF",
            f"All {environment} nodes powered OFF"
        )

        for node in nodes:

            refresh_dependents(
                node["node_id"]
            )

        return {
            "success": True,
            "message": f"All {environment} nodes powered off"
        }

    if action == "ON":

        ordered = sorted(
            nodes,
            key=lambda n: PRIORITY_RANK.get(
                n["priority"],
                2
            ),
            reverse=True
        )

        started = []
        blocked = []

        remaining = {
            n["node_id"]: n
            for n in ordered
        }

        progress = True

        while remaining and progress:

            progress = False

            for node_id, node in list(
                remaining.items()
            ):

                if active_failures(
                    node_id
                ):

                    blocked.append(
                        node_id
                    )

                    del remaining[
                        node_id
                    ]

                    continue

                if any(
                    (
                        db.get_node(parent)
                        or {}
                    ).get("status") != "ONLINE"
                    for parent in parents_of(node_id)
                ):

                    continue

                db.update_node_status(
                    node_id,
                    "ONLINE"
                )

                db.update_node_metrics(
                    node_id,
                    health=100
                )

                started.append(
                    node_id
                )

                del remaining[
                    node_id
                ]

                progress = True

        blocked.extend(
            remaining.keys()
        )

        db.save_event(
            "POWER_ALL_ON",
            (
                f"{environment}: "
                f"{len(started)} started, "
                f"{len(blocked)} blocked"
            )
        )

        return {
            "success": True,
            "message": (
                f"{len(started)} nodes started. "
                f"{len(blocked)} blocked by "
                f"failures/dependencies."
            ),
            "started": started,
            "blocked": blocked
        }

    return {
        "success": False,
        "message": "Invalid power action"
    }


# ============================================================
# FAILURE OPTIONS
# ============================================================

@app.get(
    "/node-types/{environment}/{node_type}/failures"
)
def get_failure_options(
    environment: str,
    node_type: str
):

    environment = environment.upper()

    if (
        environment not in ENVIRONMENTS
        or node_type not in ENVIRONMENTS[environment]
    ):

        return {
            "failures": []
        }

    return {
        "failures": failure_options(
            node_type
        )
    }


# ============================================================
# FAILURES
# ============================================================

@app.get("/failures")
def get_failures():

    return db.get_failures()


@app.post("/failures")
def inject_failure(
    failure: dict
):

    node_id = failure.get(
        "node_id"
    )

    failure_type = str(
        failure.get(
            "failure_type",
            ""
        )
    ).upper()

    node = (
        db.get_node(node_id)
        if node_id
        else None
    )

    if not node:

        return {
            "success": False,
            "message": "Node not found"
        }

    if failure_type not in failure_options(
        node["node_type"]
    ):

        return {
            "success": False,
            "message": (
                f"{failure_type} is not valid "
                f"for {node['node_type']}"
            )
        }

    if any(
        f["active"]
        and f["failure_type"] == failure_type
        for f in db.get_node_failures(
            node_id
        )
    ):

        return {
            "success": False,
            "message": (
                f"{failure_type} is already "
                f"active on {node_id}"
            )
        }

    db.save_failure(
        node_id,
        failure_type
    )

    if failure_type == "CRASH":

        db.update_node_status(
            node_id,
            "OFFLINE"
        )

        db.update_node_metrics(
            node_id,
            health=0
        )

    elif failure_type in {
        "TIMEOUT",
        "NETWORK",
        "SENSOR_FAULT"
    }:

        db.update_node_status(
            node_id,
            "DEGRADED"
        )

        db.update_node_metrics(
            node_id,
            health=50
        )

    elif failure_type == "HIGH_CPU":

        db.update_node_status(
            node_id,
            "WARNING"
        )

        db.update_node_metrics(
            node_id,
            health=60,
            cpu_usage=95
        )

    elif failure_type == "HIGH_MEMORY":

        db.update_node_status(
            node_id,
            "WARNING"
        )

        db.update_node_metrics(
            node_id,
            health=60,
            memory_usage=95
        )

    db.save_event(
        "FAILURE",
        f"{failure_type} injected into {node_id}"
    )

    refresh_dependents(
        node_id
    )

    return {
        "success": True,
        "message": (
            f"{failure_type} injected into {node_id}"
        )
    }


# ============================================================
# REMOVE FAILURE
# ============================================================

@app.delete("/failures/{failure_id}")
def remove_failure(
    failure_id: int
):

    rows = db.get_failures()

    failure = next(
        (
            f
            for f in rows
            if f["id"] == failure_id
        ),
        None
    )

    if not failure:

        return {
            "success": False,
            "message": "Failure not found"
        }

    db.remove_failure(
        failure_id
    )

    restore_node_state(
        failure["node_id"]
    )

    refresh_dependents(
        failure["node_id"]
    )

    db.save_event(
        "RECOVERY",
        (
            f"Failure #{failure_id} "
            f"removed from {failure['node_id']}"
        )
    )

    return {
        "success": True,
        "message": "Failure removed successfully"
    }


# ============================================================
# NODE RECOVERY
# ============================================================

@app.post("/nodes/{node_id}/recover")
def recover_node(
    node_id: str
):

    if not db.get_node(node_id):

        return {
            "success": False,
            "message": "Node not found"
        }

    db.recover_node(
        node_id
    )

    db.save_event(
        "RECOVERY",
        f"{node_id} recovered successfully"
    )

    refresh_dependents(
        node_id
    )

    return {
        "success": True,
        "message": (
            f"{node_id} recovered successfully"
        )
    }


# ============================================================
# DEPENDENCIES
# ============================================================

@app.get("/dependencies")
def get_dependencies():

    sync_dependencies()

    return db.get_dependencies()


@app.post("/dependencies")
def add_dependency(
    dependency: dict
):

    parent = dependency.get(
        "parent_node"
    )

    child = dependency.get(
        "child_node"
    )

    if not parent or not child:

        return {
            "success": False,
            "message": (
                "Both parent_node and "
                "child_node are required"
            )
        }

    if (
        not db.get_node(parent)
        or not db.get_node(child)
    ):

        return {
            "success": False,
            "message": (
                "Both nodes must exist"
            )
        }

    db.add_dependency(
        parent,
        child
    )

    db.save_event(
        "DEPENDENCY",
        f"{child} depends on {parent}"
    )

    return {
        "success": True,
        "message": (
            "Dependency created successfully"
        )
    }


# ============================================================
# RESULTS / TESTS / EVENTS / HISTORY
# ============================================================

@app.get("/results")
def get_results():

    return db.get_results()


@app.get("/tests")
def get_tests():

    return db.get_tests()


@app.get("/events")
def get_events():

    return db.get_events()


@app.delete("/events")
def clear_events():

    db.clear_events()

    return {
        "success": True,
        "message": "Logs cleared successfully"
    }


@app.get("/runs")
def get_runs():

    return db.get_runs()


@app.delete("/runs")
def clear_runs():

    db.clear_runs()

    return {
        "success": True,
        "message": "History cleared successfully"
    }


# ============================================================
# TEST RUNNER
# ============================================================

@app.post("/run-tests")
def run_tests(
    data: dict = None
):

    environment = (
        data or {}
    ).get("environment")

    environment = (
        environment.upper()
        if environment
        else None
    )

    run_id = db.create_run()

    db.save_event(
        "TEST_START",
        (
            f"Test campaign #{run_id} started"
            + (
                f" for {environment}"
                if environment
                else ""
            )
        )
    )

    nodes = [
        n
        for n in db.get_nodes()
        if (
            not environment
            or n["environment"] == environment
        )
    ]

    passed = 0
    failed = 0

    for node in nodes:

        name = (
            f"{node['node_type']} Health Test"
        )

        db.save_test(
            name
        )

        if node["status"] == "OFFLINE":

            status = "FAIL"

            message = (
                f"{node['node_id']} is offline"
            )

            failed += 1

        elif node["health"] < 50:

            status = "FAIL"

            message = (
                f"{node['node_id']} "
                f"health is critically low"
            )

            failed += 1

        elif node["cpu_usage"] > 90:

            status = "FAIL"

            message = (
                f"{node['node_id']} "
                f"CPU usage is too high"
            )

            failed += 1

        elif node["memory_usage"] > 90:

            status = "FAIL"

            message = (
                f"{node['node_id']} "
                f"memory usage is too high"
            )

            failed += 1

        else:

            status = "PASS"

            message = (
                f"{node['node_id']} "
                f"passed all checks"
            )

            passed += 1

        db.save_result(
            name,
            status,
            message
        )

    db.save_event(
        "TEST_COMPLETE",
        (
            f"Test campaign #{run_id} "
            f"completed with "
            f"{passed} passed and "
            f"{failed} failed"
        )
    )

    return {
        "success": True,
        "run_id": run_id,
        "passed": passed,
        "failed": failed,
        "message": (
            "GHOSTLAB tests completed successfully"
        )
    }
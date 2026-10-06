import sqlite3

from datetime import datetime

from pathlib import Path


class DatabaseManager:

    def __init__(
        self,
        database_name="ghostlab.db"
    ):

        path = Path(database_name)

        if not path.is_absolute():

            path = (
                Path(__file__)
                .resolve()
                .parents[2]
                / path
            )

        self.database_name = str(path)

        self.create_tables()


    def connect(self):

        return sqlite3.connect(
            self.database_name
        )


    def _ensure_column(
        self,
        cursor,
        table,
        column,
        definition
    ):

        cursor.execute(
            f"PRAGMA table_info({table})"
        )

        columns = {
            row[1]
            for row in cursor.fetchall()
        }

        if column not in columns:

            cursor.execute(
                f"""
                ALTER TABLE {table}
                ADD COLUMN {column}
                {definition}
                """
            )


    def create_tables(self):

        with self.connect() as connection:

            cursor = connection.cursor()


            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS nodes (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    node_id TEXT UNIQUE,

                    node_type TEXT,

                    status TEXT DEFAULT 'OFFLINE',

                    health INTEGER DEFAULT 100,

                    cpu_usage INTEGER DEFAULT 0,

                    memory_usage INTEGER DEFAULT 0,

                    priority TEXT DEFAULT 'MEDIUM',

                    environment TEXT DEFAULT 'AUTOMOTIVE'

                )
                """
            )


            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tests (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    test_name TEXT

                )
                """
            )


            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    run_time TEXT

                )
                """
            )


            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS results (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    test_name TEXT,

                    status TEXT,

                    message TEXT

                )
                """
            )


            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS failures (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    node_id TEXT,

                    failure_type TEXT,

                    active INTEGER DEFAULT 1

                )
                """
            )


            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS events (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    event_type TEXT,

                    description TEXT,

                    event_time TEXT

                )
                """
            )


            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS dependencies (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    parent_node TEXT,

                    child_node TEXT,

                    UNIQUE(parent_node, child_node)

                )
                """
            )


            node_columns = {

                "status":
                    "TEXT DEFAULT 'OFFLINE'",

                "health":
                    "INTEGER DEFAULT 100",

                "cpu_usage":
                    "INTEGER DEFAULT 0",

                "memory_usage":
                    "INTEGER DEFAULT 0",

                "priority":
                    "TEXT DEFAULT 'MEDIUM'",

                "environment":
                    "TEXT DEFAULT 'AUTOMOTIVE'"

            }


            for column, definition in node_columns.items():

                self._ensure_column(
                    cursor,
                    "nodes",
                    column,
                    definition
                )


            self._ensure_column(
                cursor,
                "failures",
                "active",
                "INTEGER DEFAULT 1"
            )


            self._ensure_column(
                cursor,
                "events",
                "event_time",
                "TEXT"
            )


    # ============================================================
    # NODES
    # ============================================================

    def save_node(
        self,
        node_id,
        node_type,
        status="OFFLINE",
        health=100,
        cpu_usage=0,
        memory_usage=0,
        priority="MEDIUM",
        environment="AUTOMOTIVE"
    ):

        with self.connect() as connection:

            connection.execute(
                """
                INSERT INTO nodes (

                    node_id,
                    node_type,
                    status,
                    health,
                    cpu_usage,
                    memory_usage,
                    priority,
                    environment

                )

                VALUES (
                    ?,?,?,?,?,?,?,?
                )

                ON CONFLICT(node_id)
                DO UPDATE SET

                    node_type=excluded.node_type,

                    status=excluded.status,

                    health=excluded.health,

                    cpu_usage=excluded.cpu_usage,

                    memory_usage=excluded.memory_usage,

                    priority=excluded.priority,

                    environment=excluded.environment
                """,
                (
                    node_id,
                    node_type,
                    status,
                    health,
                    cpu_usage,
                    memory_usage,
                    priority,
                    environment
                )
            )


    def get_nodes(self):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT

                    node_id,
                    node_type,
                    status,
                    health,
                    cpu_usage,
                    memory_usage,
                    priority,
                    environment

                FROM nodes

                ORDER BY id DESC
                """
            ).fetchall()


        keys = (
            "node_id",
            "node_type",
            "status",
            "health",
            "cpu_usage",
            "memory_usage",
            "priority",
            "environment"
        )


        return [
            dict(zip(keys, row))
            for row in rows
        ]


    def get_node(
        self,
        node_id
    ):

        with self.connect() as connection:

            row = connection.execute(
                """
                SELECT

                    node_id,
                    node_type,
                    status,
                    health,
                    cpu_usage,
                    memory_usage,
                    priority,
                    environment

                FROM nodes

                WHERE node_id=?
                """,
                (node_id,)
            ).fetchone()


        if not row:

            return None


        keys = (
            "node_id",
            "node_type",
            "status",
            "health",
            "cpu_usage",
            "memory_usage",
            "priority",
            "environment"
        )


        return dict(
            zip(
                keys,
                row
            )
        )


    def update_node(
        self,
        node_id,
        node_type
    ):

        with self.connect() as connection:

            connection.execute(
                """
                UPDATE nodes

                SET node_type=?

                WHERE node_id=?
                """,
                (
                    node_type,
                    node_id
                )
            )


    def update_node_status(
        self,
        node_id,
        status
    ):

        with self.connect() as connection:

            connection.execute(
                """
                UPDATE nodes

                SET status=?

                WHERE node_id=?
                """,
                (
                    status,
                    node_id
                )
            )


    def update_node_metrics(
        self,
        node_id,
        health=None,
        cpu_usage=None,
        memory_usage=None
    ):

        fields = []
        values = []


        if health is not None:

            fields.append(
                "health=?"
            )

            values.append(
                health
            )


        if cpu_usage is not None:

            fields.append(
                "cpu_usage=?"
            )

            values.append(
                cpu_usage
            )


        if memory_usage is not None:

            fields.append(
                "memory_usage=?"
            )

            values.append(
                memory_usage
            )


        if not fields:

            return


        values.append(
            node_id
        )


        with self.connect() as connection:

            connection.execute(
                f"""
                UPDATE nodes

                SET {",".join(fields)}

                WHERE node_id=?
                """,
                values
            )


    def delete_node(
        self,
        node_id
    ):

        with self.connect() as connection:

            connection.execute(
                """
                DELETE FROM nodes

                WHERE node_id=?
                """,
                (node_id,)
            )


            connection.execute(
                """
                DELETE FROM failures

                WHERE node_id=?
                """,
                (node_id,)
            )


            connection.execute(
                """
                DELETE FROM dependencies

                WHERE parent_node=?

                   OR child_node=?
                """,
                (
                    node_id,
                    node_id
                )
            )


    # ============================================================
    # FAILURES
    # ============================================================

    def save_failure(
        self,
        node_id,
        failure_type
    ):

        with self.connect() as connection:

            connection.execute(
                """
                INSERT INTO failures (

                    node_id,
                    failure_type,
                    active

                )

                VALUES (?, ?, 1)
                """,
                (
                    node_id,
                    failure_type
                )
            )


    def get_failures(self):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT

                    id,
                    node_id,
                    failure_type,
                    active

                FROM failures

                ORDER BY id DESC
                """
            ).fetchall()


        return [

            {
                "id": row[0],
                "node_id": row[1],
                "failure_type": row[2],
                "active": bool(row[3])
            }

            for row in rows

        ]


    def get_node_failures(
        self,
        node_id
    ):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT

                    id,
                    node_id,
                    failure_type,
                    active

                FROM failures

                WHERE node_id=?

                ORDER BY id DESC
                """,
                (node_id,)
            ).fetchall()


        return [

            {
                "id": row[0],
                "node_id": row[1],
                "failure_type": row[2],
                "active": bool(row[3])
            }

            for row in rows

        ]


    def remove_failure(
        self,
        failure_id
    ):

        with self.connect() as connection:

            connection.execute(
                """
                UPDATE failures

                SET active=0

                WHERE id=?
                """,
                (failure_id,)
            )


    def clear_failures(self):

        with self.connect() as connection:

            connection.execute(
                "DELETE FROM failures"
            )


    def recover_node(
        self,
        node_id
    ):

        with self.connect() as connection:

            connection.execute(
                """
                UPDATE nodes

                SET

                    status='ONLINE',
                    health=100,
                    cpu_usage=0,
                    memory_usage=0

                WHERE node_id=?
                """,
                (node_id,)
            )


            connection.execute(
                """
                UPDATE failures

                SET active=0

                WHERE node_id=?
                """,
                (node_id,)
            )


    # ============================================================
    # TESTS
    # ============================================================

    def save_test(
        self,
        test_name
    ):

        with self.connect() as connection:

            connection.execute(
                """
                INSERT INTO tests(test_name)

                VALUES(?)
                """,
                (test_name,)
            )


    def get_tests(self):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    id,
                    test_name

                FROM tests

                ORDER BY id DESC
                """
            ).fetchall()


        return [

            {
                "id": row[0],
                "test_name": row[1]
            }

            for row in rows

        ]


    def save_result(
        self,
        test_name,
        status,
        message
    ):

        with self.connect() as connection:

            connection.execute(
                """
                INSERT INTO results(
                    test_name,
                    status,
                    message
                )

                VALUES(?,?,?)
                """,
                (
                    test_name,
                    status,
                    message
                )
            )


    def get_results(self):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    id,
                    test_name,
                    status,
                    message

                FROM results

                ORDER BY id DESC
                """
            ).fetchall()


        return [

            {
                "id": row[0],
                "test_name": row[1],
                "status": row[2],
                "message": row[3]
            }

            for row in rows

        ]


    # ============================================================
    # RUN HISTORY
    # ============================================================

    def create_run(self):

        with self.connect() as connection:

            cursor = connection.execute(
                """
                INSERT INTO runs(run_time)

                VALUES(?)
                """,
                (
                    datetime.now()
                    .strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                )
            )


            return cursor.lastrowid


    def get_runs(self):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    id,
                    run_time

                FROM runs

                ORDER BY id DESC
                """
            ).fetchall()


        return [

            {
                "id": row[0],
                "run_time": row[1]
            }

            for row in rows

        ]


    def clear_runs(self):

        with self.connect() as connection:

            connection.execute(
                "DELETE FROM runs"
            )


    # ============================================================
    # EVENTS
    # ============================================================

    def save_event(
        self,
        event_type,
        description
    ):

        with self.connect() as connection:

            connection.execute(
                """
                INSERT INTO events(
                    event_type,
                    description,
                    event_time
                )

                VALUES(?,?,?)
                """,
                (
                    event_type,
                    description,
                    datetime.now()
                    .strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
            )


    def get_events(self):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT

                    id,
                    event_type,
                    description,
                    event_time

                FROM events

                ORDER BY id DESC
                """
            ).fetchall()


        return [

            {
                "id": row[0],
                "event_type": row[1],
                "description": row[2],
                "event_time": row[3]
            }

            for row in rows

        ]


    def clear_events(self):

        with self.connect() as connection:

            connection.execute(
                "DELETE FROM events"
            )


    # ============================================================
    # DEPENDENCIES
    # ============================================================

    def add_dependency(
        self,
        parent_node,
        child_node
    ):

        if parent_node == child_node:

            return


        with self.connect() as connection:

            connection.execute(
                """
                INSERT OR IGNORE INTO dependencies(
                    parent_node,
                    child_node
                )

                VALUES(?,?)
                """,
                (
                    parent_node,
                    child_node
                )
            )


    def get_dependencies(self):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    parent_node,
                    child_node

                FROM dependencies

                ORDER BY id
                """
            ).fetchall()


        return [

            {
                "parent_node": row[0],
                "child_node": row[1]
            }

            for row in rows

        ]


    def get_children(
        self,
        parent_node
    ):

        with self.connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    child_node

                FROM dependencies

                WHERE parent_node=?
                """,
                (parent_node,)
            ).fetchall()


        return [
            row[0]
            for row in rows
        ]

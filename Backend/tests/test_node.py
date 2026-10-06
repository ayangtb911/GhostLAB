from simulator.node import Node


def test_node_starts():

    node = Node("TEST_01", "Test")

    node.start()

    assert node.status == "ONLINE"


def test_node_stops():

    node = Node("TEST_02", "Test")

    node.start()
    node.stop()

    assert node.status == "OFFLINE"


def test_node_initial_status():

    node = Node("TEST_03", "Test")

    assert node.status == "OFFLINE"
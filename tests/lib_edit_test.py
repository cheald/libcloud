import pytest
import libcloud
from libcloud import loadbalancer
from libcloud.common.nttcis import NttCisAPIException


def test_disable_node_snapshot(compute_driver):
    node = '040fefdb-78be-4b17-8ef9-86820bad67d9'
    assert compute_driver.ex_disable_snapshots(node) is True


def test_list_windows(compute_driver):
    loc = 'EU6'
    service_plan = 'ADVANCED'
    windows = compute_driver.list_snapshot_windows(loc, service_plan)
    for window in windows:
       print(window)
       assert 'day_of_week' in window


def test_enable_snapshot(compute_driver):
    """
    This will enable a snapshot window and create an initial
    snapshot when it has done so. A node object and a window id are required
    :param compute_driver: The driver object for compute nodes.
    :return: True or False
    :rtype: ``bool``
    """
    window_id = 'ea646520-4272-11e8-838c-180373fb68df'
    node = '040fefdb-78be-4b17-8ef9-86820bad67d9'
    result = compute_driver.ex_enable_snapshots(node, window_id)
    assert result is True


def test_initiate_manual_snapshot_warn(compute_driver):
    with pytest.raises(RuntimeError, match=r'Found more than one server Id .*'):
        compute_driver.ex_initiate_manual_snapshot('sdk_server_1', 'dc637783-2bb2-4b92-838a-99a899b5e29b')


def test_initiate_manual_snapshot(compute_driver):
    compute_driver.ex_initiate_manual_snapshot('sdk_server_1', 'dc637783-2bb2-4b92-838a-99a899b5e29b')


def test_shutdown_server_1(compute_driver):
    node = compute_driver.ex_get_node_by_id('040fefdb-78be-4b17-8ef9-86820bad67d9 ')
    result = compute_driver.ex_shutdown_graceful(node)
    assert result is True


def test_start_server_1(compute_driver):
    node = compute_driver.ex_get_node_by_id('040fefdb-78be-4b17-8ef9-86820bad67d9 ')
    result = compute_driver.ex_start_node(node)
    assert result is True


def test_shutdown_server_2(compute_driver):
    nodes = compute_driver.list_nodes(ex_name='sdk_server_1')
    for node in nodes:
        result = compute_driver.ex_shutdown_graceful(node)
        assert result is True


def test_start_server_2(compute_driver):
    nodes = compute_driver.list_nodes(ex_name='sdk_server_1')
    for node in nodes:
        result = compute_driver.ex_start_node(node)
        assert result is True


def test_edit_metadata(compute_driver):
    node = compute_driver.ex_get_node_by_id('040fefdb-78be-4b17-8ef9-86820bad67d9 ')
    description = 'SDK  Test server'
    name = 'sdk_server_1'
    result = compute_driver.ex_edit_metadata(node, name=name, description=description)
    assert result is True


def test_edit_metadata_fails(compute_driver):
    node = compute_driver.ex_get_node_by_id('040fefdb-78be-4b17-8ef9-86820bad67d9 ')
    description = 'Test server'
    ip_address = 'EU6 Ubuntu'
    with pytest.raises(TypeError):
        result = compute_driver.ex_edit_metadata(node, ip_address=ip_address, description=description)


def test_reconfigure_node(compute_driver):
    node = compute_driver.ex_get_node_by_id('040fefdb-78be-4b17-8ef9-86820bad67d9')
    cpu_performance = 'HIGHPERFORMANCE'
    result = compute_driver.ex_reconfigure_node(node, cpu_performance=cpu_performance)
    assert result is True


def test_add_disk_by_node(compute_driver):
    """
    Speeds can be specified based on DataCenter
    :param compute_driver: libcloud.DriverType.COMPUTE.NTTCIS
    :return: NA
    """
    node = compute_driver.ex_get_node_by_id('803e5e00-b22a-450a-8827-066ff15ec977')
    shut_result = compute_driver.ex_shutdown_graceful(node)
    assert shut_result is True
    compute_driver.ex_wait_for_state('stopped', compute_driver.ex_get_node_by_id, 2, 45, node.id)
    result = compute_driver.ex_add_storage_to_node(20, node)
    assert result is True
    compute_driver.ex_wait_for_state('stopped', compute_driver.ex_get_node_by_id, 2, 180, node.id)
    result = compute_driver.ex_start_node(node)
    assert result is True


def test_add_disk_by_controller_id(compute_driver):
    node = compute_driver.ex_get_node_by_id('803e5e00-b22a-450a-8827-066ff15ec977')
    shut_result = compute_driver.ex_shutdown_graceful(node)
    assert shut_result is True
    compute_driver.ex_wait_for_state('stopped', compute_driver.ex_get_node_by_id, 2, 45, node.id)
    result = compute_driver.ex_add_storage_to_node(20, controller_id=node.extra['scsi_controller'][0].id)
    assert result is True
    compute_driver.ex_wait_for_state('stopped', compute_driver.ex_get_node_by_id, 2, 180, node.id)
    result = compute_driver.ex_start_node(node)
    assert result is True


def test_changing_diskspeed(compute_driver):
    node = compute_driver.ex_get_node_by_id('803e5e00-b22a-450a-8827-066ff15ec977')
    shut_result = compute_driver.ex_shutdown_graceful(node)
    assert shut_result is True
    compute_driver.ex_wait_for_state('stopped', compute_driver.ex_get_node_by_id, 2, 45, node.id)
    disk_id = 'f8a01c24-4768-46be-af75-9fe877f8c588'
    result = compute_driver.ex_change_storage_speed(disk_id, 'HIGHPERFORMANCE')
    assert result is True
    compute_driver.ex_wait_for_state('stopped', compute_driver.ex_get_node_by_id, 2, 240, node.id)
    result = compute_driver.ex_start_node(node)
    assert result is True


def test_changing_diskspeed_iops(compute_driver):
    node = compute_driver.ex_get_node_by_id('803e5e00-b22a-450a-8827-066ff15ec977')
    shut_result = compute_driver.ex_shutdown_graceful(node)
    assert shut_result is True
    compute_driver.ex_wait_for_state('stopped', compute_driver.ex_get_node_by_id, 2, 45, node.id)
    disk_id = 'f8a01c24-4768-46be-af75-9fe877f8c588'
    result = compute_driver.ex_change_storage_speed(disk_id, 'PROVISIONEDIOPS', iops=60)
    assert result is True
    compute_driver.ex_wait_for_state('stopped', compute_driver.ex_get_node_by_id, 2, 240, node.id)
    result = compute_driver.ex_start_node(node)
    assert result is True


def test_add_scsi_controller(compute_driver):
    node = compute_driver.ex_get_node_by_id('803e5e00-b22a-450a-8827-066ff15ec977')
    shut_result = compute_driver.ex_shutdown_graceful(node)
    assert shut_result is True
    compute_driver.ex_wait_for_state('stopped', compute_driver.ex_get_node_by_id, 2, 45, node.id)
    adapter_type = 'VMWARE_PARAVIRTUAL'
    result = compute_driver.ex_add_scsi_controller_to_node(node.id, adapter_type)
    assert result is True
    compute_driver.ex_wait_for_state('stopped', compute_driver.ex_get_node_by_id, 2, 240, node.id)
    result = compute_driver.ex_start_node(node)
    assert result is True


def test_remove_scsi_controller(compute_driver):
    node = compute_driver.ex_get_node_by_id('803e5e00-b22a-450a-8827-066ff15ec977')
    shut_result = compute_driver.ex_shutdown_graceful(node)
    assert shut_result is True
    compute_driver.ex_wait_for_state('stopped', compute_driver.ex_get_node_by_id, 2, 45, node.id)
    result = compute_driver.ex_remove_scsi_controller('f1126751-c6d5-4d64-893c-8902b8481f90')
    assert result is True
    compute_driver.ex_wait_for_state('stopped', compute_driver.ex_get_node_by_id, 2, 240, node.id)
    result = compute_driver.ex_start_node(node)
    assert result is True


def test_update_vmware_tools(compute_driver):
    pass


def test_list_locations(compute_driver):
    locations = compute_driver.list_locations()
    for location in locations:
        print(location)


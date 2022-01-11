#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.


import logging
from pathlib import Path

import pytest
import yaml
from helpers import IPAddressWorkaround, get_unit_address  # type: ignore[import]

log = logging.getLogger(__name__)

METADATA = yaml.safe_load(Path("./metadata.yaml").read_text())


@pytest.mark.abort_on_fail
async def test_build_and_deploy(ops_test, charm_under_test):
    """Deploy the charm-under-test and deploy it together with related charms."""
    # deploy charm from local source folder
    resources = {"placeholder-image": "alpine"}
    await ops_test.model.deploy(charm_under_test, resources=resources, application_name="proxy")
    # the charm should go into blocked status until the "proxied" url is configured
    await ops_test.model.wait_for_idle(apps=["proxy"], status="blocked")
    assert ops_test.model.applications["proxy"].units[0].workload_status == "blocked"


@pytest.mark.abort_on_fail
async def test_charm_goes_into_active_state_after_alertmanager_ip_provided(ops_test):
    # deploy alertmanager
    with IPAddressWorkaround(ops_test):
        await ops_test.model.deploy("ch:alertmanager-k8s", application_name="am", channel="edge")
        await ops_test.model.wait_for_idle(apps=["am"], status="active")

    # configure the proxy charm (the charm-under-test) with alertmanager's IP address
    url = f"http://{get_unit_address(ops_test, 'am', 0)}:9093"
    await ops_test.model.applications["proxy"].set_config({"url": url})

    # after IP address is configured, the charm should be in "active" status
    await ops_test.model.wait_for_idle(apps=["proxy"], status="active", timeout=60)
    assert ops_test.model.applications["proxy"].units[0].workload_status == "active"


@pytest.mark.abort_on_fail
async def test_karma_charm_goes_into_active_state_after_related_to_proxy(ops_test):
    """Confirm alertmanager is reachable, after its IP has been passed to the proxy charm."""
    # deploy karma
    await ops_test.model.deploy("ch:karma-k8s", application_name="karma", channel="edge")
    await ops_test.model.wait_for_idle(apps=["karma"], status="blocked")

    await ops_test.model.add_relation("proxy", "karma")
    # at this point all three apps should be "active"
    # karma will become active only if alertmanager is reachable; otherwise it will immediately
    # exit
    await ops_test.model.wait_for_idle(apps=["proxy", "am", "karma"], status="active")
    assert ops_test.model.applications["karma"].units[0].workload_status == "active"

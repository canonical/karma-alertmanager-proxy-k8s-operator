#!/usr/bin/env python3

#  Copyright 2021 Canonical Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
from pathlib import Path

import yaml

import pytest

log = logging.getLogger(__name__)

METADATA = yaml.safe_load(Path("./metadata.yaml").read_text())


class TestClass:
    @pytest.mark.abort_on_fail
    async def test_build_and_deploy(self, ops_test):
        """Build the charm-under-test and deploy it together with related charms.
        Assert on the unit status before any relations/configurations take place.
        """
        # build and deploy charm from local source folder
        charm_under_test = await ops_test.build_charm(".")
        resources = {"placeholder-image": "alpine"}
        await ops_test.model.deploy(
            charm_under_test, resources=resources, application_name="proxy"
        )
        # the charm should go into blocked status until the "proxied" url is configured
        await ops_test.model.wait_for_idle(apps=["proxy"], wait_for_status="blocked")
        assert ops_test.model.applications["proxy"].units[0].workload_status == "blocked"

        async def cli_deploy_and_wait(
            name: str, alias: str = "", wait_for_status: str = None, channel="edge"
        ):
            if not alias:
                alias = name
            retcode, stdout, stderr = await ops_test._run(
                "juju",
                "deploy",
                "-m",
                ops_test.model_full_name,
                name,
                alias,
                f"--channel={channel}",
            )
            assert retcode == 0, f"Deploy failed: {(stderr or stdout).strip()}"
            log.info(stdout)
            await ops_test.model.wait_for_idle(
                apps=[alias], wait_for_status=wait_for_status, timeout=60
            )

        # deploy alertmanager from charmhub
        # self.am_app = await ops_test.model.deploy(
        #     'ch:alertmanager-k8s',
        #     application_name='am',
        #     channel='edge',
        # )
        # use CLI to deploy bundle until https://github.com/juju/python-libjuju/issues/511 is fixed.
        await cli_deploy_and_wait("alertmanager-k8s", "am")

        # due to a juju bug, occasionally alertmanager finishes a startup sequence with "waiting for IP address"
        # issuing a dummy config change just to trigger an event
        await ops_test.model.applications["am"].set_config({"pagerduty_key": "just_a_dummy"})
        await ops_test.model.wait_for_idle(apps=["am"], wait_for_status="active", timeout=60)
        assert ops_test.model.applications["am"].units[0].workload_status == "active"

        # deploy karma from charmhub
        # self.karma_app = await ops_test.model.deploy(
        #     'ch:karma-k8s',
        #     application_name='karma',
        #     channel='edge',
        # )
        await cli_deploy_and_wait("karma-k8s", "karma", "blocked")
        assert ops_test.model.applications["karma"].units[0].workload_status == "blocked"

    @pytest.mark.abort_on_fail
    async def test_config_proxy_with_alertmanager_ip(self, ops_test):
        # url = f"http://{ops_test.model.applications['am'].units[0].data['private-address']}:9093"
        status = await ops_test.model.get_status()
        url = f"http://{status['applications']['am']['units']['am/0']['address']}:9093"
        log.info("am public address: %s", url)

        # configure the proxy charm (the charm-under-test) with alertmanager's IP address
        await ops_test.model.applications["proxy"].set_config({"url": url})

        # after IP address is configured, the charm should be in "active" status
        await ops_test.model.wait_for_idle(apps=["proxy"], wait_for_status="active", timeout=60)
        assert ops_test.model.applications["proxy"].units[0].workload_status == "active"

    @pytest.mark.abort_on_fail
    async def test_relation_to_karma(self, ops_test):
        """Confirm alertmanager is reachable, after its IP address has been passed to the proxy charm"""
        await ops_test.model.add_relation("proxy", "karma")
        # at this point all three apps should be "active"
        # karma will become active only if alertmanager is reachable; otherwise it will immediately exit
        await ops_test.model.wait_for_idle(apps=["proxy", "am", "karma"], wait_for_status="active")
        assert ops_test.model.applications["karma"].units[0].workload_status == "active"

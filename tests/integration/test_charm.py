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
        charm_under_test = await ops_test.build_charm(".")
        resources = {"placeholder-image": "alpine"}
        self.proxy_app = await ops_test.model.deploy(
            charm_under_test,
            resources=resources,
            application_name="proxy")
        await ops_test.model.wait_for_idle(apps=["proxy"])
        assert ops_test.model.applications["proxy"].units[0].workload_status == "blocked"

        # also deploy alertmanager from charmhub
        # self.am_app = await ops_test.model.deploy(
        #     'ch:alertmanager-k8s',
        #     application_name='am',
        #     channel='edge',
        # )
        # use CLI to deploy bundle until https://github.com/juju/python-libjuju/issues/511 is fixed.
        retcode, stdout, stderr = await ops_test._run(
            "juju", "deploy", "-m", ops_test.model_full_name, "alertmanager-k8s", "am", "--channel=edge"
        )
        assert retcode == 0, f"Deploy failed: {(stderr or stdout).strip()}"
        log.info(stdout)
        await ops_test.model.wait_for_idle(apps=["am"], wait_for_status="active", timeout=60)
        assert ops_test.model.applications["am"].units[0].workload_status == "active"

        # also karma alertmanager from charmhub
        # self.karma_app = await ops_test.model.deploy(
        #     'ch:karma-k8s',
        #     application_name='karma',
        #     channel='edge',
        # )

        retcode, stdout, stderr = await ops_test._run(
            "juju", "deploy", "-m", ops_test.model_full_name, "karma-k8s", "karma", "--channel=edge"
        )
        assert retcode == 0, f"Deploy failed: {(stderr or stdout).strip()}"
        log.info(stdout)
        await ops_test.model.wait_for_idle(apps=["karma"], wait_for_status="blocked")
        assert ops_test.model.applications["karma"].units[0].workload_status == "blocked"

        # due to a juju bug, occasionally alertmanager finishes a startup sequence with "waiting for IP address"
        # issuing a dummy config change just to trigger an event
        await ops_test.model.applications["am"].set_config({"pagerduty_key": "just_a_dummy"})
        #await ops_test.model.wait_for_idle(apps=["am"], wait_for_active=True, timeout=60)

    @pytest.mark.skip(reason="one at a time please")
    @pytest.mark.abort_on_fail
    async def test_config_proxy_with_alertmanager_ip(self, ops_test):
        # TODO relate the apps, and verify relations are valid
        log.info("================================================")
        log.info("===== OMG I'M FINALLY HERE =====================")
        log.info("================================================")

        url = f"http://{ops_test.model.applications['am'].unit[0].public_address}:9093"
        log.info("am public address: %s", url)
        await self.proxy_app.set_config({"url": url})
        await ops_test.model.wait_for_idle(wait_for_status="active", timeout=60)
        assert self.proxy_app.units[0].workload_status == "active"

    @pytest.mark.skip(reason="one at a time please")
    @pytest.mark.abort_on_fail
    async def test_relations_to_karma(self, ops_test):
        await ops_test.model.add_relation("proxy", "karma")
        await ops_test.model.wait_for_idle()
        log.info(ops_test.model.relations)
        assert ops_test.model.applications["karma"].units[0].workload_status == "active"


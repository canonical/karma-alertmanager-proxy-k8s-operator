#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest

from ops.model import ActiveStatus, BlockedStatus
from ops.testing import Harness

from charm import AlertmanagerKarmaProxyCharm


class TestCharm(unittest.TestCase):
    def setUp(self):
        self.harness = Harness(AlertmanagerKarmaProxyCharm)
        self.addCleanup(self.harness.cleanup)

        self.harness.set_leader(True)
        self.harness.begin_with_initial_hooks()

    def test_unit_status_without_config(self):
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

    def test_unit_status_with_config(self):
        self.harness.update_config({"url": "http://1.2.3.4:5678"})
        self.assertIsInstance(self.harness.charm.unit.status, ActiveStatus)

    @unittest.skip("not yet implemented")
    def test_status_returns_to_blocked(self):
        self.harness.update_config({"url": "http://1.2.3.4:5678"})
        self.harness.update_config({"url": ""})
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

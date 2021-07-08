#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Proxy charm for providing alertmanager URI info to Karma."""

from charms.alertmanager_karma.v0.karma import KarmaConsumer
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus

import logging

logger = logging.getLogger(__name__)


class AlertmanagerKarmaProxyCharm(CharmBase):
    _relation_name = "karmamanagement"

    def __init__(self, *args):
        super().__init__(*args)
        self.karma_lib = KarmaConsumer(
            self,
            self._relation_name,
            consumes={"karma": ">=0.0.1"},  # TODO update karma version
        )

        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.karma_lib.on.karmamanagement_available, self._on_karma_changed)

    def _on_karma_changed(self, _):
        self._update_unit_status()

    def _update_unit_status(self):
        relation = self.model.get_relation(self._relation_name)

        if not self.karma_lib.config_valid:
            self.unit.status = BlockedStatus("Waiting for valid configuration")
            return

        if relation is None or len(relation.units) == 0:
            self.unit.status = BlockedStatus("Waiting for relation to Karma")
            return

        self.unit.status = ActiveStatus()

    def _on_start(self, _):
        self._update_unit_status()

    def _on_config_changed(self, _):
        if url := self.config.get("alertmanager_url"):
            config = {"name": self.app.name, "uri": url}
            self.karma_lib.store_config(config)

        logger.info("config_changed: alertmanager_url = %s", url)
        # self._update_unit_status()


if __name__ == "__main__":
    main(AlertmanagerKarmaProxyCharm, use_juju_for_storage=True)

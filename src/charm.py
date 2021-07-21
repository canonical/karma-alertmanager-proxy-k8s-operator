#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Proxy charm for providing alertmanager URL info to Karma."""

from charms.karma_k8s.v0.karma import KarmaConsumer
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus

import logging

logger = logging.getLogger(__name__)


class AlertmanagerKarmaProxyCharm(CharmBase):
    _relation_name = "karma-dashboard"
    _service_name = "karma"

    def __init__(self, *args):
        super().__init__(*args)

        self.karma_lib = KarmaConsumer(
            self,
            self._relation_name,
            consumes={self._service_name: ">=0.86"},
        )

        self.framework.observe(self.on.config_changed, self._on_config_changed)

    def _update_unit_status(self):
        if not self.karma_lib.config_valid:
            self.unit.status = BlockedStatus(
                "Waiting for 'juju config url=...' with alertmanager url"
            )
            return

        self.unit.status = ActiveStatus("Proxying {}".format(self.karma_lib.target))

    def _on_config_changed(self, _):
        if url := self.config.get("url"):
            logger.debug("url = %s", url)

            self.karma_lib.target = url

        self._update_unit_status()


if __name__ == "__main__":
    main(AlertmanagerKarmaProxyCharm, use_juju_for_storage=True)

#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Proxy charm for providing alertmanager URI info to Karma."""

import logging

from charms.alertmanager_karma.v0.karma import KarmaCharmEvents, KarmaProvides
from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus

logger = logging.getLogger(__name__)


class AlertmanagerKarmaProxyCharm(CharmBase):
    """Charm the service."""

    on = KarmaCharmEvents()
    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self._stored.set_default(related=False)
        # use 'uri' here to match the Karma config dict expectation
        self.karma = KarmaProvides(
            self, {"name": self.app.name, "uri": self.config["alertmanager_url"]}
        )
        self.framework.observe(self.on.karmamanagement_available, self._on_config_changed)

    def _on_config_changed(self, _):
        """Set the charm status."""

        if self._stored.related:
            self.unit.status = ActiveStatus()
        else:
            self.unit.status = BlockedStatus(message="Waiting for relation to Karma")


if __name__ == "__main__":
    main(AlertmanagerKarmaProxyCharm, use_juju_for_storage=True)

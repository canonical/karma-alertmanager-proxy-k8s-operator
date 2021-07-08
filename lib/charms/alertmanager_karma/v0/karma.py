# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.

"""
# Karma Library

This library provides the interface needed in order to provide Alertmanager URIs
and associated information to the Karma application.

To have your charm provide URIs to Karma, you need to declare the interface's use in
your charm's metadata.yaml file:

```yaml
provides:
  karmamanagement:
    interface: karma
```

A typical example of including this library might be

```
from charms.alertmanager_karma.v0.karma import KarmaProvides

# in your charm's `__init__` method:

```
self.karmamanagement = KarmaProvides(self, {"name": self.app.name,
                                            "uri": self.config["external_hostname"],
                                           })
```

In config-changed, you can:

```
self.karmamanagement.update_config(
    {"service-hostname": self.config["external_hostname"]}
    )
```
"""

import logging

import ops.charm
from ops.charm import RelationBrokenEvent
from ops.framework import EventBase, EventSource, ObjectEvents
from ops.model import BlockedStatus
from ops.relation import ConsumerBase, ProviderBase
from ops.framework import StoredState


# The unique Charmhub library identifier, never change it
LIBID = "abcdef1234"

# Increment this major API version when introducing breaking changes
LIBAPI = 0

# Increment this PATCH version before using `charmcraft publish-lib` or reset
# to 0 if you are raising the major API version
LIBPATCH = 2

logger = logging.getLogger(__name__)


REQUIRED_FIELDS = {
    "name",
    "uri",
}

OPTIONAL_FIELDS = {
    "proxy",
    "readonly",
    "headers",
    "tls",
}


# Define a custom event "KarmaRelationUpdatedEvent" to be emitted
# when relation change has completed successfully, and handled
# by charm authors.
# See "Notes on defining events" section in docs
# TODO move inside KarmaConsumer class?
class KarmaAvailableEvent(EventBase):
    def __init__(self, handle, data=None):
        super().__init__(handle)
        self.data = data

    def snapshot(self):
        """Save relation data."""
        return {"data": self.data}

    def restore(self, snapshot):
        """Restore relation data."""
        self.data = snapshot["data"]


class KarmaProxyEvents(ops.relation.ConsumerEvents):
    karmamanagement_available = EventSource(KarmaAvailableEvent)


class KarmaProvider(ProviderBase):
    _provider_relation_name = "karmamanagement"
    karmamanagement_available = EventSource(
        KarmaAvailableEvent
    )  # TODO why same name as in consumer

    def __init__(self, charm, service_name: str, version: str = None):
        super().__init__(charm, self._provider_relation_name, service_name, version)
        self.charm = charm
        self._service_name = service_name

        # Set default value for the public port
        # This is needed here to avoid accessing charm constructs directly
        self._port = 8080  # default value

        events = self.charm.on[self._provider_relation_name]

        # Observe the relation-changed hook event and bind
        # self.on_relation_changed() to handle the event.
        self.framework.observe(events.relation_changed, self._on_relation_changed)
        self.framework.observe(events.relation_broken, self._on_relation_broken)

    def _on_relation_changed(self, event):
        """Handle a change to the karma relation.

        Confirm we have the fields we expect to receive."""
        # `self.unit` isn't available here, so use `self.model.unit`.
        if not self.model.unit.is_leader():
            return

        karma_data = {
            field: event.relation.data[event.app].get(field)
            for field in REQUIRED_FIELDS | OPTIONAL_FIELDS
            if event.relation.data[event.app].get(field)
        }

        missing_fields = sorted(
            [field for field in REQUIRED_FIELDS if karma_data.get(field) is None]
        )

        if missing_fields:
            logger.error(
                "Missing required data fields for karma relation: {}".format(
                    ", ".join(missing_fields)
                )
            )
            self.model.unit.status = BlockedStatus(
                "Missing fields for karma: {}".format(", ".join(missing_fields))
            )

        self.charm._stored.servers[event.relation.id] = karma_data
        # Create an event that our charm can use to decide it's okay to
        # configure the karma.
        self.karmamanagement_available.emit()

    def _on_relation_broken(self, event: RelationBrokenEvent):
        """Remove the unit data from local state."""
        self.charm._stored.servers.pop(event.relation.id, None)


class KarmaConsumer(ConsumerBase):
    """Functionality for the 'requires' side of the 'karma' relation.

    Hook events observed:
      - relation-changed
    """
    on = KarmaProxyEvents()
    _stored = StoredState()

    def __init__(self, charm, relation_name: str, consumes: dict, multi: bool = False):
        super().__init__(charm, relation_name, consumes, multi)
        self.charm = charm
        self._consumer_relation_name = relation_name  # from consumer's metadata.yaml
        self._stored.set_default(config={})

        events = self.charm.on[self._consumer_relation_name]

        self.framework.observe(events.relation_changed, self._on_relation_changed)

    def _update_relation_data(self):
        if not self.model.unit.is_leader():
            return

        for relation in self.charm.model.relations[self._consumer_relation_name]:
            relation.data[self.charm.app].update(self._stored.config)
            logger.info("store_config: updated app bag: %s = %s", relation.name, relation.data[self.model.app])
            logger.info("store_config: updated app bag (refetched): %s",
                        self.model.get_relation(self._consumer_relation_name).data[self.model.app])

    def _on_relation_changed(self, event: ops.charm.RelationChangedEvent):
        if not self.model.unit.is_leader():
            return

        # update app data bag
        if event.relation:
            # event.relation.data[self.model.app].update(self._stored.config)
            self._update_relation_data()
            logger.info("updated app bag: %s", event.relation.data[self.model.app])
            logger.info("updated app bag (refetched): %s",
                        self.model.get_relation(self._consumer_relation_name).data[self.model.app])

        self.on.karmamanagement_available.emit()

    @property
    def config_valid(self):
        return all(key in self._stored.config for key in ("name", "uri"))

    def store_config(self, config):
        self._stored.config.update(config)
        logger.info("stored config: %s", self._stored.config)

        if self.config_valid:
            self.on.karmamanagement_available.emit()
            self._update_relation_data()

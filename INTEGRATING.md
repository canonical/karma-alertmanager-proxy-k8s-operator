## Integrating karma-alertmanager-proxy-operator
karma-alertmanager-proxy-operator integrates with any charm that supports the
`karma_dashboard` interface.

This charm is intended as a bridge between a juju-managed karma instance, and a
remote alertmanager instance. This is useful when karma and alertmanager cannot
be connected via a juju relation.

Alertmanager should already be reachable from within the juju model used for
deploying karma, e.g. by means of some ingress. You would then configure this
proxy charm to hold the url to the remote alertmanager

```shell
juju deploy karma-alertmanager-proxy-k8s proxy
juju config proxy url="http://some.url.somewhere:9093"
```

and relate to a karma instance, for example

```shell
juju relate karma proxy
```

Note that every alertmanager _unit_ requires a separate proxy _app_: a remote
cluster of three alertmanager units would require three proxy apps.

Version compatibility between the remote alertmanager and related applications
is not ensured by this charm.

See [karma-operator][Karma operator], which
provides further details on integration.


[Alertmanager operator]: https://charmhub.io/alertmanager-k8s
[Karma operator]: https://charmhub.io/karma-k8s/


# Karma Alertmanager Proxy (k8s)

[![CharmHub Badge](https://charmhub.io/karma-alertmanager-proxy-k8s/badge.svg)](https://charmhub.io/karma-alertmanager-proxy-k8s)
[![Release](https://github.com/canonical/karma-alertmanager-proxy-k8s-operator/actions/workflows/release.yaml/badge.svg)](https://github.com/canonical/karma-alertmanager-proxy-k8s-operator/actions/workflows/release.yaml)
[![Discourse Status](https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.charmhub.io&style=flat&label=CharmHub%20Discourse)](https://discourse.charmhub.io)

## Description

Proxy charm to provide the details of an [Alertmanager][Alertmanager operator]
server to [Karma][Karma operator]. This is a sidecar-only charm (no workload)
that is used to pass data to Karma over a relation.

## Usage
```shell
juju deploy karma-alertmanager-proxy-k8s
juju relate karma-alertmanager-proxy-k8s karma-k8s
```

### Configuration
```shell
juju config karma-alertmanager-proxy-k8s url="http://some.url.somewhere:9093"
```

Note that an instance of the proxy _app_ is needed for every alertmanager _unit_.
Therefore, if more than one alertmanager unit needs to be registered in karma,
multiple proxy apps should be used:

```shell
juju deploy karma-alertmanager-proxy-k8s proxy1
juju deploy karma-alertmanager-proxy-k8s proxy2

juju config proxy1 url="http://some.uri.somewhere:9093"
juju config proxy2 url="http://some.uri.somewhere.else:9093"
```

### Actions
None.

### Scale out usage
You may add additional units for high availability
```shell
juju add-unit karma-alertmanager-proxy-k8s
```

## Relations
Currently, supported relations are:
- `karma-dashboard`, which forwards the configured alertmanager unit data to karma,
  over the `karma_dashboard:` interface.
  Set up with: `juju relate karma-alertmanager-proxy-k8s karma-k8s`.


## OCI Images
This is a no-workload charm, but currently, due to juju limitations, an image must be provided nonetheless.
Either `alpine` or `busybox` are good choices for a small footprint, stand-in image.


[Karma operator]: https://charmhub.io/karma-k8s/
[gh:Alertmanager operator]: https://github.com/canonical/alertmanager-operator
[Alertmanager operator]: https://charmhub.io/alertmanager-k8s

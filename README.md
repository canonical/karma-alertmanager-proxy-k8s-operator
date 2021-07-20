# Karma Alertmanager Proxy (k8s)

## Description

Proxy charm to provide the details of an [Alertmanager](https://github.com/canonical/alertmanager-operator)
server to [Karma](https://github.com/canonical/karma-operator). This is a sidecar-only charm (no workload) that is used
to pass data to Karma over a relation.

## Usage
```shell
juju deploy karma-alertmanager-proxy-k8s --resource placeholder-image=alpine
juju relate karma-alertmanager-proxy-k8s karma-k8s
```

### Configuration
```shell
juju config karma-alertmanager-proxy-k8s url="http://some.uri.somewhere:9093"
```

Note that an instance of the proxy _app_ is needed for every alertmanager _unit_.
Therefore, if more than one alertmanager unit needs to be registered in karma, 
multiple proxy apps should be used:

```shell
juju deploy karma-alertmanager-proxy-k8s proxy1 --resource placeholder-image=alpine
juju deploy karma-alertmanager-proxy-k8s proxy2 --resource placeholder-image=alpine

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


## Developing

Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests

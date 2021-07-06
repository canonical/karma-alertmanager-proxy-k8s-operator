# alertmanager-karma-proxy (k8s)

## Description

Proxy charm to provide the details of an [Alertmanager](https://github.com/canonical/alertmanager-operator)
server to alertmanager-karma. This is a sidecar-only charm (no workload) that is used to pass data to karma
over a relation.

## Usage
```shell
juju deploy alertmanager-karma-proxy --resource placeholder-image=alpine
juju relate alertmanager-karma-proxy alertmanager-karma
```

### Configuration
```shell
juju config alertmanager-karma-proxy alertmanager_url="http://some.uri.somewhere"
```

Note that an instance of the proxy _app_ is needed for every alertmanager _unit_.
Therefore, if more than one alertmanager unit needs to be registered in karma, 
multiple proxy apps should be used:

```shell
juju deploy alertmanager-karma-proxy proxy1 --resource placeholder-image=alpine
juju deploy alertmanager-karma-proxy proxy2 --resource placeholder-image=alpine

juju config proxy1 alertmanager-uri="http://some.uri.somewhere"
juju config proxy2 alertmanager-uri="http://some.uri.somewhere.else"
```

### Actions
None.

### Scale out usage
You may add additional units for high availability
```shell
juju add-unit alertmanager-karma-proxy
```

## Relations
Currently, supported relations are:
- alertmanager-karma, which forwards the configured alertmanager unit data to karma, 
  over the `karmamanagement` interface.
  Set up with: `juju relate alertmanager-karma-proxy alertmanager-karma`.


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

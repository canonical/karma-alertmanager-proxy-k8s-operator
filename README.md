# alertmanager-karma-proxy

## Description

Proxy charm to provide the details of an Alertmanager server to
alertmanager-karma.

## Usage

```
juju deploy alertmanager-karma-proxy --resource placeholder-image=alpine
juju config alertmanager-karma-proxy alertmanager-uri="http://some.uri.somewhere"
juju relate alertmanager-karma-proxy alertmanager-karma
```

## Developing

Create and activate a virtualenv with the development requirements:

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements-dev.txt

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests

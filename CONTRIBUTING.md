# Contributing to alertmanager-karma-proxy-operator
The intended use case of this operator is to be deployed together with
[karma-operator][Karma operator].

## Bugs and pull requests
- Generally, before developing enhancements to this charm, you should consider
  opening an issue explaining your use case.
- If you would like to chat with us about your use-cases or proposed
  implementation, you can reach us at
  [Canonical Mattermost public channel](https://chat.charmhub.io/charmhub/channels/charm-dev)
  or [Discourse](https://discourse.charmhub.io/).
- All enhancements require review before being merged. Besides the
  code quality and test coverage, the review will also take into
  account the resulting user experience for Juju administrators using
  this charm.


## Setup

A typical setup using [snaps](https://snapcraft.io/) can be found in the
[Juju docs](https://juju.is/docs/sdk/dev-setup).

## Developing

Use your existing Python 3 development environment or create and
activate a Python 3 virtualenv

```shell
virtualenv -p python3 venv
source venv/bin/activate
```

Install the development requirements

```shell
pip install -r requirements.txt
```

Later on, upgrade packages as needed

```shell
pip install --upgrade -r requirements.txt
```

### Testing
All tests can be executed by running `tox` without arguments.

To run individual test environments,

```shell
tox -e prettify  # update your code according to linting rules
tox -e lint      # check your code complies to linting rules
tox -e static    # run static analysis
tox -e unit      # run unit tests
tox -e integration  # run inegration tests
```

#### Integration tests

The integration tests are based on a pytest plugin
([pytest-operator](https://github.com/charmed-kubernetes/pytest-operator))
for [python-libjuju](https://github.com/juju/python-libjuju).

To run the integration tests locally, first install dependencies:

```shell
sudo snap install charm --classic
```

Then you can run the integration tests

```shell
tox -e integration
```


## Build charm

Build the charm in this git repository using

```shell
charmcraft pack
```

## Usage

```shell
juju deploy ./alertmanager-karma-proxy-k8s.charm \
  --resource placeholder-image=alpine
juju config alertmanager-karma-proxy-k8s url="http://whatever:9093"
```

See [karma-operator][Karma operator] for details.

## Code overview
TODO

## Design choices
- Every alertmanager unit requires a proxy app. This allows to partially mimic
  a cross-model relation from the point of view of the karma operator.

## Roadmap
- Support [additional fields](https://github.com/prymitive/karma/blob/main/docs/CONFIGURATION.md#alertmanagers),
  such as cluster name.


[Karma operator]: https://charmhub.io/karma-k8s/
[gh:Karma operator]: https://github.com/canonical/karma-operator

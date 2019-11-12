# pyfarmsim
![GitHub](https://img.shields.io/github/license/moriglia/pyfarmsim)
## Requirements
`pipenv`, running on ![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/moriglia/pyfarmsim)

## Initialize
```bash
make [init]
```

## Testing

For all tests:
```bash
make test
```

For a specific test (e.g. `test/test_usage.py`) use one of the following
equivalent commands
```bash
pipenv run python3 -m unittest test/test_loadbalancer.py

# or enter the environment
pipenv shell
python3 -m unittest test/test_loadbalancer.py
exit

# or use make target
make test_loadbalancer
```

## Syntax check
```bash
make pylama [ F="test/test_loadbalancer.py pyfarmsim/loadbalancer.py" ]
```

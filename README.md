# py-farm-sim

## Requirements
`pipenv` and `python3.6`
## Initialize
```bash
make [init]
```

## Testing

For all tests:
```bash
make test
```

For a specific test (e.g. `test/test_usage.py`)
```bash
pipenv run python3 -m unittest test/test_usage.py
```
or alternatively
```bash
pipenv shell
python3 -m unittest test/test_usage.py
```

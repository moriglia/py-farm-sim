# pyfarmsim
![GitHub](https://img.shields.io/github/license/moriglia/pyfarmsim)
## Requirements
`pipenv`, running on ![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/moriglia/pyfarmsim)

## Initialize
```bash
make [init]
```
This will create a virtual environment using the `Pipfile`

## Testing

For all tests:
```bash
make test
# or
pipenv run python3 -m unittest discover -v
```
The latter is recommended because it will not perform the tests file per file,
but as a whole. The first form is for the lazy typer.

For a specific test (e.g. `test/test_04_server.py`) use one of the following
equivalent commands
```bash
pipenv run python3 -m unittest test/test_04_server.py

# or enter the environment
pipenv shell
python3 -m unittest test/test_loadbalancer.py
exit

# or use make target
make test_04_server
```

## Syntax check
```bash
make pylama [ F="test/test_04_server.py pyfarmsim/loadbalancer.py" ]
```
If the `F` parameter is not specified, all files in `pyfarmsim` and `test`
will be checked.

## Examples
Just run them like this:
```bash
python3 <example_file>.py
```
If a gnuplot file is associated with the example
(and you have gnuplot installed),
you can plot some statistics.
```bash
./<filename>.gnuplot
# or
gnuplot -p ./<filename>.gnuplot
```

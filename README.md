# Yanara

## dev

```bash
# install all needed dependencies
poetry install

# set up pre-commit hooks
poetry run pre-commit install
```

After setting up pre-commit hooks, we can then use the following command to do checks before committing code:
```bash
poetry run pre-commit run --all-files
```

Also, try to run tests and view coverage reports oftentimes (if you're a TDD fundamentalist):
```bash
poetry run pytest --maxfail=1 --disable-warnings --cov=. --cov-report=term-missing
```

## prod

```
poetry install --no-dev
```

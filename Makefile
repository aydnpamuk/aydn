.PHONY: fmt lint test

fmt:
    ruff --fix .

lint:
    ruff .

test:
    pytest -q

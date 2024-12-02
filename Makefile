
tests:
	pytest .

fast-tests:
	pytest . -m 'not slow'

format:
	pre-commit run -a

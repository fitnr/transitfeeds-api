# This file is part of transitfeeds-api.
# https://github.com/fitnr/transitfeeds-api

# test your application (tests in the tests/ directory)
test:
	python setup.py test

README.rst: README.md
	- pandoc $< -o $@
	@touch $@
	python setup.py check -r -s -m -q

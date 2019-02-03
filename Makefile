# This file is part of transitfeeds-api.
# https://github.com/fitnr/transitfeeds-api
.PHONY: test deploy

test:; python setup.py test

deploy: README.rst
	twine register
	git push
	git push --tags
	rm -rf dist build
	python3 setup.py bdist_wheel --universal
	twine upload dist/*

README.rst: README.md
	- pandoc $< -o $@
	@touch $@
	python setup.py check -r -s -m -q

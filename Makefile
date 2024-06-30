package = ${PWD##*/}  # basename of current directory
tests = tests
venv = venv_publish

test:
	python -m unittest -v $(tests)/test*.py
check:
	mypy src/$(package/*.py)
	ruff check src/*
test_publish:  # you should have proper pyproject.toml
	python -m $(venv) $(venv)
	. $(venv)/bin/activate
	pip install build twine
	python -m build
	cd dist
	unzip $(package) -d $(package)-whl
	tree $(package) 
	rm -rf $(package)-whl 
	cd ..
	twine check dist/*
	twine upload -r testpypi dist/* --verbose
	pip install $(package) 
	pip list
	deactivate
publish:
	python -m build
	twine upload dist/* --verbose
	make clean
clean:
	rm -rf __pycache__
	rm -rf src/$(package).egg-info
	rm -rf dist
clean_all:
	make clean
	rm -rf $(venv)

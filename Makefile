test_codemod:
	py.test

build:
	python setup.py sdist bdist_wheel

clean:
	rm -r build/ dist/

upload:
	twine upload dist/*

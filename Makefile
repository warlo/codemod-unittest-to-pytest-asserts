
test:
	python -m codemod_unittest_to_pytest_asserts.tests.test_codemod

build:
	python setup.py sdist bdist_wheel

clean:
	rm -r build/ dist/

upload:
	twine upload dist/*
import codemod
import shutil
import os

from ..codemod_unittest_to_pytest_asserts import *

UNITTEST_TEMPLATE = "./unittest_code_template.py"
UNITTEST_FILE = "unittest_code.py"
PYTEST_FILE = "./pytest_code.py"
DIRNAME = os.path.dirname(__file__)


def test():

    unittest_code = open(os.path.join(DIRNAME, UNITTEST_FILE)).read()

    codemod.Query(
        assert_patches,
        path_filter=lambda x: x
        == "./" + os.path.join(os.path.relpath(DIRNAME), UNITTEST_FILE),
    ).run_interactive()

    assert (
        open(os.path.join(DIRNAME, UNITTEST_FILE)).read()
        == open(os.path.join(DIRNAME, PYTEST_FILE)).read()
    )

    # Overwrite the unittest file from the template again to avoid git
    open(os.path.join(DIRNAME, UNITTEST_FILE), "w").write(unittest_code)


if __name__ == "__main__":
    test()

import codemod
import shutil
import os
import pathlib

from ..codemod_unittest_to_pytest_asserts import *

UNITTEST_TEMPLATE = "./unittest_code_template.py"
UNITTEST_FILE = "unittest_code.py"
PYTEST_FILE = "./pytest_code.py"
DIRNAME = pathlib.Path(__file__).parent


def test():

    unittest_code = (DIRNAME / UNITTEST_FILE).read_text()

    codemod.Query(
        assert_patches,
        path_filter=lambda x: x
        == "./" + str((pathlib.PurePath(DIRNAME).relative_to(pathlib.Path.cwd()) / UNITTEST_FILE)),
    ).run_interactive()

    assert (
        (DIRNAME / UNITTEST_FILE).read_text()
        == (DIRNAME / PYTEST_FILE).read_text()
    )
    assert (
        (DIRNAME / UNITTEST_FILE).read_text()
        != (DIRNAME / UNITTEST_TEMPLATE).read_text()
    )
    print("Tests passed!")

    # Overwrite the unittest file from the template again to avoid git
    open((DIRNAME / UNITTEST_FILE), "w").write(unittest_code)


if __name__ == "__main__":
    test()

import pathlib
import shutil

import codemod

from codemod_unittest_to_pytest_asserts import assert_patches, is_py

DIRNAME = pathlib.Path(__file__).parent

UNITTEST_FILE = DIRNAME / "unittest_code.py"
PYTEST_FILE = DIRNAME / "pytest_code.py"


def test_codemod(tmp_path):
    victim = tmp_path / "victim.py"
    shutil.copy(UNITTEST_FILE, victim)
    for patch in codemod.Query(
        assert_patches,
        root_directory=tmp_path,
        path_filter=is_py,
    ).generate_patches():
        lines = list(open(patch.path))
        patch.apply_to(lines)
        pathlib.Path(patch.path).write_text("".join(lines))

    assert victim.read_text() == (DIRNAME / PYTEST_FILE).read_text()

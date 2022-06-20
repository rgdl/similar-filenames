from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List
from typing import Set
from typing import Tuple

from similar_filenames import DEFAULT_MAX_RESULTS
from similar_filenames import find_all_files
from similar_filenames import parse_arguments


def test_default_argument_parsing():
    args_dict = parse_arguments([])
    expected = {
        "path": Path(),
        "n_results": DEFAULT_MAX_RESULTS,
        "max_depth": None,
    }
    assert args_dict == expected


def _setup_find_all_files(**kwargs) -> Tuple[Set[Path], Set[Path], List[Path]]:
    """
    Build temporary file tree, return dirs and files along with results of
    invoking `find_all_files` with `kwargs`
    """
    with TemporaryDirectory() as _td:
        td = Path(_td)
        dirs = ((td / "dir1"), (td / "dir2"), (td / "dir1/dir3"))
        for _dir in dirs:
            _dir.mkdir()
            assert _dir.exists()
        files = tuple((_dir / f"file{i+1}") for i, _dir in enumerate(dirs))
        for file in files:
            file.touch()
            assert file.exists()

        found_files = find_all_files(td, **kwargs)
        return (
            {_dir.relative_to(td) for _dir in dirs},
            {file.relative_to(td) for file in files},
            found_files,
        )


def test_find_files_but_not_directories():
    dirs, files, found_files = _setup_find_all_files()
    assert files == set(found_files)

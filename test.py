from pathlib import Path

from similar_filenames import DEFAULT_MAX_RESULTS
from similar_filenames import parse_arguments


def test_default_argument_parsing():
    args_dict = parse_arguments([])
    expected = {
        "path": Path(),
        "n_results": DEFAULT_MAX_RESULTS,
        "max_depth": None,
    }
    assert args_dict == expected

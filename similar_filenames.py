#!/usr/bin/env python

"""
Given a directory, return the most similar filenames.
Defaults to current directory.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import numpy as np
import pandas as pd  # type: ignore
import simhash  # type: ignore
from tqdm import tqdm  # type: ignore

DEFAULT_MAX_RESULTS = 1000
DEFAULT_IGNORE = (".DS_Store",)


def parse_arguments(args: List[str]) -> Dict[str, Any]:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "dir",
        nargs="?",
        default=Path(),
        help="directory to begin search from",
    )
    parser.add_argument(
        "--max-results",
        "-n",
        type=int,
        default=DEFAULT_MAX_RESULTS,
        help="maximum number of results to return",
    )
    parser.add_argument(
        "--max-depth",
        "-d",
        type=int,
        help=(
            "maximum number of subdirectories to traverse - no limit if "
            "unspecified"
        ),
    )

    parsed_args = parser.parse_args(args)

    return {
        "path": Path(parsed_args.dir),
        "n_results": parsed_args.max_results,
        "max_depth": parsed_args.max_depth,
    }


def count_bits(n: np.ndarray) -> np.ndarray:
    """
    Count the number of 1s in the binary representation of integers.

    Works on numpy arrays in a vectorised fashion.

    No idea how this works. Copied from here:
    https://stackoverflow.com/questions/9829578/
    """
    n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
    n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
    n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
    n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
    n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
    n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32)
    return n


def find_all_files(
    path: Path,
    max_depth: Optional[int] = None,
    ignore: Tuple[str] = DEFAULT_IGNORE,
) -> List[Path]:
    """
    Recursively find all files in `path`, provided their name is not listed in
    `ignore`. Don't look more than `max_depth` directories deep. If `max_depth`
    is None, search depth is unlimited.
    """
    all_files = []
    for fn in path.glob("**/*"):
        if fn.is_dir() or fn.name in ignore:
            continue
        fn = fn.relative_to(path)
        if max_depth is not None and len(fn.parts) - 1 > max_depth:
            continue
        all_files.append(fn)
    return all_files


def hash_distances(hash_1: List[int], hash_2: List[int]) -> List[int]:
    """
    Given two equal-length lists of hashes, count the number of bits that
    differ, element-wise.
    """
    assert len(hash_1) == len(hash_2)
    hash_diff = np.array(hash_1, dtype=np.uint64) ^ np.array(
        hash_2, dtype=np.uint64
    )
    return count_bits(hash_diff).tolist()


def build_results_dataframe(files: List[Path]) -> pd.DataFrame:
    """
    Build a dataframe containing all possible filename pairings and the
    distance measure corresponding to each
    """
    distinct_file_names = {file.name for file in files}
    hash_dict = {
        file_name: simhash.Simhash(file_name).value
        for file_name in distinct_file_names
    }

    file_1, file_2, hash_1, hash_2 = [], [], [], []

    for i, f1 in tqdm(list(enumerate(files))):
        for f2 in files[i + 1 :]:
            file_1.append(str(f1))
            file_2.append(str(f2))
            hash_1.append(hash_dict[f1.name])
            hash_2.append(hash_dict[f2.name])

    return (
        pd.DataFrame(
            {
                "file_1": file_1,
                "file_2": file_2,
                "distance": hash_distances(hash_1, hash_2),
            }
        )
        .sort_values("distance")
        .reset_index(drop=True)
    )


def main(path: Path, n_results: int, max_depth: Optional[int]) -> None:
    all_files = find_all_files(path, max_depth)
    results = build_results_dataframe(all_files).head(n_results)

    if results.empty:
        msg = f"No files found in '{path}'"
        if max_depth is not None:
            msg += f" at a search depth of {max_depth}"
        print(msg, file=sys.stderr)

    data = results.to_json(orient="records")
    print(json.dumps(json.loads(data), indent=4))


if __name__ == "__main__":
    args_dict = parse_arguments(sys.argv[1:])
    main(**args_dict)

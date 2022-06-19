#!/usr/bin/env python

"""
Given a directory, return the most similar filenames.
Defaults to current directory.
"""

import argparse
import sys
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

import numpy as np
import simhash  # type: ignore
from tqdm import tqdm  # type: ignore

DEFAULT_MAX_RESULTS = 1000


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
        "dir_path": Path(parsed_args.dir),
        "n_results": parsed_args.max_results,
        "max_depth": parsed_args.max_depth,
    }


def count_bits(n: np.ndarray) -> np.ndarray:
    """
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


def main(dir_path: Path, n_results: int, max_depth: int) -> None:
    all_fn = [
        fn
        for fn in dir_path.glob("**/*")
        if all(
            [
                not fn.is_dir(),
                len(fn.parts) <= max_depth,
                fn.name not in (".DS_Store",),
            ]
        )
    ]
    distinct_fn = set(fn.name for fn in all_fn)
    hash_dict = {str(fn): simhash.Simhash(fn).value for fn in distinct_fn}

    all_f1 = []
    all_f2 = []
    hash1 = []
    hash2 = []

    for i, f1 in tqdm(list(enumerate(all_fn)), desc="Hashing"):
        for f2 in all_fn[i + 1 :]:
            all_f1.append(f1)
            all_f2.append(f2)
            hash1.append(hash_dict[str(f1.name)])
            hash2.append(hash_dict[str(f2.name)])

    hash_diff = np.array(hash1, dtype=np.uint64) ^ np.array(
        hash2, dtype=np.uint64
    )
    hash_diff_count = count_bits(hash_diff)
    hash_diff_count_order = hash_diff_count.argsort()

    n_results = min(n_results, len(all_f1))

    if n_results:
        print()
        print(n_results, "most similar pairs of filenames:")

        for i in reversed(range(n_results)):
            ind = hash_diff_count_order[i]
            print("\n***\n")
            print(all_f1[ind])
            print(all_f2[ind])
            print()
            print(
                "# Similarity Hashes differ by", hash_diff_count[ind], "bits"
            )
        print()
    else:
        print()
        print("No files found")


if __name__ == "__main__":
    args_dict = parse_arguments(sys.argv[1:])
    main(**args_dict)

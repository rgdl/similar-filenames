# Command Line to Tool to find files with similar names

I wrote this to help me find duplicates in a huge PDF collection. All filenames are compared pairwise using the simhash algorithm: https://github.com/1e0ng/simhash. Similarity is measured with bitwise distance.

Outputs file paths and distance measures as JSON, sorted ascending by distance.

```
usage: similar_filenames.py [-h] [--max-results MAX_RESULTS] [--max-depth MAX_DEPTH] dir

Given a directory, return the most similar filenames.

positional arguments:
  dir                   directory to begin search from

optional arguments:
  -h, --help            show this help message and exit
  --max-results MAX_RESULTS, -n MAX_RESULTS
                        maximum number of results to return
  --max-depth MAX_DEPTH, -d MAX_DEPTH
                        maximum number of subdirectories to traverse - no limit if
                        unspecified
```

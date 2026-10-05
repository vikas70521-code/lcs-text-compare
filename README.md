# Text Comparison System using Longest Common Subsequence (LCS)

**Subject:** Design and Analysis of Algorithms (DAA)
**Topic:** A basic text comparison tool that finds the similarity between two documents using LCS.

## What it does
Give it two documents. It finds their Longest Common Subsequence (LCS), reports a
similarity score, and marks every word/line/character as **shared**, **removed** (only in A)
or **added** (only in B) - the same idea that powers `diff`, Git and plagiarism checkers.

```
Similarity = 2 x LCS length / (|A| + |B|)         (1.0 = identical, 0.0 = nothing in common)
```

## Project structure
```
lcs-text-compare/
|-- lcs.py             # all algorithms: naive, memoized, DP, 2-row, Hirschberg + diff builder
|-- app.py             # Flask web app (REST endpoint /api/compare)
|-- templates/index.html  # web UI (side-by-side, combined, DP table view)
|-- cli.py             # command line tool
|-- benchmark.py       # empirical time analysis -> benchmark.png
|-- tests/test_lcs.py  # 11 unit tests
|-- samples/           # two sample documents
|-- REPORT.md          # full project report (problem, design, analysis, results)
`-- requirements.txt
```

## Setup and run
```bash
pip install -r requirements.txt

# 1) Web app
python app.py                 # open http://127.0.0.1:5000  -> click "Load sample"

# 2) Command line
python cli.py samples/doc_a.txt samples/doc_b.txt
python cli.py a.txt b.txt --mode line         # word (default) | line | char

# 3) Tests and benchmark
python -m unittest discover -s tests -v
python benchmark.py
```

## Algorithms implemented (all in `lcs.py`)
| Function | Technique | Time | Space | Returns |
|---|---|---|---|---|
| `lcs_length_naive` | plain recursion | O(2^(m+n)) | O(m+n) | length |
| `lcs_length_memo` | top-down DP | O(mn) | O(mn) | length |
| `build_table` + `backtrack` | bottom-up DP | O(mn) | O(mn) | the LCS |
| `lcs_length_linear_space` | two-row DP | O(mn) | O(min(m,n)) | length |
| `lcs_hirschberg` | divide and conquer | O(mn) | O(min(m,n)) | the LCS |

Extra optimization: a common prefix/suffix is trimmed before DP (always safe for LCS).
In "auto" mode the app switches to Hirschberg when the table would exceed 2 million cells.

## Viva quick answers
* **Why DP?** LCS has *optimal substructure* and *overlapping subproblems*; naive recursion is exponential.
* **Why not just compare character by character?** That only finds differences at the same position; one inserted word would make everything after it "different". LCS handles insertions and deletions.
* **Is the LCS unique?** The length is unique, the subsequence itself may not be.
* **Subsequence vs substring?** A substring must be contiguous; a subsequence keeps order but can skip items.

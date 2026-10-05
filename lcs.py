"""
lcs.py - Core algorithms for the Text Comparison System
=======================================================
Subject : Design and Analysis of Algorithms (DAA)
Topic   : Text comparison using the Longest Common Subsequence (LCS)

This module contains
  1. Four classic LCS algorithms (naive recursion, memoization,
     bottom-up DP, linear-space DP) + Hirschberg's divide & conquer,
  2. A tokenizer (character / word / line level),
  3. A diff builder that turns LCS matches into equal / delete / insert runs,
  4. `compare()` - the single entry point used by the CLI and the web app.
"""

import re
import sys
import time
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

Pairs = List[Tuple[int, int]]          # matched index pairs (i in A, j in B)

# Switch from the full DP table to Hirschberg when the table would exceed this
# many cells (keeps memory low for very large documents).
TABLE_CELL_LIMIT = 2_000_000
# Show the full DP table in the UI only for tiny inputs.
TABLE_DISPLAY_LIMIT = 14


# ---------------------------------------------------------------------------
# 1. LCS ALGORITHMS
# ---------------------------------------------------------------------------

def lcs_length_naive(a, b) -> int:
    """Plain recursion straight from the recurrence.  Time O(2^(m+n)).
    Only usable for tiny inputs - it is here to *show* why DP is needed."""
    def rec(i: int, j: int) -> int:
        if i == 0 or j == 0:
            return 0
        if a[i - 1] == b[j - 1]:
            return 1 + rec(i - 1, j - 1)
        return max(rec(i - 1, j), rec(i, j - 1))
    return rec(len(a), len(b))


def lcs_length_memo(a, b) -> int:
    """Top-down DP (memoization).  Time O(m*n), space O(m*n) + recursion stack."""
    sys.setrecursionlimit(max(sys.getrecursionlimit(), len(a) + len(b) + 100))

    @lru_cache(maxsize=None)
    def rec(i: int, j: int) -> int:
        if i == 0 or j == 0:
            return 0
        if a[i - 1] == b[j - 1]:
            return 1 + rec(i - 1, j - 1)
        return max(rec(i - 1, j), rec(i, j - 1))

    result = rec(len(a), len(b))
    rec.cache_clear()
    return result


def build_table(a, b) -> List[List[int]]:
    """Bottom-up DP.  table[i][j] = LCS length of a[:i] and b[:j].

        table[i][j] = 0                                  if i == 0 or j == 0
                    = table[i-1][j-1] + 1                if a[i-1] == b[j-1]
                    = max(table[i-1][j], table[i][j-1])  otherwise

    Time O(m*n), space O(m*n)."""
    m, n = len(a), len(b)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        row, prev, ai = table[i], table[i - 1], a[i - 1]
        for j in range(1, n + 1):
            if ai == b[j - 1]:
                row[j] = prev[j - 1] + 1
            else:
                row[j] = prev[j] if prev[j] >= row[j - 1] else row[j - 1]
    return table


def backtrack(table: List[List[int]], a, b) -> Pairs:
    """Walk the DP table from the bottom-right corner to recover one LCS.
    Time O(m+n)."""
    i, j = len(a), len(b)
    pairs: Pairs = []
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif table[i - 1][j] >= table[i][j - 1]:
            i -= 1
        else:
            j -= 1
    pairs.reverse()
    return pairs


def lcs_length_linear_space(a, b) -> int:
    """Length only, using two rows.  Time O(m*n), space O(min(m,n))."""
    if len(b) > len(a):
        a, b = b, a                      # keep the rows as short as possible
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            cur[j] = prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]


def _last_row(a, b) -> List[int]:
    """Last row of the DP table of (a, b), computed in O(len(b)) space."""
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0] * (len(b) + 1)
        for j, y in enumerate(b, 1):
            cur[j] = prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1])
        prev = cur
    return prev


def lcs_hirschberg(a, b) -> Pairs:
    """Hirschberg's algorithm: recovers the LCS itself in O(min(m,n)) extra
    space by divide & conquer.  Time stays O(m*n).

    Idea: split A in the middle, find the column k in B where the best LCS
    "crosses" the middle (forward row + backward row), then recurse on the
    two halves."""
    pairs: Pairs = []

    def solve(alo: int, ahi: int, blo: int, bhi: int) -> None:
        if alo >= ahi or blo >= bhi:
            return
        if ahi - alo == 1:                       # base case: one item of A
            for j in range(blo, bhi):
                if b[j] == a[alo]:
                    pairs.append((alo, j))
                    return
            return
        mid = (alo + ahi) // 2
        left = _last_row(a[alo:mid], b[blo:bhi])
        right = _last_row(a[mid:ahi][::-1], b[blo:bhi][::-1])
        width = bhi - blo
        best, split = -1, 0
        for k in range(width + 1):
            score = left[k] + right[width - k]
            if score > best:
                best, split = score, k
        solve(alo, mid, blo, blo + split)
        solve(mid, ahi, blo + split, bhi)

    solve(0, len(a), 0, len(b))
    return pairs


def lcs_pairs(a, b, algorithm: str = "auto") -> Tuple[Pairs, str, Optional[list]]:
    """Return (matched index pairs, algorithm used, DP table or None).

    Optimization: a common prefix and suffix always belong to some LCS, so
    they are stripped first and only the differing middle goes through DP."""
    pre = 0
    while pre < len(a) and pre < len(b) and a[pre] == b[pre]:
        pre += 1
    suf = 0
    while (suf < len(a) - pre and suf < len(b) - pre
           and a[len(a) - 1 - suf] == b[len(b) - 1 - suf]):
        suf += 1

    mid_a, mid_b = a[pre:len(a) - suf], b[pre:len(b) - suf]

    if algorithm == "auto":
        algorithm = "dp" if len(mid_a) * len(mid_b) <= TABLE_CELL_LIMIT else "hirschberg"

    table = None
    if not mid_a or not mid_b:
        core: Pairs = []
    elif algorithm == "hirschberg":
        core = lcs_hirschberg(mid_a, mid_b)
    else:
        algorithm = "dp"
        table = build_table(mid_a, mid_b)
        core = backtrack(table, mid_a, mid_b)

    pairs = [(k, k) for k in range(pre)]
    pairs += [(i + pre, j + pre) for i, j in core]
    pairs += [(len(a) - suf + k, len(b) - suf + k) for k in range(suf)]
    return pairs, algorithm, (table if pre == 0 and suf == 0 else None)


# ---------------------------------------------------------------------------
# 2. TOKENIZER
# ---------------------------------------------------------------------------

def tokenize(text: str, mode: str) -> List[str]:
    """Split text into tokens at the chosen granularity."""
    if mode == "char":
        return list(text)
    if mode == "line":
        return text.splitlines()
    return text.split()                  # "word" (default)


def normalize(token: str, mode: str, ignore_case: bool, ignore_punct: bool) -> str:
    """Comparison key for a token.  The original token is kept for display."""
    key = token
    if ignore_case:
        key = key.lower()
    if mode == "word" and ignore_punct:
        key = re.sub(r"[^\w]", "", key) or key
    if mode == "line":
        key = " ".join(key.split())       # collapse whitespace inside a line
    return key


SEPARATORS = {"char": "", "word": " ", "line": "\n"}


# ---------------------------------------------------------------------------
# 3. DIFF BUILDER
# ---------------------------------------------------------------------------

def build_ops(tokens_a: List[str], tokens_b: List[str], pairs: Pairs) -> List[Tuple[str, str]]:
    """Convert LCS matches to an edit script of ('equal'|'delete'|'insert', token).
      equal  -> token is in the LCS (common to both documents)
      delete -> token only exists in A
      insert -> token only exists in B"""
    ops: List[Tuple[str, str]] = []
    i = j = 0
    for pi, pj in pairs:
        while i < pi:
            ops.append(("delete", tokens_a[i])); i += 1
        while j < pj:
            ops.append(("insert", tokens_b[j])); j += 1
        ops.append(("equal", tokens_b[pj]))
        i, j = pi + 1, pj + 1
    while i < len(tokens_a):
        ops.append(("delete", tokens_a[i])); i += 1
    while j < len(tokens_b):
        ops.append(("insert", tokens_b[j])); j += 1
    return ops


def group_runs(ops: List[Tuple[str, str]], sep: str) -> List[Dict[str, str]]:
    """Merge consecutive ops of the same type into one run (nicer to display)."""
    runs: List[Dict[str, object]] = []
    for kind, token in ops:
        if runs and runs[-1]["type"] == kind:
            runs[-1]["tokens"].append(token)
        else:
            runs.append({"type": kind, "tokens": [token]})
    return [{"type": r["type"], "text": sep.join(r["tokens"])} for r in runs]


# ---------------------------------------------------------------------------
# 4. PUBLIC API
# ---------------------------------------------------------------------------

def compare(text_a: str, text_b: str, mode: str = "word", ignore_case: bool = True,
            ignore_punct: bool = True, algorithm: str = "auto") -> Dict:
    """Compare two documents and return a JSON-friendly result dictionary."""
    if mode not in SEPARATORS:
        raise ValueError("mode must be 'char', 'word' or 'line'")

    raw_a, raw_b = tokenize(text_a, mode), tokenize(text_b, mode)
    key_a = [normalize(t, mode, ignore_case, ignore_punct) for t in raw_a]
    key_b = [normalize(t, mode, ignore_case, ignore_punct) for t in raw_b]
    m, n = len(key_a), len(key_b)

    start = time.perf_counter()
    pairs, used, table = lcs_pairs(key_a, key_b, algorithm)
    elapsed_ms = (time.perf_counter() - start) * 1000

    ops = build_ops(raw_a, raw_b, pairs)
    sep = SEPARATORS[mode]
    lcs_len = len(pairs)

    result = {
        "mode": mode,
        "len_a": m,
        "len_b": n,
        "lcs_length": lcs_len,
        # Dice-style score: 1.0 = identical, 0.0 = nothing in common
        "similarity": round(2 * lcs_len / (m + n), 4) if (m + n) else 1.0,
        "coverage_a": round(lcs_len / m, 4) if m else 1.0,   # how much of A survives in B
        "coverage_b": round(lcs_len / n, 4) if n else 1.0,   # how much of B comes from A
        "algorithm": used,
        "time_ms": round(elapsed_ms, 3),
        "cells": m * n,
        "separator": sep,
        "runs": group_runs(ops, sep),
        "lcs_tokens": [raw_b[j] for _, j in pairs][:300],
        "table": None,
    }

    # For tiny inputs, expose the DP table so it can be drawn (great for demos).
    if m <= TABLE_DISPLAY_LIMIT and n <= TABLE_DISPLAY_LIMIT and m and n:
        full = build_table(key_a, key_b)
        result["table"] = {"rows": full, "a": raw_a, "b": raw_b,
                           "path": [[i + 1, j + 1] for i, j in pairs]}
    return result

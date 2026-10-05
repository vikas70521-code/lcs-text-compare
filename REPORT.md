# Text Comparison System using Longest Common Subsequence

**Subject:** Design and Analysis of Algorithms
**Student:** G. Vikas Kumar, B.Tech CSE (AI/ML), Sandip University, Nashik

---

## 1. Abstract
This project builds a text comparison tool that measures how similar two documents are and
shows exactly what was kept, removed and added. The core is the **Longest Common Subsequence (LCS)**
problem, solved with dynamic programming. Five LCS algorithms are implemented and compared, from
exponential recursion to Hirschberg's linear-space divide and conquer. The tool is available as a
web app (Flask) and a command line program.

## 2. Problem statement
Given two documents A and B, each a sequence of tokens (characters, words or lines), find the longest
sequence of tokens that appears in both documents **in the same order** (not necessarily contiguously).
Use it to compute a similarity score and an edit script (what to delete from A and insert to get B).

Formally, for A = a1..am and B = b1..bn, find the longest sequence of index pairs
(i1,j1) < (i2,j2) < ... < (ik,jk) with a[it] = b[jt]. k is the LCS length.

## 3. Objectives
1. Implement LCS using dynamic programming and analyse its time and space complexity.
2. Show experimentally why DP is needed (naive vs DP).
3. Build a usable tool: similarity percentage, highlighted differences, file input.
4. Reduce memory usage with a space-optimised algorithm (Hirschberg).

## 4. Why LCS for text comparison
A position-by-position comparison breaks as soon as one word is inserted: every later word looks
"different". LCS aligns the documents by finding the biggest common skeleton, so insertions and deletions
are detected correctly. The same idea is used in `diff`, Git, plagiarism detection and DNA sequence alignment.

## 5. Algorithm design

### 5.1 Optimal substructure
Let L(i,j) be the LCS length of the prefixes A[1..i] and B[1..j].

* If a[i] = b[j], that last item can always be part of an LCS, so L(i,j) = L(i-1,j-1) + 1.
* Otherwise a[i] and b[j] cannot both be the last matched pair, so L(i,j) = max(L(i-1,j), L(i,j-1)).

### 5.2 Recurrence
```
L(i,j) = 0                           if i = 0 or j = 0
L(i,j) = L(i-1,j-1) + 1              if a[i] = b[j]
L(i,j) = max(L(i-1,j), L(i,j-1))     if a[i] != b[j]
```
The answer is L(m,n).

### 5.3 Overlapping subproblems
The same L(i,j) is requested by many different paths of the recursion tree. Without storing results the
recursion makes up to C(m+n, m) calls (exponential). Only (m+1)(n+1) distinct subproblems exist, so storing
them gives polynomial time.

### 5.4 Pseudocode (bottom-up)
```
LCS-LENGTH(A, B):
    for i = 0..m: L[i][0] = 0
    for j = 0..n: L[0][j] = 0
    for i = 1..m:
        for j = 1..n:
            if A[i] == B[j]:      L[i][j] = L[i-1][j-1] + 1
            else:                 L[i][j] = max(L[i-1][j], L[i][j-1])
    return L

BACKTRACK(L, A, B):
    i = m, j = n, result = []
    while i > 0 and j > 0:
        if A[i] == B[j]:          prepend A[i]; i--; j--
        else if L[i-1][j] >= L[i][j-1]:   i--
        else:                             j--
    return result
```

### 5.5 Worked example
A = `ABCBDAB`, B = `BDCABA` (the classic textbook pair). Rows are A, columns are B.

|   | ∅ | B | D | C | A | B | A |
|---|---|---|---|---|---|---|---|
| ∅ | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| A | 0 | 0 | 0 | 0 | 1 | 1 | 1 |
| B | 0 | 1 | 1 | 1 | 1 | 2 | 2 |
| C | 0 | 1 | 1 | 2 | 2 | 2 | 2 |
| B | 0 | 1 | 1 | 2 | 2 | 3 | 3 |
| D | 0 | 1 | 2 | 2 | 2 | 3 | 3 |
| A | 0 | 1 | 2 | 2 | 3 | 3 | 4 |
| B | 0 | 1 | 2 | 2 | 3 | 4 | 4 |

L(7,6) = 4. Backtracking from the bottom-right corner gives the LCS **BCBA** (length 4).

### 5.6 From LCS to a diff
Every token in the LCS is **shared**. A token of A not in the LCS is **removed**; a token of B not in the
LCS is **added**. The similarity score is

```
similarity = 2 x LCS / (|A| + |B|)        0 <= similarity <= 1
```
which is 1 for identical documents and 0 when nothing is shared.

### 5.7 Space optimisations
* **Two-row DP:** L(i,j) only needs row i-1 and row i, so the length can be found in O(min(m,n)) space.
  Backtracking needs the whole table, so this variant returns only the length.
* **Hirschberg's algorithm (divide and conquer):** split A at its middle, compute the forward LCS row of the
  top half and the backward LCS row of the bottom half (both in linear space), pick the column k of B where
  their sum is largest, and recurse on the two sub-problems. It recovers the actual LCS in O(min(m,n)) space
  with the same O(mn) time (the work per level halves, giving mn + mn/2 + mn/4 + ... <= 2mn).
* **Prefix/suffix trimming:** equal items at the start and end of both documents always belong to some LCS,
  so they are removed before DP. Real document versions usually differ in the middle only, so this is a large saving.

## 6. Complexity analysis

| Algorithm | Time | Space | Notes |
|---|---|---|---|
| Naive recursion | O(2^(m+n)) worst case | O(m+n) stack | unusable beyond ~15 items |
| Memoization (top-down) | O(mn) | O(mn) + recursion stack | recursion depth m+n |
| Bottom-up DP + backtrack | O(mn) | O(mn) | simplest way to get the LCS itself |
| Two-row DP | O(mn) | O(min(m,n)) | length only |
| Hirschberg | O(mn) | O(min(m,n)) | LCS itself in linear space |

* **Time of DP:** two nested loops of m and n iterations with O(1) work each, so Theta(mn). Backtracking adds O(m+n).
* **Space of DP:** the (m+1) x (n+1) table, so Theta(mn). For two documents of 5,000 words that is 25 million cells,
  which is why the tool switches to Hirschberg for large inputs.

### Correctness argument (sketch)
*Claim:* L(i,j) equals the LCS length of A[1..i] and B[1..j]. *Proof by induction on i+j.*
Base: if i = 0 or j = 0 one prefix is empty, so the LCS is empty and L = 0.
Step: take an optimal LCS Z of the two prefixes. If a[i] = b[j], then Z must end with that item (otherwise Z could be
extended, contradicting optimality) and removing it leaves an LCS of A[1..i-1], B[1..j-1], so L = L(i-1,j-1) + 1.
If a[i] != b[j], Z cannot end with both, so Z is an LCS of (A[1..i-1], B[1..j]) or of (A[1..i], B[1..j-1]); taking
the larger of the two is exactly the recurrence. By induction every table entry is correct. Backtracking follows the
same decisions in reverse, so it returns a common subsequence whose length is L(m,n). ∎

## 7. System design

```
 Browser / CLI  --->  Flask (/api/compare)  --->  lcs.compare()
                                                    |-- tokenize (char | word | line) + normalise
                                                    |-- lcs_pairs  (trim -> DP table or Hirschberg)
                                                    |-- build_ops  (equal / delete / insert)
                                                    `-- similarity, coverage, timing, DP table
```

| Module | Responsibility |
|---|---|
| `lcs.py` | algorithms, tokenizer, diff builder, `compare()` |
| `app.py` | validation, size limits (6,000 tokens per document), JSON API |
| `templates/index.html` | inputs, options, side-by-side view, combined view, DP table view |
| `cli.py` | terminal output with colours |
| `benchmark.py` | timing experiments and graph |

**Options:** compare by words / lines / characters; ignore capitals; ignore punctuation; choose DP or Hirschberg.
**Safety:** the browser builds the highlighted text with `textContent`, so pasted text can never inject HTML.

## 8. Testing
11 unit tests (`python -m unittest discover -s tests -v`) cover:
* the textbook example (length 4) on all four length algorithms,
* edge cases: empty strings, identical strings, disjoint strings,
* 200 random cases where naive, memoized, DP, two-row and Hirschberg must agree,
* 200 random cases where the reconstructed subsequence must be a valid common subsequence (indices strictly
  increasing, items equal) and DP and Hirschberg must give the same length,
* the edit script must rebuild both original documents exactly,
* similarity for identical, disjoint and empty inputs, all three modes, and a 1,800-word Hirschberg run.

All tests pass.

## 9. Results

### 9.1 Sample documents (`samples/doc_a.txt`, `samples/doc_b.txt`)
68 words vs 71 words, LCS length 60, **similarity 86.3%** (88.2% of A is kept in B, 84.5% of B comes from A).
The tool found the edits "for solving" -> "used to solve", "efficient" -> "fast", "storing" -> "saving", the inserted
words "given" and "widely", and the replaced phrases "file comparison tools" -> "plagiarism detection" and
"bioinformatics" -> "DNA analysis".

### 9.2 Experiment 1: naive recursion vs DP (random strings, time in ms)
| n | naive | DP |
|---|---|---|
| 8 | 0.44 | 0.007 |
| 10 | 2.38 | 0.010 |
| 12 | 12.67 | 0.014 |
| 13 | 101.89 | 0.015 |

Naive time grows several times for every extra character, DP grows only slightly: this is the exponential
versus polynomial gap, and it justifies dynamic programming.

### 9.3 Experiment 2: polynomial algorithms (random strings, time in ms)
| n | memoized | DP + path | two-row | Hirschberg |
|---|---|---|---|---|
| 100 | 8.1 | 1.3 | 1.9 | 4.3 |
| 200 | 27.9 | 4.3 | 7.4 | 16.0 |
| 400 | 108.1 | 16.0 | 28.0 | 61.1 |
| 800 | - | 75.5 | 114.8 | 229.6 |
| 1200 | - | 188.6 | 330.7 | 473.3 |

Doubling n multiplied DP time by about 3.3x, 3.7x and 4.7x, in line with the theoretical 4x of Theta(n^2).
Hirschberg is roughly 2 to 3 times slower than the table-based DP (it computes each cell about twice) but needs
only linear memory. Times depend on the machine; the growth pattern is what matters. The graph is in `benchmark.png`
(run `python benchmark.py` to regenerate on your computer).

## 10. Limitations
* Exact-match only: "quick" and "fast" are different tokens, so synonyms and paraphrases count as differences.
* Quadratic time: very large documents (tens of thousands of words) are slow in pure Python; the web app caps
  each document at 6,000 tokens.
* A document pair can have several different LCSs of the same length; the tool reports one of them.
* Sentence reordering lowers the score, because LCS respects order.

## 11. Future scope
Sentence-level and paragraph-level comparison, Myers' O(ND) diff algorithm for near-identical files, synonym-aware
matching using word embeddings, PDF and DOCX input, and multi-document plagiarism ranking.

## 12. Conclusion
LCS turns the vague question "how similar are these documents?" into a precise, solvable problem. Dynamic
programming reduces it from exponential to Theta(mn) time, and Hirschberg's algorithm shows that the memory cost
can be cut to linear without changing the running time. The final tool gives a similarity percentage and a clear
word-level diff, and the experiments match the theoretical analysis.

## 13. References
1. T. H. Cormen, C. E. Leiserson, R. L. Rivest, C. Stein - *Introduction to Algorithms*, chapter on Dynamic Programming (Longest common subsequence).
2. D. S. Hirschberg - "A linear space algorithm for computing maximal common subsequences", *Communications of the ACM*, 18(6), 1975.
3. E. W. Myers - "An O(ND) difference algorithm and its variations", *Algorithmica*, 1(1-4), 1986.
4. J. W. Hunt and M. D. McIlroy - "An algorithm for differential file comparison", Bell Labs, 1976.

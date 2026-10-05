"""Unit tests - run with:  python -m unittest discover -s tests -v"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lcs import (backtrack, build_ops, build_table, compare, lcs_hirschberg,
                 lcs_length_linear_space, lcs_length_memo, lcs_length_naive,
                 lcs_pairs)


def is_common_subsequence(a, b, pairs):
    """pairs must be strictly increasing in both strings and match equal items."""
    return (all(a[i] == b[j] for i, j in pairs)
            and all(p[0] < q[0] and p[1] < q[1] for p, q in zip(pairs, pairs[1:])))


class TestLCSLength(unittest.TestCase):
    def test_textbook_example(self):
        # CLRS example: LCS("ABCBDAB", "BDCABA") has length 4
        a, b = "ABCBDAB", "BDCABA"
        self.assertEqual(lcs_length_naive(a, b), 4)
        self.assertEqual(lcs_length_memo(a, b), 4)
        self.assertEqual(build_table(a, b)[-1][-1], 4)
        self.assertEqual(lcs_length_linear_space(a, b), 4)

    def test_edge_cases(self):
        self.assertEqual(build_table("", "abc")[-1][-1], 0)
        self.assertEqual(build_table("abc", "")[-1][-1], 0)
        self.assertEqual(build_table("abc", "abc")[-1][-1], 3)
        self.assertEqual(build_table("abc", "xyz")[-1][-1], 0)

    def test_all_algorithms_agree_on_random_input(self):
        random.seed(7)
        for _ in range(200):
            a = "".join(random.choice("ACGT") for _ in range(random.randint(0, 9)))
            b = "".join(random.choice("ACGT") for _ in range(random.randint(0, 9)))
            expected = lcs_length_naive(a, b)
            self.assertEqual(lcs_length_memo(a, b), expected)
            self.assertEqual(build_table(a, b)[-1][-1], expected)
            self.assertEqual(lcs_length_linear_space(a, b), expected)
            self.assertEqual(len(lcs_hirschberg(a, b)), expected)


class TestReconstruction(unittest.TestCase):
    def test_backtrack_and_hirschberg_return_valid_lcs(self):
        random.seed(11)
        for _ in range(200):
            a = [random.choice("abcd") for _ in range(random.randint(0, 25))]
            b = [random.choice("abcd") for _ in range(random.randint(0, 25))]
            via_table = backtrack(build_table(a, b), a, b)
            via_hirsch = lcs_hirschberg(a, b)
            self.assertTrue(is_common_subsequence(a, b, via_table))
            self.assertTrue(is_common_subsequence(a, b, via_hirsch))
            self.assertEqual(len(via_table), len(via_hirsch))

    def test_prefix_suffix_trimming_keeps_result_correct(self):
        a, b = list("HELLO_WORLD"), list("HELLO_BRAVE_WORLD")
        for algo in ("dp", "hirschberg", "auto"):
            pairs, _, _ = lcs_pairs(a, b, algo)
            self.assertTrue(is_common_subsequence(a, b, pairs))
            self.assertEqual(len(pairs), len(a))      # all of A survives in B


class TestDiff(unittest.TestCase):
    def test_edit_script_rebuilds_both_documents(self):
        a = "the quick brown fox jumps over the lazy dog".split()
        b = "the quick red fox leaps over the very lazy dog".split()
        pairs, _, _ = lcs_pairs(a, b)
        ops = build_ops(a, b, pairs)
        self.assertEqual([t for k, t in ops if k in ("equal", "delete")], a)
        self.assertEqual([t for k, t in ops if k in ("equal", "insert")], b)


class TestCompare(unittest.TestCase):
    def test_identical_documents(self):
        r = compare("same text here", "Same text, here!")     # case + punctuation ignored
        self.assertEqual(r["similarity"], 1.0)

    def test_disjoint_documents(self):
        r = compare("alpha beta", "gamma delta")
        self.assertEqual(r["lcs_length"], 0)
        self.assertEqual(r["similarity"], 0.0)

    def test_empty_documents(self):
        self.assertEqual(compare("", "")["similarity"], 1.0)
        self.assertEqual(compare("", "word")["similarity"], 0.0)

    def test_modes(self):
        self.assertEqual(compare("abcd", "abxd", mode="char")["lcs_length"], 3)
        self.assertEqual(compare("l1\nl2\nl3", "l1\nl3", mode="line")["lcs_length"], 2)

    def test_large_input_uses_hirschberg_and_stays_correct(self):
        random.seed(3)
        words = ["w%d" % random.randint(0, 40) for _ in range(1800)]
        other = [w for w in words if random.random() > 0.2]
        r = compare(" ".join(words), " ".join(other), algorithm="hirschberg")
        self.assertEqual(r["lcs_length"], len(other))       # `other` is a subsequence of `words`


if __name__ == "__main__":
    unittest.main()

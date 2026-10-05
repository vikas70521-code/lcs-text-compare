"""
benchmark.py - empirical analysis of the LCS algorithms.

Produces a results table in the terminal and saves 'benchmark.png'.
    python benchmark.py
"""
import random
import time

import matplotlib
matplotlib.use("Agg")                       # no display needed
import matplotlib.pyplot as plt

from lcs import (backtrack, build_table, lcs_hirschberg, lcs_length_linear_space,
                 lcs_length_memo, lcs_length_naive)

random.seed(42)
ALPHABET = "ABCD"


def rand_string(n: int) -> str:
    return "".join(random.choice(ALPHABET) for _ in range(n))


def timeit(fn, *args, repeats: int = 3) -> float:
    """Best-of-N wall time in milliseconds."""
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        fn(*args)
        best = min(best, time.perf_counter() - start)
    return best * 1000


def dp_with_backtrack(a, b):
    return backtrack(build_table(a, b), a, b)


def main() -> None:
    # ---- Experiment 1: naive recursion vs dynamic programming (tiny n) ----
    small = [4, 6, 8, 10, 12, 13]
    naive, dp_small = [], []
    print("\nExperiment 1 - why DP?  (time in ms, n = |A| = |B|)")
    print(f"{'n':>4} {'naive O(2^n)':>14} {'bottom-up DP':>14}")
    for n in small:
        a, b = rand_string(n), rand_string(n)
        naive.append(timeit(lcs_length_naive, a, b, repeats=1))
        dp_small.append(timeit(build_table, a, b))
        print(f"{n:>4} {naive[-1]:>14.3f} {dp_small[-1]:>14.4f}")

    # ---- Experiment 2: polynomial algorithms on larger inputs -------------
    sizes = [100, 200, 400, 800, 1200]
    memo, dp, linear, hirsch = [], [], [], []
    print("\nExperiment 2 - O(m*n) algorithms  (time in ms)")
    print(f"{'n':>5} {'memoized':>10} {'DP+path':>10} {'2-row':>10} {'Hirschberg':>11}")
    for n in sizes:
        a, b = rand_string(n), rand_string(n)
        memo.append(timeit(lcs_length_memo, a, b, repeats=1) if n <= 400 else None)
        dp.append(timeit(dp_with_backtrack, a, b, repeats=1))
        linear.append(timeit(lcs_length_linear_space, a, b, repeats=1))
        hirsch.append(timeit(lcs_hirschberg, a, b, repeats=1))
        m_txt = f"{memo[-1]:.1f}" if memo[-1] is not None else "-"
        print(f"{n:>5} {m_txt:>10} {dp[-1]:>10.1f} {linear[-1]:>10.1f} {hirsch[-1]:>11.1f}")

    # growth ratio: doubling n should roughly quadruple the time for O(n^2)
    print("\nGrowth when n doubles (expect ~4x for O(n^2)):")
    for k in range(1, 4):
        print(f"  {sizes[k-1]:>4} -> {sizes[k]:>4}: DP x{dp[k] / dp[k-1]:.2f}")

    # ---- Plots -------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(small, naive, "o-", label="Naive recursion  O(2^n)", color="#c0392b")
    axes[0].plot(small, dp_small, "s-", label="Bottom-up DP  O(n^2)", color="#1f6f8b")
    axes[0].set_yscale("log")
    axes[0].set(xlabel="string length n", ylabel="time (ms, log scale)",
                title="Naive vs Dynamic Programming")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].plot(sizes, dp, "s-", label="DP table + backtrack", color="#1f6f8b")
    axes[1].plot(sizes, linear, "^-", label="Two-row (length only)", color="#2e8b57")
    axes[1].plot(sizes, hirsch, "d-", label="Hirschberg", color="#8e44ad")
    axes[1].set(xlabel="string length n", ylabel="time (ms)",
                title="Quadratic-time algorithms")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("benchmark.png", dpi=140)
    print("\nSaved plot -> benchmark.png")


if __name__ == "__main__":
    main()

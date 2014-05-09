"""
:Synopsis: Mackay's Quantum LDPC Codes (including bicycle codes)
:Author: DOHMATOB Elvis Dopgima <gmdopp@gmail.com> <elvis.dohmatob.inia.fr>

"""

from functools import partial
from random import shuffle
import numpy as np
import pylab as pl
import networkx as nx


def rotate_list (l, r=1):
    l = list(l)
    return l[-r:] + l[:-r]


def kl_div(p, q):
    """
    Kullback-Leibler divergence of q from p.

    """

    msk = (p > 0) * (q > 0)
    p = p[msk]
    q = q[msk]
    p = p / (1. * p.sum())
    q = q / (1. * q.sum())

    return np.sum(p * np.log(p / q))


def best_row_to_rm(h):
    """
    Remove row which does least damage to uniformity of column weights.

    """

    best = 1
    best_core = np.inf
    uniform = np.ones(h.shape[1])
    for r in xrange(h.shape[0]):
        score = kl_div(uniform, np.delete(h, r, axis=0).sum(axis=0))
        if score < best_core:
            best = r
            best_core = score

    return best


def circulant(n, k):
    assert k <= n
    c = np.ndarray((n, n), dtype=int)
    row = np.zeros(n)
    row[:k] = 1
    shuffle(row)
    for r in xrange(n):
        c[r] = row
        row = rotate_list(list(row))

    return c


def bicycle(m, n, k):
    assert n % 2 == k % 2 == 0, "n and k must be even!"
    a, b = n // 2, k // 2
    c = circulant(a, b)
    h0 = np.hstack((c, c.T))

    # remove n / 2 - m rows, making sure column density remains uniform
    if a > m:
        for _ in xrange(a - m):
            h0 = np.delete(h0, best_row_to_rm(h0), axis=0)

    # rm isolated nodes
    h0 = h0[:, (h0.sum(axis=0) > 0)]

    return h0


def parmat2graph(h):
    nchecks, nvars = h.shape
    checks =[r.nonzero()[0] for r in h]
    graph = nx.Graph()
    graph.add_nodes_from(xrange(nvars), bipartite=0)
    graph.add_nodes_from(xrange(nvars, nvars + nchecks), bipartite=1)
    for cn, check in enumerate(checks):
        for vn in check: graph.add_edge(cn + nvars, vn)

    return graph, xrange(nvars), xrange(nvars, nvars + nchecks)


def mackay_monte_carlo_example():
    return 80, 24, 10


if __name__ == '__main__':
    n, m, k = mackay_monte_carlo_example()
    h = bicycle(m, n, k)
    graph = parmat2graph(h)[0]

    pl.close("all")
    pl.figure()
    pl.title("[%i, %i, %i]-Mackay sparse-graph self-dual LDPC code (H)" % (
            m, n, k))
    nx.draw_graphviz(graph, with_labels=False, node_size=30)
    pl.matshow(h)
    pl.gray()
    pl.title("H")
    pl.axis('off')
    pl.figure()
    pl.title("Distribution of weights of columns of H")
    pl.hist(h.sum(axis=0), bins=32)

    pl.show()

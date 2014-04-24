"""
:Synopsis: Toric codes and topolical quantum computers of Kitaev et al.
:Author: DOHMATOB Elvis Dopgima <gmdopp@gmail.com> <elvis.dohmatob.inia.fr>

"""

import itertools
import networkx as nx
import pylab as pl
from qldpc import parmat2graph

# number of variable nodes in Tanner graph
_n_var_nodes = lambda supports: len(set.union(*map(set, supports)))


def _tanner_iter_edges(supports):
    nv = _n_var_nodes(supports)
    for j, cn in enumerate(supports):
        for vn in cn: yield (vn, j + nv)


def _tanner_iter_nodes(supports):
    nv = _n_var_nodes(supports)
    for x in xrange(nv + len(supports)): yield x


def tanner_graph(supports):
    """
    Compute full expansion of Tanner graph.

    """

    G = nx.Graph()
    G.add_edges_from(_tanner_iter_edges(supports))
    return G


def cartprod(G1, G2):
    """
    Cartesian product of two graphs G1 and G2. If the graphs are Tanner
    (i.e bipartite), you should be using tanner_cartprod(...) instead.

    Notes
    -----
    See also `tanner_cartprod`

    """

    G = nx.Graph()
    for (x, y), z in itertools.product(G1.edges_iter(), G2.nodes_iter()):
        G.add_edge((x, z), (y, z))
    for x, (y, z) in itertools.product(G1.nodes_iter(), G2.edges_iter()):
        G.add_edge((x, y), (x, z))

    return G


def cartpow(G, n):
    """
    Cartesian power of a graph.

    Returns
    -------
    G^n.

    """

    assert n > 0
    Gn = G
    for _ in  xrange(n - 1): Gn = cartprod(Gn, G)
    return Gn


def tanner_cartprod(supports1, supports2, return_full=False,
                    split=False):
    """
    Cartesian product G1 x G2 of two Tanner graphs Gi = (Vi, Ci, Ei),
    i = 1, 2, where for each of the lists supportsi has been defined
    as follows: for each ci \in Ci, supports1[ci] is the support of the
    ci-th row of the parity matrix of the cyclic code represented by Gi.

    Note that the cartesian product G1 x G2 is again a Tanner graph since the
    following chromatic equation holds:

        chrom(G1 x G2) = max(chrom(G1), chrom(G2)) = 2.

    Returns
    -------
    supports: list of lists
        compact representation for the cyclic code represented by the Tanner
        graph G1 x G2.

    Notes
    -----
    See also `cartprod`

    """

    if return_full: return cartprod(tanner_graph(supports1),
                                    tanner_graph(supports2))

    nv1, nv2 = _n_var_nodes(supports1), _n_var_nodes(supports2)
    nc1, nc2 = len(supports1), len(supports2)
    v1, c1 = xrange(nv1), xrange(nv1, nv1 + nc1)
    v2, c2 = xrange(nv2), xrange(nv2, nv2 + nc2)
    v = set(itertools.product(v1, v2)).union(itertools.product(c1, c2))
    if split:
        cX = list(itertools.product(c1, v2))
        cZ = list(itertools.product(v1, c2))
        iX, iZ = [], []
        c = set(cX).union(cZ)
    else: c = set(itertools.product(c1, v2)).union(itertools.product(v1, c2))
    vertices = set(v).union(c)
    v, c = list(v), list(c)
    supports = map(lambda _: [], c)  # XXX [[]] * nc is risky for the sequel!
    linked = lambda a, b, nv, nc, s: (nv <= b < nv + nc and a in s[b - nv]
                                      ) or (nv <= a < nv + nc and
                                            b in s[a - nv])

    # XXX the following loop is sub-optimal!
    for (x, y), (x_, y_) in itertools.product(vertices, vertices):
        if (x == x_ and linked(y, y_, nv2, nc2, supports2)) or (
            y == y_ and linked(x, x_, nv1, nc1, supports1)):
            if (x, y) in c and (x_, y_) in v:
                i = c.index((x, y))
                if split:
                    if (x, y) in cX and not i in iX: iX.append(i)
                    elif not i in iZ: iZ.append(i)
                supports[i].append(v.index((x_, y_)))

    if split: return [supports[i] for i in iX], [supports[i] for i in iZ]
    return supports


def tanner_cartpow(supports, n, return_full=False):
    """
    Cartesian power of Tanner graph G. Note that G^n is again a Tanner graph.

    Returns
    -------
    Compact representation supports_, for G^n.

    """

    if return_full: return cartpow(tanner_graph(supports), n)
    supports_ = supports
    for _ in xrange(n - 1): supports_ = tanner_cartprod(supports_, supports)
    return supports_


def torus(m):
    """
    Constructs an m-by-m lattice on a torus. It is worth noting that this
    is simply the (cartesian) product of two cycles of length m.

    This is the building block of Kivaet's toric code and extensions thereof.

    """

    c = nx.cycle_graph(m)
    return cartprod(c, c)


def tztprod(V1, C1, E1, V2, C2, E2):
    """
    Tillich-Zemor product of Tanner graphs G1 = (V1, C1, E1) and
    G2 = (V2, C2, E2).

    """

    pass

if __name__ == "__main__":
    import sys
    pl.close("all")
    m = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    pl.figure()
    pl.title("%i-by-%i regular paving of the torus" % (m, m))
    nx.draw_graphviz(torus(m), node_size=30, with_labels=False)

    s1 = s2 = [[0, 2], [0, 1], [1, 2]]
    s = tanner_cartprod(s1, s2, split=True)
    t = tanner_cartprod(s1, s2, return_full=True)
    pl.figure()
    pl.suptitle("Sum decomposition of Tanner graph products")
    for j, support in enumerate([s1, s2]):
        ax = pl.subplot("32%i" % (j + 1))
        ax.set_title("t%i = tanner(%s)" % (j + 1, support))
        tj = tanner_graph(support)
        nx.draw_graphviz(tj, with_labels=0, node_size=30)
    ax = pl.subplot("312")
    ax.set_title("t1 x t2 =: t =: t1' + t2'")
    nx.draw_graphviz(t, with_labels=0, node_size=30)
    for j, sj in enumerate(s):
        ax = pl.subplot("32%i" % (4 + j + 1))
        ax.set_title("t%i'" % (j + 1))
        tj = tanner_graph(sj)
        nx.draw_graphviz(tj, with_labels=0, node_size=30)
    pl.show()

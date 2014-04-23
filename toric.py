"""
:Synopsis: Toric codes and topolical quantum computers of Kitaev et al.

"""

import itertools
import networkx as nx
import pylab as pl
from qldpc import parmat2graph

# number of variable nodes in Tanner graph
n_var_nodes = lambda supports: len(set.union(*map(set, supports)))


def tanner_graph(supports):
    """
    Compute full expansion of Tanner graph.

    """

    nv = n_var_nodes(supports)
    G = nx.Graph()
    for j, cn in enumerate(supports):
        for vn in cn: G.add_edge(j + nv, vn)

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
    for x, y in itertools.product(G1.nodes_iter(), G2.nodes_iter()):
        for x_, y_ in itertools.product(G1.nodes_iter(), G2.nodes_iter()):
            if (x == x_ and G2.has_edge(y, y_)) or (
                y == y_ and G1.has_edge(x, x_)):
                G.add_edge((x, y), (x_, y_))

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


def tanner_cartprod(supports1, supports2, return_full=False):
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

    if return_full:
        return cartprod(tanner_graph(supports1), tanner_graph(supports2))

    nv1 = len(set.union(*map(set, supports1)))
    nv2 = len(set.union(*map(set, supports2)))
    nc1 = len(supports1)
    nc2 = len(supports2)
    v1 = xrange(nv1)
    c1 = xrange(nv1, nv1 + nc1)
    v2 = xrange(nv2)
    c2 = xrange(nv2, nv2 + nc2)
    v = set(itertools.product(v1, v2)).union(itertools.product(c1, c2))
    c = set(itertools.product(c1, v2)).union(itertools.product(v1, c2))
    vertices = set(v).union(c)
    v = list(v)
    c = list(c)
    supports = map(lambda _: [], c)  # [[]] * nc leads to entangled pointers!
    linked = lambda a, b, nv, nc, s: (nv <= b < nv + nc and a in s[b - nv]
                                      ) or (nv <= a < nv + nc and
                                            b in s[a - nv])
    for (x, y), (x_, y_) in itertools.product(vertices, vertices):
        if (x == x_ and linked(y, y_, nv2, nc2, supports2)) or (
            y == y_ and linked(x, x_, nv1, nc1, supports1)):
            if (x, y) in c and (x_, y_) in v:
                supports[c.index((x, y))].append(v.index((x_, y_)))

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
    pl.title("%i-by-%i lattice torus graph" % (m, m))
    nx.draw_graphviz(torus(m), node_size=30, with_labels=False)
    pl.show()

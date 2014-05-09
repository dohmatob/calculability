"""
:Author: DOHMATOB Elvis Dopgima <gmdopp@gmail.com> <elvis.dohmatob.inia.fr>

"""

import itertools
import numpy as np
import networkx as nx
import pylab as pl

# number of variable nodes in Tanner graph
_tanner_nvar_nodes = lambda checks: len(set.union(*map(set, checks)))


def rotate_list (l, r=1):
    """
    Rotates list (l) r places to the right.

    """

    l = list(l)
    return l[-r:] + l[:-r]


def parmat2graph(h):
    nchecks, nvars = h.shape
    checks =[r.nonzero()[0] for r in h]
    graph = nx.Graph()
    graph.add_nodes_from(xrange(nvars), bipartite=0)
    graph.add_nodes_from(xrange(nvars, nvars + nchecks), bipartite=1)
    for cn, check in enumerate(checks):
        for vn in check: graph.add_edge(cn + nvars, vn)

    return graph, xrange(nvars), xrange(nvars, nvars + nchecks)


def _tanner_iter_nodes(checks):
    for node in xrange(_tanner_nvar_nodes(checks) + len(checks)): yield node


def _tanner_iter_edges(checks):
    nvars = _tanner_nvar_nodes(checks)
    for cn, check in enumerate(checks):
        for vn in check: yield vn, cn + nvars


def tanner_graph(checks):
    G = nx.Graph()
    G.add_edges_from(_tanner_iter_edges(checks))
    return G


def tanner_cycle(n):
    return [[j, (j + 1) % n] for j in xrange(n)]


def tanner_cartesian_product(checks1, checks2, split=False):
    """
    Cartesian product G1 x G2 of two Tanner graphs Gi = (Vi, Ci, Ei),
    i = 1, 2, where for each of the lists checksi has been defined
    as follows: for each ci \in Ci, checks1[ci] is the support of the
    ci-th row of the parity matrix of the cyclic code represented by Gi.

    Note that the cartesian product G1 x G2 is again a Tanner graph since the
    following chromatic equation holds:

        chrom(G1 x G2) = max(chrom(G1), chrom(G2)) = 2.

    Returns
    -------
    checks: list of lists
        compact representation for the cyclic code represented by the Tanner
        graph G1 x G2.

    """

    nvars1, nvars2 = _tanner_nvar_nodes(checks1), _tanner_nvar_nodes(checks2)
    nchecks1, nchecks2 = len(checks1), len(checks2)
    var_nodes1, var_nodes2 = xrange(nvars1), xrange(nvars2)
    check_nodes1 = xrange(nvars1, nvars1 + nchecks1)
    check_nodes2 = xrange(nvars2, nvars2 + nchecks2)
    var_nodes = list(set(itertools.product(var_nodes1, var_nodes2)).union(
            itertools.product(check_nodes1, check_nodes2)))
    if split:
        iX, iZ = [], []
        check_nodesX = list(itertools.product(check_nodes1, var_nodes2))
        check_nodesZ = list(itertools.product(var_nodes1, check_nodes2))
        check_nodes = list(set(check_nodesX).union(check_nodesZ))
    else:
        check_nodes = list(set(itertools.product(
                    check_nodes1, var_nodes2)).union(
                itertools.product(var_nodes1, check_nodes2)))
    checks = [[] for _ in xrange(len(check_nodes))]
    for (x, y), z in itertools.product(_tanner_iter_edges(checks1),
                                       _tanner_iter_nodes(checks2)):
        if (x, z) in check_nodes:
            cn, vn = check_nodes.index((x, z)), var_nodes.index((y, z))
            if split and not (cn in iX or cn in iZ): iX.append(cn)
        else:
            cn, vn = check_nodes.index((y, z)), var_nodes.index((x, z))
            if split and not (cn in iX or cn in iZ): iZ.append(cn)
        checks[cn].append(vn)
    for x, (y, z) in itertools.product(_tanner_iter_nodes(checks1),
                                       _tanner_iter_edges(checks2)):
        if (x, y) in check_nodes:
            cn, vn = check_nodes.index((x, y)), var_nodes.index((x, z))
            if split and not (cn in iX or cn in iZ): iX.append(cn)
        else:
            cn, vn = check_nodes.index((x, z)), var_nodes.index((x, y))
            if split and not (cn in iZ or cn in iX): iZ.append(cn)
        checks[cn].append(vn)

    return ([checks[i] for i in iX], [checks[i] for i in iZ]
            ) if split else checks


def tanner_cartesian_power(checks, n, split=False):
    """
    Cartesian power of Tanner graph G. Note that G^n is again a Tanner graph.

    Returns
    -------
    Compact representation checks_, for G^n.

    """

    checks_ = checks
    for _ in xrange(n - 2):
        checks_ = tanner_cartesian_product(checks_, checks)
    return tanner_cartesian_product(checks_, checks, split=split)


def css_code(GX, GZ):
    """
    CSS code construction.

    """

    # XXX use scipy.linalg sparse constructs (csr_matrix, etc.) !!!
    return np.vstack((np.hstack((GX, np.zeros((GX.shape[0], GZ.shape[1])))),
                      np.hstack((np.zeros((GZ.shape[0], GX.shape[1])), GZ))))


def kovalev_code(H1, H2):
    """
    Kovalev et al's kron product construction.

    """

    r1, n1 = H1.shape
    r2, n2 = H2.shape
    E1 = np.eye(r1)
    E1_ = np.eye(n1)
    E2 = np.eye(r2)
    E2_ = np.eye(n2)

    return css_code(np.hstack((np.kron(E2, H1), np.kron(H2, E1))),
                    np.hstack((np.kron(H2.T, E1_), np.kron(E2_, H1.T))))


def repetition_code_circulant_matrix(d):
    """
    Returns circulant matrix of repetition code (Hc), where:

        g = 1 + x + x^2 + ... + x^(n - 1)
        h = (x^n - 1) / g = 1 + x (mod 2)
        Hc = [h, hx, hx^2, ..., hx^(n - 1)]^T

    """

    assert d >= 2
    h = np.append([1, 1], np.zeros(d - 2))
    return np.vstack([rotate_list(h, r=r) for r in xrange(d)])


def kovalev_toric_code_construction(d):
    G = repetition_code_circulant_matrix(d)
    return kovalev_code(G, G)

if __name__ == "__main__":
    pl.close("all")
    d = 3

    # gridded torus
    pl.figure()
    pl.title("%i-by-%i regular paving of the torus" % (d, d))
    nx.draw_graphviz(tanner_graph(tanner_cartesian_power(tanner_cycle(d), 2)),
                     node_size=30, with_labels=False)

    # Tillich-Zemor hypergraph-product constructions
    s1 = s2 = tanner_cycle(d)
    s = tanner_cartesian_product(s1, s2, split=True)
    t = nx.cartesian_product(tanner_graph(s1), tanner_graph(s2))
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

    # Kovalev et al's kron constructions
    toric = kovalev_toric_code_construction(d)
    pl.figure()
    title = ("Toric [%i, 2, %i]-code H using Kovalev et al's kron "
             "product trick") % (2 * d ** 2, d)
    pl.title(title)
    nx.draw_graphviz(parmat2graph(toric)[0], with_labels=False, node_size=30)
    pl.matshow(toric)
    pl.title(title)
    pl.gray()
    pl.axis('off')

    pl.show()

import itertools
import networkx as nx

# number of variable nodes in Tanner graph
_tanner_nvar_nodes = lambda checks: len(set.union(*map(set, checks)))


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

if __name__ == "__main__":
    import pylab as pl
    pl.close("all")

    m = 15
    pl.figure()
    pl.title("Kitaev Toric code [%i, 4, %i]: %i-by-%i regular paving of "
             "the torus" % (2 * m ** 2, m, m, m))
    nx.draw_graphviz(tanner_graph(tanner_cartesian_power(tanner_cycle(m), 2)),
                     node_size=30, with_labels=False)

    s1 = s2 = tanner_cycle(5)
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
    pl.show()

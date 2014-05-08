import itertools
import networkx as nx

# number of variable nodes in a Tanner graph
_tanner_n_var_nodes = lambda supports: len(set.union(*map(set, supports)))


def _tanner_iter_edges(supports):
    nvars = _tanner_n_var_nodes(supports)
    for cn, support in enumerate(supports):
        for vn in support: yield vn, cn + nvars


def _tanner_iter_nodes(supports):
    for i in xrange(_tanner_n_var_nodes(supports) + len(supports)): yield i


def tanner_graph(supports):
    """
    Create Tanner graph from its compact representation.

    """

    G = nx.Graph()
    G.add_edges_from(_tanner_iter_edges(supports))
    return G


def tanner_cartprod(supports1, supports2):
    """
    Cartesian product of two Tanner graphs.

    """

    nvars1, nvars2 = map(_tanner_iter_edges, supports)
    nchecks1, nchecks2 = map(len, supports)
    vars1, vars2 = map(xrange, [nvars1, nvars2])
    checks1, checks2 = map(xrange, [nvars1 + nchecks1, nvars2 + nchecks2])
    checks = set(itertools.product(checks1, vars2)).union(itertools.product(vars1, checks2))
    G = nx.Graph()
    for (x, y), z in itertools.product(_tanner_iter_edges(supports1),
                                       _tanner_iter_nodes(supports2)):
        G.add_edge((x, z), (y, z))

    for x, (y, z) in itertools.product(_tanner_iter_nodes(supports1),
                                       _tanner_iter_edges(supports2)):
        G.add_edge((x, y), (x, z))

    return G

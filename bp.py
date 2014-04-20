"""
:Synopsis: Believe propagation for decoding (binary!) LDPC codes.
:Author: DOHMATOB Elvis Dopgima <gmdopp@gmail.com> <elvis.dohmatob.inia.fr>

"""

import numpy as np
import networkx as nx
import pylab as pl
import itertools

# aribirary dimensional hypercube generator
hypercube = lambda n: itertools.product(*([[0, 1]] * n))


class BP(object):
    """
    Believe propagation for decoding (binary!) LDPC codes.

    """

    def __init__(self, codelength, p, checks):
        """
        Parameters
        ----------
        p: float in the interval [0, 1]
           channel noise: p = P(receive 0 | sent 1) = P(receive 1 | sent 0)

        checks: list of lists of integers
            the supports of the rows of the parity matric of the code

        """

        self.codelength = codelength
        assert 0 <= p <= 1.
        self.p = p
        self.checks = checks
        self.q_ = 1. - p
        self.channel_ = np.array([[self.q_, p], [p, self.q_]])
        self.nchecks_ = len(checks)
        self.graph_ = nx.Graph()  # bipartite graph to hold problem

        # variable nodes
        self.var_nodes_ = range(codelength)
        self.graph_.add_nodes_from(self.var_nodes_, bipartite=0)

        # "check" / factor nodes
        self.check_nodes_ = range(codelength, codelength + self.nchecks_)
        self.graph_.add_nodes_from(self.check_nodes_, bipartite=1)

        # connect variable and check nodes
        for cn, check in zip(self.check_nodes_, checks):
            for vn in check: self.graph_.add_edge(cn, vn)

    def fit(self, obs):
        """
        Learn marginals, given observation.

        Parameters
        ----------
        obs: array of `self.codelength` bits
            observation vector

        """

        # sanitize observation
        assert len(obs) == self.codelength
        for ob in obs: assert ob in [0, 1]

        # initialization
        self.pkts_ = {}
        self.marginals_ = np.ndarray((self.codelength, 2))
        for vn in self.var_nodes_:
            self.marginals_[vn] = self.channel_[obs[vn]].copy()
            for cn in self.graph_.neighbors(vn):
                if self.graph_.degree(vn) == 1:
                    print "%i -> %i:" % (vn, cn), self.marginals_[vn]
                    self.pkts_[(vn, cn)] = self.marginals_[vn]

        # handle "check" nodes
        for cn in self.check_nodes_:
            self.pkts_for_me = dict((src, pkt) for (
                    src, dst), pkt in self.pkts_.iteritems() if dst == cn)
            for vn in self.graph_.neighbors(cn):
                self.pkts_for_me_ = dict((src, pkt) for (
                        src, pkt) in self.pkts_for_me.iteritems(
                        ) if src != vn)
                neighbors_ = self.pkts_for_me_.keys()
                pkt = np.zeros(2)
                for b in xrange(2):
                    for i in hypercube(len(neighbors_) - 1):
                        aux = self.pkts_for_me_.values()[-1][(b + np.sum(i)) % 2]
                        aux *= np.prod([tmp[i[neighbors_.index(key)]] for (
                                    key, tmp) in self.pkts_for_me_.items(
                                    )[:-1]], axis=0)
                        pkt[b] += aux

                # cn -> vn
                print "%s -> %s:" % (cn, vn), pkt
                self.pkts_[(cn, vn)] = pkt

        # handle variable nodes
        for vn in self.var_nodes_:
            self.pkts_for_me = dict((src, pkt) for (
                    src, dst), pkt in self.pkts_.iteritems() if dst == vn)
            self.marginals_[vn] *= np.prod(self.pkts_for_me.values(), axis=0)
            self.marginals_[vn] /= self.marginals_[vn].sum()  # normalize

            # XXX the following code is useless
            neighbors = self.pkts_for_me.keys()
            for cn in self.graph_.neighbors(vn):
                aux = [pkt for src, pkt in self.pkts_for_me.iteritems(
                        ) if src != cn]
                pkt = np.prod(aux, axis=0) if aux else np.array([.5, .5])
                self.pkts_[(vn, cn)] = pkt
                print "%s -> %s:" % (vn, cn), pkt

        return self

if __name__ == "__main__":
    codelength = 7
    p = .4
    checks = [[0, 1, 2], [0, 3, 4], [0, 5, 6]]
    obs = [1, 0, 0, 0, 0, 1, 0]
    bp = BP(codelength, p, checks).fit(obs)
    print bp.marginals_

    # pl.close("all")
    # nx.draw_graphviz(bp.graph_)
    # pl.show()

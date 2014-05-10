"""
:Synopsis: Believe propagation for decoding (binary!) LDPC codes.
:Author: DOHMATOB Elvis Dopgima <gmdopp@gmail.com> <elvis.dohmatob.inia.fr>

"""

import itertools
import numpy as np
import pylab as pl
import networkx as nx

# aribirary dimensional hypercube generator
hypercube = lambda n: itertools.product(*([[0, 1]] * n))


class LdpcBpDecoder(object):
    """
    Believe Propagation decoder for LDPCs (Low-Density Parity-Check Codes).

    Parameters
    ----------
    checks: list of lists of integers
        The supports of the rows of the parity matric of the code.

    channel_model: string, optional (default None)
        Noise model in chanel.
        Possible values are:
        'BSC': Binary symmetric Channel. Here, p must be specified.
        'AWGN': Additive White Gaussian Noise. Here, snr must be specified.

    p: float in the open interval (0, 1), optional (default None)
        Crossover probability of BSC channel.

    snr: float, optional (default None)
        SNR for AWGN channel.

    verbose: int, optional (default 1)
        Verbosity level.

    Attributes
    ----------
    graphs_: nx.Graph object
        Graphical representation of the LDPC as a bipartite graph.

    nchecks_: int
        Number of check nodes (i.e number of rows in parity-check matrix).

    check_nodes_: list of `self.nchecks_` integers
        The check nodes.

    var_nodes_: list of `self.codelength` integers
        The variable nodes.

    pkts_: dict with items (src, dst) -> pkt
        Packets sent at last iteration.

    self.llrs_: list of `self.codelength` floats
        Initial log-likelihood ratios, given the received word.

    self.l_: list of `self.codelength` floats
        Final log-likelihood ratios.

    self.x_: array of `self.codelength` bits
        MAP codeword decoded from the received word.

    References
    ----------
    [1] http://sigpromu.org/sarah/SJohnsonLDPCintro.pdf

    """

    def __init__(self, codelength, checks, channel_model=None, p=None,
                 snr=None, verbose=1):

        self.verbose = verbose
        if channel_model is None:
            if not p is None: channel_model = "BSC"
        if channel_model is None:
            if not snr is None: channel_model = "AWGN"

        if channel_model: channel_model = channel_model.upper()
        assert channel_model in ["BSC", "AWGN"], (
            "Unsupported channel model: %s" % channel_model)
        if channel_model == "BSC":
            assert not p is None
            assert 0 < p < 1., (
                "p must be in the open interval (0, 1); got %g" % p)
        self.p = p
        self.snr = snr
        self.channel_model = channel_model
        self.codelength = codelength
        self.checks = checks
        self.nchecks_ = len(checks)

        # bipartite graph representation of the LDPC
        self.graph_ = nx.Graph()

        # add variable nodes
        self.var_nodes_ = xrange(codelength)
        self.graph_.add_nodes_from(self.var_nodes_, bipartite=0)

        # add "check" / factor nodes
        self.check_nodes_ = xrange(codelength, codelength + self.nchecks_)
        self.graph_.add_nodes_from(self.check_nodes_, bipartite=1)

        # connect variable and check nodes
        for cn, check in zip(self.check_nodes_, checks):
            for vn in check: self.graph_.add_edge(cn, vn)

        # generate node pseudos
        self.pseudos_ = {}
        for node in self.graph_.nodes():
            self.pseudos_[node] = (
                "BIT_%i" % node if node < self.codelength else "[%s = 0]" % (
                    " XOR ".join(["BIT_%i" % b for b in self.checks[
                                node - self.codelength]])))

    def compute_llr(self, obs):
        """
        Compute (initial) log-likelihood ratios, given evidence.

        """

        if self.channel_model == "BSC":
            q = 1. - self.p
            self.llrs_ = -np.log([self.p / q, q / self.p])[obs]
        elif self.channel_model == "AWGN":
            self.llrs_ = 4 * np.array(obs) * self.snr

    def recv(self, node):
        """
        Gather incoming messages at given node.

        """

        return dict((src, pkt) for (src, dst), pkt in self.pkts_.iteritems(
                ) if dst == node)

    def send(self, src, dst, pkt):
        """
        Send pkt from src to dst.

        """

        if self.verbose: print "\t\t%s -> %s:" % (
            self.pseudos_[src], self.pseudos_[dst]), pkt
        self.pkts_[(src, dst)] = pkt

    def handle_variable_node(self, vn):
        """
        Work done at variable node, on each round.

        """

        # gather incoming messages
        inbox = self.recv(vn)

        # update log-likelihood ratios
        self.l_[vn] = np.sum(inbox.values())
        self.l_[vn] += self.llrs_[vn]
        self.x_[vn] = self.l_[vn] <= 0.

        # spread the rumours
        for cn in self.graph_.neighbors(vn):
            pkt = np.sum([pkt for src, pkt in inbox.iteritems(
                        ) if src != cn])  # rumours
            pkt += self.llrs_[vn]  # our own belief
            pkt = int(pkt <= 0), np.abs(pkt)

            # send pkt from vn to cn
            self.send(vn, cn, pkt)

    def handle_check_node(self, cn):
        """
        Work done at check node, on each round.

        """

        # gather incoming messages
        inbox = self.recv(cn)

        # spread the rumours
        for vn in self.graph_.neighbors(cn):
            # accumulate pkts from other neighboring variable nodes
            signs, mags = zip(*[pkt for src, pkt in inbox.iteritems(
                        ) if src != vn])
            pkt = np.min(mags) * (-1) ** (np.sum(signs) % 2)

            # send pkt from cn to vn
            self.send(cn, vn, pkt)

    def is_codeword(self, x):
        bits = np.array(x, dtype=int) % 2
        for check in self.checks:
            if bits[check].sum() % 2: return false
        else: return True

    def fit(self, obs, max_iter=100):
        """
        BP decoding of a corrupt word. See Algorithm 4 of [1].

        Parameters
        ----------
        obs: array of `self.codelength` bits
            Observed word.

        """

        # sanitize observation
        if self.verbose: print "BP: initialization (loadin evidence...)"
        assert len(obs) == self.codelength
        if self.channel_model == "BSC":
            for ob in obs: assert ob in [0, 1]

        # initialization
        self.x_ = np.array(obs, dtype=int)
        old_pkts = None
        self.pkts_ = {}  # messages sent on the graph
        self.compute_llr(obs)
        self.l_ = np.ndarray(self.llrs_.shape)  # dynamic log-likelihood ratios

        # iterative BP (message passing) loop
        self.ok_ = False
        for it in xrange(max_iter):
            if self.verbose:
                print "_" * 79
                print "BP: iter %03i/%03i..." % (it + 1, max_iter)

            # handle variable nodes (in parallel)
            if self.verbose: print "\tHandling variable nodes..."
            map(self.handle_variable_node, self.var_nodes_)

            # handle "check" nodes (in parallel)
            if self.verbose: print "\tHandling check nodes..."
            map(self.handle_check_node, self.check_nodes_)

            # test for convergence
            if self.verbose: print "\tTesting for convergence..."
            for check in self.checks:
                if self.x_[check].sum() % 2:
                    if self.verbose:
                        print "\tA check failed:  %s != 0" % " XOR ".join(
                            map(str, self.x_[check]))
                    break
            else:
                self.ok_ = True
                if self.verbose: print "\tOK."
                break

            # abort if we've reached steady-state
            if self.pkts_ == old_pkts: break
            else: old_pkts = self.pkts_.copy()

        # print results
        if self.verbose:
            print "_" * 79
            if it < max_iter - 1:
                status = "perfectly decoded" if self.ok_ else (
                    "some errors could not be decoded")
                print "Converged after %i iterations (%s)." % (it + 1, status)
            else:
                print "Did not converge in %i iterations." % max_iter
            print "\tMAP codeword:", "".join(map(str, self.x_))
            print "\tChecks:"
            for check in self.checks:
                res = np.sum(self.x_[check]) % 2
                print "\t%s = %s = %i (%s)" % (
                    " XOR ".join(["BIT_%i" % b for b in check]),
                    " XOR ".join(map(str, self.x_[check])), res,
                    "FAILED!" if res else "PASSED!")

        return self

    def apply_bsc(self, codeword):
        assert len(codeword) == self.codelength
        assert self.channel_model == "BSC"
        assert self.is_codeword(codeword)
        return (np.array(codeword, dtype=int) + (np.random.rand(
                    self.codelength) < self.p)) % 2


def demo_1():
    """
    Demo 2 of:
    http://www.stanford.edu/~montanar/RESEARCH/BOOK/partD.pdf

    """

    codelength = 7
    p = .49
    checks = [[0, 1, 2], [0, 3, 4], [0, 5, 6]]
    obs = [1, 0, 0, 0, 0, 1, 0]
    bp = LdpcBpDecoder(codelength, checks, p=p).fit(obs)
    return bp


def demo_2():
    """
    Example 2.5 of:
    http://sigpromu.org/sarah/SJohnsonLDPCintro.pdf

    """

    codelength = 6
    p = .2
    checks = [[0, 1, 3], [1, 2, 4], [0, 4, 5], [2, 3, 5]]
    obs = [1, 0, 1, 0, 1, 1]
    return LdpcBpDecoder(codelength, checks, p=p).fit(obs)


def demo_3():
    """
    Example 2.6 of:
    http://sigpromu.org/sarah/SJohnsonLDPCintro.pdf

    """

    codelength = 6
    snr = 1.25
    checks = [[0, 1, 3], [1, 2, 4], [0, 4, 5], [2, 3, 5]]
    obs = [-.1, .5, -.8, 1., -.7, .5]
    return LdpcBpDecoder(codelength, checks, snr=snr).fit(obs)


def demo_4():
    codelength = 6
    checks = [[0, 1, 2, 3], [2, 3, 5], [0, 3, 4]]
    p = .1
    obs = [1, 1, 1, 0, 0, 0]
    return LdpcBpDecoder(codelength, checks, p=p).fit(obs)

if __name__ == "__main__":
    pl.close("all")
    for x in xrange(1, 5):
        demo = "demo_%i" % x
        bp = eval(demo)()
        pl.figure()
        pl.title("graph for %s" % demo)
        nx.draw_graphviz(bp.graph_)
    pl.show()

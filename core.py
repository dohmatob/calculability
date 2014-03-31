"""
:Synopsis: Core utilities
:Author: DOHMATOB Elvis Dopgima <gmdopp@gmail.com> <elvis.dohmatob@inria.fr>

"""

import numpy as np
from sklearn.externals.joblib import Memory

'''
Bernoulli variable with parameter p
'''
flip = lambda p=.5, seed=None: np.random.rand() <= p


def multinomial(probs):
    '''
    Multinomial variable

    Parameters
    ----------
    probs: 1D array-like
       weight of each class

    '''

    cs = np.cumsum(probs)  # CDF
    cs /= cs.max()  # normalization for stochasticity

    return np.min(np.nonzero(np.random.rand() <= cs))


class MarkovChain(object):
    """
    Finite-state discrete-time Markov chain.

    """

    def __init__(self, trans_table=None, n_states=None, memory=Memory(None)):
        self.memory = memory
        self.trans_table = trans_table
        self.n_states = n_states
        if trans_table is None:
            assert not n_states is None, (
                "Exactly on of trans_table and n_states should be specified!")
            self.n_states_ = n_states
            self.trans_table_ = self.memory.cache(np.random.rand)(n_states, n_states)

            # normalization for stochasticity
            self.trans_table_ /= self.trans_table_.sum(axis=1)
        else:
            assert n_states is None, (
                "Exactly on of trans_table and n_states should be specified!")
            self.trans_table_ = np.array(self.trans_table)
            n, m = self.trans_table_.shape
            assert n == m
            self.n_states_ = m

    def _check_none(self, x): return 0 if x is None else x

    def draw(self, x): return multinomial(self.trans_table_[
            self._check_none(x)])

    def trans(self, x, y): return self.trans_table_[self._check_none(x),
                                                    self._check_none(y)]


def metropolis_hastings(p, q, n_samples, x0=None, maxit=1000, lag=100):
    """
    Metropolis Hastings (rejection) sampler.

    Parameters
    ----------
    p: callable
        distribution from which we're trying to sample p(x) returns the
        probablity mass at x

    q: object with methods draw(...) and trans(...)
        auxiliary machine: draw(x) returns a sample from q(.|x) whilst
        trans(...) returns the probablity of the transition x -> y.

    n_samples: int
        number of samples to draw

    x0: an acceptable argument for p and q (optional, default None)
        starting state

    maxit: int, optional (default 1000)
        maximum number of iterations to run

    lag: int, optional (default 100)
       the first `lag` draws will be rejected (so that the engine warms up)

    Returns
    -------
    generator (for generating n_samples points from the distribution p, using
    the "proposal" q.

    Notes
    -----
    insofar as maxit is large enough, x0 is irrelevant

    """

    x = x0
    maxit = max(maxit, n_samples + lag)  # maxit should be large enough
    for i in xrange(maxit):
        # draw y from q(.|x)
        y = q.draw(x)

        # keep y with probablity min(p(y)*q.trans(x,y)/(p(x)*q.trans(y,x)),1.)
        if flip(min(p(y) * q.trans(y, x) / (p(x)  * q.trans(x, y)), 1.)): x = y

        # yield sample point if in tail of runs
        if i >= maxit - n_samples: yield x

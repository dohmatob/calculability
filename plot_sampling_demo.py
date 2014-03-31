from core import metropolis_hastings, MarkovChain
import pylab as pl


if __name__ == "__main__":
    q = MarkovChain(trans_table=[[.5, .5], [.4, .6]])

    # one can easily show (linear algebra) that the MC above
    # has the following limiting distro:
    p = lambda x: [4. / 9, 5. / 9][0 if x is None else x]

    pl.close("all")
    for i in xrange(3):
        samples = [x for x in metropolis_hastings(p, q, 1000)]
        pl.figure()
        ax = pl.subplot(111)
        pl.title("clone %i" % i)
        pl.hist(samples, bins=q.n_states_)
        pl.setp(ax.get_xticklabels(), visible=False)

    pl.show()

"""
:Synopsis: Tug-of-War generative model
:Author: DOHMATOB Elvis Dopgima <gmdopp@gmail.com>

"""

import numpy as np
from joblib import Memory
import tempfile
from core import flip

mem = Memory(tempfile.mkdtemp(prefix="tow"), verbose=-1)
strength = lambda person: 10 if mem.cache(flip)(seed=person) else 5
lazy = lambda _: flip(1. / 3)
pull = lambda person: .5 * strength(person) if lazy(
  person) else strength(person)
total_pulling = lambda team: np.sum(map(pull, team))
winner = lambda team1, team2: team2 if total_pulling(team1) < total_pulling(
  team2) else team1

print [winner(*competitors)
       for competitors in [(("alice", "bob"), ("sue", "tom")),
                           (("alice", "bob"), ("sue", "tom")),
                           (("alice", "sue"), ("bob", "tom")),
                           (("alice", "sue"), ("bob", "tom")),
                           (("alice", "tom"), ("bob", "sue")),
                           (("alice", "tom"), ("bob", "sue"))]]

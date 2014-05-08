import numpy as np

LEN = 200
MAX_ITER = 10000
RULE = {'111': "0", "110": "1", "101": "1", "100": "0", "011": "1",
        "010": "1", "001": "1", "000": "0"}

if __name__ == "__main__":
    s = (np.random.rand(LEN) > .4)
    s = "".join(map(str, map(int, s)))
    for _ in xrange(MAX_ITER):
        print "".join(s).replace("1", "#").replace("0", " ")
        s_ = list(s)
        for j in xrange(len(s)):
            s_[j] = RULE["".join([s[(j - 1) % len(s)],
                                 s[j], s[(j + 1) % len(s)]])]
        s = s_

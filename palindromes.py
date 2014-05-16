def palindromes(n, base=10):
    """
    Recursively generates all palindromes of length n, with given base.

    """

    if n > 0:
        if n % 2:
            for s in palindromes(n - 1, base=base):
                for j in xrange(base):
                    m = (n - 1) // 2
                    yield s[:m] + str(j) + s[m:]
        else:
            for s in palindromes(n - 2, base=base):
                for j in xrange(1, base): yield str(j) + s + str(j)
    else: yield ''


if __name__ == "__main__":
    for x in palindromes(5, base=10):
        print x

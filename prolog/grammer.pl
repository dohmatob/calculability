%File: grammar.pl
%Example of a small generative grammar with 3 re-write rules
%and 9 lexical entries (facts).

%Rules
%Each rule has two argument variables that represent lists.
%The first list is the input to the rule and the second is
%used to keep track of the remaining input.

s(L1,L) :- np(L1,L2), vp(L2,L).
np(L1,L) :- d(L1,L2), n(L2,L).
vp(L1,L) :- v(L1,L2), np(L2,L).

%Lexicon
%Each lexical entry represents a word and its lexical category.

d([the|L],L).
d([a|L],L).
n([dog|L],L).
n([cat|L],L).
n([gardener|L],L).
n([policeman|L],L).
n([butler|L],L).
v([chased|L],L).
v([saw|L],L).

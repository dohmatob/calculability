% A small family somewhere in France.

male(elton).
male(gaston).
male(edouard).
male(octave).
male(george).

female(eva).
female(magali).
female(nadine).
female(simone).
female(alize).
female(sophie).

parent(elton, edouard).
parent(elton, magali).
parent(eva, edouard).
parent(eva, magali).

parent(gaston, octave).
parent(gaston, george).
parent(simone, octave).
parent(simone, george).

parent(magali, nadine).
parent(magali, sophie).
parent(magali, alize).
parent(octave, nadine).
parent(octave, sophie).
parent(octave, alize).

child(X, Y) :-
    parent(Y, X).

son(X, Y) :-
    male(X),
    child(X, Y).

daughter(X, Y) :-
    female(X),
    child(X, Y).

mother(X, Y) :-
    female(X),
    parent(X, Y).

father(X, Y) :-
    male(X),
    parent(X, Y).

grandparent(X, Y) :-
    parent(X, Z),
    parent(Z, Y).

grandmother(X, Y) :-
    mother(X, Z),
    parent(Z, Y).

grandfather(X, Y) :-
    father(X, Z),
    parent(Z, Y).

grandchild(X, Y) :-
    grandparent(Y, X).

grandson(X, Y) :-
    male(X),
    grandchild(X, Y).

granddaughter(X, Y) :-
    female(X),
    grandchild(X, Y).

brother(X, Y) :-
    male(X),
    parent(Z, X),
    parent(Z, Y).

sibling(X, Y) :-
    parent(Z, X),
    parent(Z, Y).

sister(X, Y) :-
    female(X),
    sibling(X, Y).
    
uncle(X, Y) :-
    parent(Z, Y),
    brother(X, Z).

aunt(X, Y) :-
    parent(Z, Y),
    sister(X, Z).

ancestor(X, Y) :-
    parent(X, Y).

ancestor(X, Y) :-
    parent(X, Z),
    ancestor(Z, Y).

descendant(X, Y) :-
    ancestor(Y, X).

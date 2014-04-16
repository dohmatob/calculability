% Towers of Hanoi puzzle with N towers
% (c) DOHMATOB Elvis Dopgima

hanoi(A, B, C, N) :-
    hanoi_core(A, B, C, N, 0, _).

hanoi_core(A, B, C, N, K1, K2) :-
    (N < 2 ->
     K2 is K1 + 1,
     writef('[%d] Move topmost disc from tower %w to tower %w.', [K2, A, C]),
     nl
     ;
     N1 is N - 1,
     hanoi_core(A, C, B, N1, K1, K3),
     hanoi_core(A, B, C, 1, K3, K4),
     hanoi_core(B, A, C, N1, K4, K2)).


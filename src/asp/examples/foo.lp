n(1).
n(3).
n(5).
n(10).
n(4).

n_elem(N_Elem) :- N_Elem=#count{X : n(X)}.

{scelta(A, B)}1 :- n(A), n(B), A<B, not not_scelta(A,B).
not_scelta(A,B) :- scelta(A,B), scelta(A,C), B!=C.
not_scelta(A,B) :- scelta(A,B), scelta(C,B), A!=C.

N-1{n(A) : scelta(A,B) }N-1 :- n_elem(N).

%not_scelta(A,B) :- Count=#count{scelta(A,C) : n(C), C>B}, scelta(A,B), Count>0.
%coppie(A,B, Count) :- Count=#count{scelta(A,C) : n(C), C>B}, scelta(A,B), Count>0.

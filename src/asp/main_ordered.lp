1{
	insegnamento(I) : insegna(docente(Matricola), insegnamento(I), corso(Corso))
} :-
	garante(docente(Matricola), corso(Corso)).

% numero garanti
M{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola)
}N :-
	min_garanti(M, corso(Corso)),
  max_garanti(N, corso(Corso)),
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(Categoria)).

% almeno X garanti a tempo indeterminato
X{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola),
	insegna(docente(Matricola), insegnamento(Insegnamento), corso(Corso)),
	indeterminato(docente(Matricola))
} :-
	min_indeterminato(X, corso(Corso)),
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(Categoria)).

% al più X garanti ricercatore
{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola),
	insegna(docente(Matricola), insegnamento(Insegnamento), corso(Corso)),
	ricercatore(docente(Matricola))
}X :-
	max_ricercatori(X, corso(Corso)),
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(Categoria)).

% al più X garanti a contratto
{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola),
	insegna(docente(Matricola), insegnamento(Insegnamento), corso(Corso)),
	contratto(docente(Matricola))
}X :-
	max_contratto(X, corso(Corso)),
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(Categoria)).

% un docente è scelto al più una volta
1{
	garante(docente(Matricola), corso(Corso2)) :
	corso(Corso2),
	afferisce(corso(Corso2), categoria_corso(Categoria2))
}1 :-
	garante(docente(Matricola), corso(Corso1)),
	afferisce(corso(Corso1), categoria_corso(Categoria1)).

R{
	
	garante(docente(Matricola), corso(Corso)) :
	afferisce(docente(Matricola), settore(Settore)),
	di_riferimento(settore(Settore), corso(Corso))
} :-
	corso(Corso),
	min_riferimento(R, corso(Corso)).


{precede(docente(Matricola1), docente(Matricola2))}1 :-
	garante(docente(Matricola1), corso(Corso)),
	garante(docente(Matricola2), corso(Corso)),
	not not_precede(docente(Matricola1), docente(Matricola2)),
	Matricola1<Matricola2.

not_precede(docente(Matricola), docente(Matricola2)) :-
	precede(docente(Matricola), docente(Matricola1)),
	precede(docente(Matricola), docente(Matricola2)),
	Matricola1<Matricola2.
not_precede(docente(Matricola2), docente(Matricola)) :-
	precede(docente(Matricola1), docente(Matricola)),
	precede(docente(Matricola2), docente(Matricola)),
	Matricola1>Matricola2.

Min-1{docente(Matricola1) : precede(docente(Matricola1), docente(Matricola2))}Min-1 :- min_garanti(Min, corso(Corso)).


primo_garante(docente(Matricola), corso(Corso)) :-
	Matricola=#min{X : docente(X),garante(docente(X), corso(Corso))},
	corso(Corso).
ultimo_garante(docente(Matricola), corso(Corso)) :-
	Matricola=#max{X : docente(X),garante(docente(X), corso(Corso))},
	corso(Corso).


garanti_per_corso(corso(Corso), 1, l(Succ, l(Matricola) ) ) :-
	corso(Corso),
	precede(docente(Matricola), docente(Succ)),
	primo_garante(docente(Matricola), corso(Corso)).

garanti_per_corso(corso(Corso), Lunghezza+1, l(Succ, l(Prec, Resto) ) ) :-
	corso(Corso),
	precede(docente(Prec), docente(Succ)),
	garanti_per_corso(corso(Corso), Lunghezza, l(Prec, Resto)),
	max_garanti(Max, corso(Corso)),
	Lunghezza<Max.

:- 
	garanti_per_corso(corso(Corso), L, _),
	max_garanti(Max, corso(Corso)),
	L!=Max.

#show garanti_per_corso/3.


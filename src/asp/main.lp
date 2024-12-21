% se garante, allora insegna almeno una materia in quel corso
1{
	insegnamento(I) : insegna(docente(Matricola), insegnamento(I), corso(Corso))
} :-
	garante(docente(Matricola), corso(Corso)).

scelta(docente(Matricola), corso(Corso)) :-
	docente(Matricola),
	insegna(docente(Matricola), insegnamento(_), corso(Corso)).

% numero garanti
M{
	garante(docente(Matricola), corso(Corso)) :
	scelta(docente(Matricola), corso(Corso))
}N :-
	min_garanti(M, corso(Corso)),
  max_garanti(N, corso(Corso)),
	corso(Corso).

% un docente è scelto al più una volta
0{
	garante(docente(Matricola), corso(Corso2)) :
	garante(docente(Matricola), corso(Corso2)),
	Corso1!=Corso2
}0 :-
	garante(docente(Matricola), corso(Corso1)).

% almeno X garanti a tempo indeterminato
X{
	garante(docente(Matricola), corso(Corso)) :
	garante(docente(Matricola), corso(Corso)),
	indeterminato(docente(Matricola))
}M :-
	min_indeterminato(X, corso(Corso)),
	max_garanti(M, corso(Corso)),
	corso(Corso).

% al più X garanti ricercatore
{
	garante(docente(Matricola), corso(Corso)) :
	garante(docente(Matricola), corso(Corso)),
	ricercatore(docente(Matricola))
}X :-
	max_ricercatori(X, corso(Corso)),
	corso(Corso).

% al più X garanti a contratto
{
	garante(docente(Matricola), corso(Corso)) :
	garante(docente(Matricola), corso(Corso)),
	contratto(docente(Matricola))
}X :-
	max_contratto(X, corso(Corso)),
	corso(Corso).

R{
	garante(docente(Matricola), corso(Corso)) :
	garante(docente(Matricola), corso(Corso)),
	afferisce(docente(Matricola), settore(Settore)),
	di_riferimento(settore(Settore), corso(Corso))
} :-
	corso(Corso),
	min_riferimento(R, corso(Corso)).

#show garante/2.
#show scelta/2.

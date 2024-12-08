% numero garanti per laurea triennale
9{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola)
}11 :-
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(l)).

% almeno X garanti a tempo indeterminato
5{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola),
	afferisce(docente(Matricola), settore(Settore)),
	insegna(docente(Matricola), insegnamento(Insegnamento), corso(Corso)),
	di_riferimento(settore(Settore), corso(Corso)),
	indeterminato(docente(Matricola))
} :-
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(l)).

% al più X garanti ricercatore
{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola),
	afferisce(docente(Matricola), settore(Settore)),
	insegna(docente(Matricola), insegnamento(Insegnamento), corso(Corso)),
	di_riferimento(settore(Settore), corso(Corso)),
	ricercatore(docente(Matricola))
}4 :-
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(l)).

% al più X garanti a contratto
{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola),
	afferisce(docente(Matricola), settore(Settore)),
	insegna(docente(Matricola), insegnamento(Insegnamento), corso(Corso)),
	di_riferimento(settore(Settore), corso(Corso)),
	contratto(docente(Matricola))
}2 :-
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(l)).

% un docente è garante al più una volta
1{
	garante(docente(Matricola), corso(Corso2)) :
	corso(Corso2),
	afferisce(corso(Corso2), categoria_corso(Categoria2))
}1 :-
	garante(docente(Matricola), corso(Corso1)),
	afferisce(corso(Corso1), categoria_corso(Categoria1)).

%ok(docente(Matricola), corso(Corso), categoria_corso(l)) :- garante(docente(Matricola), corso(Corso)), afferisce(corso(Corso), categoria_corso(l)).

#show garante/2.
%#show ok/3.

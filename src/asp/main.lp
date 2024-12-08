% numero garanti per laurea triennale
9{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola)
}12 :-
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(l)).

% numero garanti per laurea magistrale
6{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola)
}9 :-
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(lm)).

% numero garanti per laurea magistrale cu 5
15{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola)
}18 :-
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(lm5)).

% numero garanti per laurea magistrale cu 6
18{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola)
}21 :-
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(lm6)).

% numero garanti per LM Scienze Infermieristiche
3{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola)
}6 :-
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(lm6)),
	Corso=5050.

% TODO:identificare tutte le LT professioni sanitarie e 
% LT a orient. professionale

% numero garanti per LM Scienze Infermieristiche
4{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola)
}7 :-
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(lm6)),
	Corso = 5050 ; Corso = 5028 ; Corso = 5010.



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

#show garante/2.
%#show ok/3.

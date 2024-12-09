% parametri per lauree triennali
min_garanti(6) :- categoria_corso(l).
max_garanti(12) :- categoria_corso(l).
min_indeterminato(5) :- categoria_corso(l).
max_ricercatori(4) :- categoria_corso(l).
max_contratto(2) :- categoria_corso(l).

%*
:- garante(docente(Matricola), corso(Corso)), 
	not insegna(docente(Matricola), insegnamento(I), corso(Corso)),
	insegnamento(I).
*%

%:- garante(docente(Matricola), corso(Corso)), not insegna(docente(Matricola), insegnamento(_), corso(Corso)).
1{
	insegnamento(I) : insegna(docente(Matricola), insegnamento(I), corso(Corso))
} :-
	garante(docente(Matricola), corso(Corso)).

% numero garanti per laurea triennale
M{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola)
}N :-
	min_garanti(M),
    max_garanti(N),
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(l)).

%*
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
*%


% almeno X garanti a tempo indeterminato
X{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola),
	insegna(docente(Matricola), insegnamento(Insegnamento), corso(Corso)),
	indeterminato(docente(Matricola))
} :-
	min_indeterminato(X),
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(l)).

% al più X garanti ricercatore
{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola),
	insegna(docente(Matricola), insegnamento(Insegnamento), corso(Corso)),
	ricercatore(docente(Matricola))
}X :-
	max_ricercatori(X),
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(l)).

% al più X garanti a contratto
{
	garante(docente(Matricola), corso(Corso)) :
	docente(Matricola),
	insegna(docente(Matricola), insegnamento(Insegnamento), corso(Corso)),
	contratto(docente(Matricola))
}X :-
	max_contratto(X),
	corso(Corso),
	afferisce(corso(Corso), categoria_corso(l)).

% un docente è scelto al più una volta
1{
	garante(docente(Matricola), corso(Corso2)) :
	corso(Corso2),
	afferisce(corso(Corso2), categoria_corso(Categoria2))
}1 :-
	garante(docente(Matricola), corso(Corso1)),
	afferisce(corso(Corso1), categoria_corso(Categoria1)).

#show garante/2.
#show insegna/3.
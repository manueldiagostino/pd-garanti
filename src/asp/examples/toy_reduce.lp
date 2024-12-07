settore(inf).
settore(mat).
settore(null).

docente(1..10).

afferisce(docente(1), settore(inf)).
afferisce(docente(2), settore(inf)).
afferisce(docente(3), settore(inf)).
afferisce(docente(4), settore(inf)).
afferisce(docente(5), settore(mat)).
afferisce(docente(6), settore(mat)).
afferisce(docente(7), settore(mat)).
afferisce(docente(8), settore(inf)).
afferisce(docente(9), settore(inf)).
afferisce(docente(10), settore(null)).

indeterminato(docente(1)).
indeterminato(docente(2)).
indeterminato(docente(3)).
indeterminato(docente(4)).
indeterminato(docente(5)).
indeterminato(docente(6)).

ricercatore(docente(7)).
ricercatore(docente(8)).
ricercatore(docente(9)).

contratto(docente(10)).


categoria_corso(l).
categoria_corso(lm).
categoria_corso(lm6).
categoria_corso(lm5).

corso_di_studio(1). % L Inf
corso_di_studio(2). % L Mat
afferisce(corso_di_studio(1), categoria_corso(l)).
afferisce(corso_di_studio(2), categoria_corso(l)).

insegnamento(1..10).

afferisce(insegnamento(1), settore(inf)).
afferisce(insegnamento(2), settore(inf)).
afferisce(insegnamento(3), settore(inf)).
afferisce(insegnamento(4), settore(inf)).
afferisce(insegnamento(5), settore(inf)).
afferisce(insegnamento(6), settore(inf)).
afferisce(insegnamento(7), settore(inf)).
afferisce(insegnamento(8), settore(mat)).
afferisce(insegnamento(9), settore(mat)).
afferisce(insegnamento(10), settore(mat)).


di_riferimento(settore(inf), corso_di_studio(1)).
di_riferimento(settore(mat), corso_di_studio(1)).
di_riferimento(settore(inf), corso_di_studio(2)).
di_riferimento(settore(mat), corso_di_studio(2)).

insegna(docente(1), insegnamento(1), corso_di_studio(1)).
insegna(docente(2), insegnamento(2), corso_di_studio(1)).
insegna(docente(3), insegnamento(3), corso_di_studio(1)).
insegna(docente(4), insegnamento(4), corso_di_studio(1)).
insegna(docente(5), insegnamento(5), corso_di_studio(1)).
insegna(docente(6), insegnamento(6), corso_di_studio(1)).
insegna(docente(7), insegnamento(7), corso_di_studio(1)).
insegna(docente(8), insegnamento(8), corso_di_studio(1)).
insegna(docente(9), insegnamento(9), corso_di_studio(1)).
insegna(docente(10), insegnamento(10), corso_di_studio(1)).

insegna(docente(1), insegnamento(1), corso_di_studio(2)).
insegna(docente(2), insegnamento(2), corso_di_studio(2)).
insegna(docente(3), insegnamento(3), corso_di_studio(2)).
insegna(docente(4), insegnamento(4), corso_di_studio(2)).
insegna(docente(5), insegnamento(5), corso_di_studio(2)).
insegna(docente(6), insegnamento(6), corso_di_studio(2)).
insegna(docente(7), insegnamento(7), corso_di_studio(2)).
insegna(docente(8), insegnamento(8), corso_di_studio(2)).
insegna(docente(9), insegnamento(9), corso_di_studio(2)).
insegna(docente(10), insegnamento(10), corso_di_studio(2)).


4{
	garante(docente(Matricola), corso_di_studio(Corso)) :
	docente(Matricola)
} :-
	corso_di_studio(Corso),
	afferisce(corso_di_studio(Corso), categoria_corso(l)).

% almeno X garanti a tempo indeterminato
3{
	garante(docente(Matricola), corso_di_studio(Corso)) :
	docente(Matricola),
	afferisce(docente(Matricola), settore(Settore)),
	insegna(docente(Matricola), insegnamento(Insegnamento), corso_di_studio(Corso)),
	di_riferimento(settore(Settore), corso_di_studio(Corso)),
	indeterminato(docente(Matricola))
} :-
	corso_di_studio(Corso),
	afferisce(corso_di_studio(Corso), categoria_corso(l)).

% al più X garanti ricercatore
{
	garante(docente(Matricola), corso_di_studio(Corso)) :
	docente(Matricola),
	afferisce(docente(Matricola), settore(Settore)),
	insegna(docente(Matricola), insegnamento(Insegnamento), corso_di_studio(Corso)),
	di_riferimento(settore(Settore), corso_di_studio(Corso)),
	ricercatore(docente(Matricola))
}1 :-
	corso_di_studio(Corso),
	afferisce(corso_di_studio(Corso), categoria_corso(l)).

% un docente è garante al più una volta
1{
	garante(docente(Matricola), corso_di_studio(Corso2)) :
	corso_di_studio(Corso2),
	afferisce(corso_di_studio(Corso2), categoria_corso(Categoria2))
}1 :-
	garante(docente(Matricola), corso_di_studio(Corso1)),
	afferisce(corso_di_studio(Corso1), categoria_corso(Categoria1)).

#show garante/2.
%#show afferisce/2.
%#show corso_di_studio/1.


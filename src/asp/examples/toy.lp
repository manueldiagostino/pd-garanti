settore(1..5).

docente(1, settore(inf)).
docente(2, settore(inf)).
docente(3, settore(inf)).
docente(4, settore(inf)).
docente(5, settore(mat)).
docente(6, settore(mat)).
docente(7, settore(mat)).
docente(8, settore(inf)).
docente(9, settore(inf)).
docente(10, settore(null)).


indeterminato(docente(1, settore(inf))).
indeterminato(docente(2, settore(inf))).
indeterminato(docente(3, settore(inf))).
indeterminato(docente(4, settore(inf))).
indeterminato(docente(5, settore(mat))).
indeterminato(docente(6, settore(mat))).
ricercatore(docente(7, settore(mat))).
ricercatore(docente(8, settore(inf))).
ricercatore(docente(9, settore(inf))).
contratto(docente(10, settore(null))).


categoria_corso(l).
categoria_corso(lm).
categoria_corso(lm6).
categoria_corso(lm5).

corso_di_studio(1, categoria_corso(l)). % L Inf
corso_di_studio(2, categoria_corso(l)). % L Mat


insegnamento(1, settore(inf)).
insegnamento(2, settore(inf)).
insegnamento(3, settore(inf)).
insegnamento(4, settore(inf)).
insegnamento(5, settore(inf)).
insegnamento(6, settore(inf)).
insegnamento(7, settore(inf)).
insegnamento(8, settore(mat)).
insegnamento(9, settore(mat)).
insegnamento(10, settore(mat)).


di_riferimento(settore(inf), corso_di_studio(1, categoria_corso(l))).
di_riferimento(settore(mat), corso_di_studio(1, categoria_corso(l))).

di_riferimento(settore(mat), corso_di_studio(3, categoria_corso(lm))).
di_riferimento(settore(inf), corso_di_studio(2, categoria_corso(l))).
di_riferimento(settore(mat), corso_di_studio(2, categoria_corso(l))).

insegna(docente(1, settore(inf)), insegnamento(1, settore(inf)), corso_di_studio(1, categoria_corso(l))).
insegna(docente(2, settore(inf)), insegnamento(2, settore(inf)), corso_di_studio(1, categoria_corso(l))).
insegna(docente(3, settore(inf)), insegnamento(3, settore(inf)), corso_di_studio(1, categoria_corso(l))).
insegna(docente(4, settore(inf)), insegnamento(4, settore(inf)), corso_di_studio(1, categoria_corso(l))).
insegna(docente(5, settore(mat)), insegnamento(5, settore(inf)), corso_di_studio(1, categoria_corso(l))).
insegna(docente(6, settore(mat)), insegnamento(6, settore(inf)), corso_di_studio(1, categoria_corso(l))).
insegna(docente(7, settore(mat)), insegnamento(7, settore(inf)), corso_di_studio(1, categoria_corso(l))).
insegna(docente(8, settore(inf)), insegnamento(8, settore(mat)), corso_di_studio(1, categoria_corso(l))).
insegna(docente(9, settore(inf)), insegnamento(9, settore(mat)), corso_di_studio(1, categoria_corso(l))).
insegna(docente(10, settore(null)), insegnamento(10, settore(mat)), corso_di_studio(1, categoria_corso(l))).

insegna(docente(1, settore(inf)), insegnamento(1, settore(inf)), corso_di_studio(2, categoria_corso(l))).
insegna(docente(2, settore(inf)), insegnamento(2, settore(inf)), corso_di_studio(2, categoria_corso(l))).
insegna(docente(3, settore(inf)), insegnamento(3, settore(inf)), corso_di_studio(2, categoria_corso(l))).
insegna(docente(4, settore(inf)), insegnamento(4, settore(inf)), corso_di_studio(2, categoria_corso(l))).
insegna(docente(5, settore(mat)), insegnamento(5, settore(inf)), corso_di_studio(2, categoria_corso(l))).
insegna(docente(6, settore(mat)), insegnamento(6, settore(inf)), corso_di_studio(2, categoria_corso(l))).
insegna(docente(7, settore(mat)), insegnamento(7, settore(inf)), corso_di_studio(2, categoria_corso(l))).
insegna(docente(8, settore(inf)), insegnamento(8, settore(mat)), corso_di_studio(2, categoria_corso(l))).
insegna(docente(9, settore(inf)), insegnamento(9, settore(mat)), corso_di_studio(2, categoria_corso(l))).
insegna(docente(10, settore(null)), insegnamento(10, settore(mat)), corso_di_studio(2, categoria_corso(l))).

4{
	garante(docente(Matricola, settore(Settore)), corso_di_studio(Corso, categoria_corso(Categoria_corso))) :
	docente(Matricola, settore(Settore))
} :- corso_di_studio(Corso, categoria_corso(Categoria_corso)), Categoria_corso = l.

% almeno 4 garanti a tempo indeterminato
3{
	garante(docente(Matricola, settore(Settore)), corso_di_studio(Corso, categoria_corso(Categoria_corso))) :
	docente(Matricola, settore(Settore)),
	insegna(docente(Matricola, settore(Settore)), insegnamento(Insegnamento, settore(Settore_insegnamento)), corso_di_studio(Corso, categoria_corso(Categoria_corso))),
	di_riferimento(settore(Settore), corso_di_studio(Corso, categoria_corso(Categoria_corso))),
	indeterminato(docente(Matricola, settore(Settore)))
} :- corso_di_studio(Corso, categoria_corso(Categoria_corso)), Categoria_corso = l.


% al più 1 garante ricercatore
{
	garante(docente(Matricola, settore(Settore)), corso_di_studio(Corso, categoria_corso(Categoria_corso))) :
	docente(Matricola, settore(Settore)),
	insegna(docente(Matricola, settore(Settore)), insegnamento(Insegnamento, settore(Settore_insegnamento)), corso_di_studio(Corso, categoria_corso(Categoria_corso))),
	di_riferimento(settore(Settore), corso_di_studio(Corso, categoria_corso(Categoria_corso))),
	ricercatore(docente(Matricola, settore(Settore)))
}1 :- corso_di_studio(Corso, categoria_corso(Categoria_corso)), Categoria_corso = l.

% un docente è garante al più una volta
1{
	garante(docente(Matricola, settore(Settore)), corso_di_studio(Corso2, categoria_corso(Categoria_corso2))) :
	corso_di_studio(Corso2, categoria_corso(Categoria_corso2))
}1 :- garante(docente(Matricola, settore(Settore)), corso_di_studio(Corso1,
	categoria_corso(Categoria_corso1))).

#show garante/2.

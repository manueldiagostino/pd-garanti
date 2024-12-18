#minimize{
	-1@4,
	Matricola :
		garante(docente(Matricola), corso(Corso)),
		presidente(docente(Matricola), corso(Corso))
}.

%*
#minimize{
	-1@1,
	Matricola :
		garante(docente(Matricola), corso(Corso)),
		ricercatore(docente(Matricola))
}.
*%

#minimize{
	-1@2,
	Matricola :
		garante(docente(Matricola), corso(Corso)),
		indeterminato(docente(Matricola))
}.

ideale(corso(Corso)) :-
	N=#count{
		docente(Matricola) :
		garante(docente(Matricola), corso(Corso)),
		indeterminato(docente(Matricola))
	},
	corso(Corso),
	max_garanti(Max, corso(Corso)),
	N=Max.

#minimize{
	-1@3,
	ideale(corso(Corso)) :
	ideale(corso(Corso))
}.

non_ideale(corso(Corso)) :-
	N=#count{
		docente(Matricola) :
		garante(docente(Matricola), corso(Corso)),
		indeterminato(docente(Matricola))
	},
	corso(Corso),
	max_garanti(Max, corso(Corso)),
	N<Max.

%*
non_ideale(corso(Corso)) :-
	N=#count{
		docente(Matricola) :
		garante(docente(Matricola), corso(Corso)),
		ricercatore(docente(Matricola))
	},
	corso(Corso),
	max_garanti(Max, corso(Corso)),
	N>0.

non_ideale(corso(Corso)) :-
	N=#count{
		docente(Matricola) :
		garante(docente(Matricola), corso(Corso)),
		contratto(docente(Matricola))
	},
	corso(Corso),
	max_garanti(Max, corso(Corso)),
	N>0.
*%

#minimize{
	1@1,
	non_ideale(corso(Corso)) :
	non_ideale(corso(Corso))
}.

#show ideale/1.


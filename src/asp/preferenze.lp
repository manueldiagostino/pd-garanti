#minimize{
	-1@1,
	Matricola :
		garante(docente(Matricola), corso(Corso)),
		presidente(docente(Matricola), corso(Corso))
}.

#minimize{
	-1@2,
	Matricola :
		garante(docente(Matricola), corso(Corso)),
		ricercatore(docente(Matricola))
}.

#minimize{
	-1@3,
	Matricola :
		garante(docente(Matricola), corso(Corso)),
		indeterminato(docente(Matricola))
}.


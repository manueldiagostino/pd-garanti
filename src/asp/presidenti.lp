#minimize{
	-1@1,
	Matricola :
		garante(docente(Matricola), corso(Corso)),
		presidente(docente(Matricola), corso(Corso))
}.

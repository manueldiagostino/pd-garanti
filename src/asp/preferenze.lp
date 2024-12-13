#minimize{
	-1@1,
	Matricola :
		garante(docente(Matricola), corso(Corso)),
		presidente(docente(Matricola), corso(Corso))
}.

#minimize{
	-1@3,
	Matricola :
		garante(docente(Matricola), corso(Corso)),
		afferisce(docente(Matricola), settore(Settore)),
		di_riferimento(settore(Settore), corso(Corso)),
		indeterminato(docente(Docente))
}.

#minimize{
	-1@2,
	Matricola :
		garante(docente(Matricola), corso(Corso)),
		afferisce(docente(Matricola), settore(Settore)),
		di_riferimento(settore(Settore), corso(Corso)),
		ricercatore(docente(Docente))
}.

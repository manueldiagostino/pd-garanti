presidente(docente(6625), corso(5069)). % Dal Palu' A., LM Info

#minimize{
	-1@1,
	Matricola :
		garante(docente(Matricola), corso(Corso)),
		presidente(docente(Matricola), corso(Corso))
}.

settore(inf).
settore(mat).
settore(ing_inf).

categoria(l).
categoria(lm).
categoria(lmcu5).
categoria(lmcu6).

corso(1, categoria(l)).
corso(2, categoria(l)).
corso(3, categoria(lm)).

insegnamento(1, settore(inf)).
insegnamento(2, settore(inf)).
insegnamento(3, settore(inf)).
insegnamento(4, settore(mat)).
insegnamento(5, settore(mat)).
insegnamento(6, settore(mat)).

% LT info
di_riferimento(settore(inf), corso(1, categoria(l))).
di_riferimento(settore(mat), corso(1, categoria(l))).

di_riferimento(settore(mat), corso(3, categoria(lm))).
di_riferimento(settore(ing_inf), corso(2, categoria(l))).
di_riferimento(settore(mat), corso(2, categoria(l))).

docente(33657, settore(inf)).
docente(5145, settore(inf)).
docente(204741, settore(inf)).
docente(32990, settore(inf)).
docente(34181, settore(inf)).
docente(6625, settore(inf)).
docente(13027, settore(inf)).
docente(36662, settore(inf)).
docente(5602, settore(inf)).

docente(10285, settore(mat)).
docente(15988, settore(mat)).
docente(4609, settore(mat)).
docente(26131, settore(mat)).

insegna(docente(33657, settore(inf)), insegnamento(1, settore(inf)), corso(1, categoria(l))).
insegna(docente(32990, settore(inf)), insegnamento(2, settore(inf)), corso(1, categoria(l))).
insegna(docente(15988, settore(inf)), insegnamento(3, settore(inf)), corso(1, categoria(l))).
insegna(docente(26131, settore(mat)), insegnamento(4, settore(mat)), corso(2, categoria(l))).
insegna(docente(26131, settore(mat)), insegnamento(4, settore(mat)), corso(1, categoria(l))).

2{ garante(docente(X, settore(Y)), corso(Z, categoria(W))) :
    insegna(docente(X, settore(Y)), insegnamento(A, settore(B)), corso(Z, categoria(W))), 
    di_riferimento(settore(Y), corso(Z, categoria(W))) }2.

#show garante/2.
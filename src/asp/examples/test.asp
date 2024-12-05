corso(1..3).

settore(1..4).

insegnamento(1, settore(1)).
insegnamento(2, settore(1)).
insegnamento(3, settore(1)).
insegnamento(4, settore(1)).
insegnamento(5, settore(2)).
insegnamento(6, settore(2)).

% LT info
di_riferimento(settore(1), corso(1)).
di_riferimento(settore(2), corso(1)).

di_riferimento(settore(1), corso(3)).
di_riferimento(settore(3), corso(2)).

docente(33657, settore(1)).
docente(5145, settore(1)).
docente(204741, settore(1)).
docente(32990, settore(1)).
docente(34181, settore(1)).
docente(6625, settore(1)).
docente(13027, settore(1)).
docente(36662, settore(1)).
docente(5602, settore(1)).

docente(10285, settore(2)).
docente(15988, settore(2)).
docente(4609, settore(2)).
docente(26131, settore(2)).

insegna(docente(33657, settore(1)), insegnamento(1, settore(1)), corso(1)).
insegna(docente(32990, settore(1)), insegnamento(2, settore(1)), corso(1)).
insegna(docente(15988, settore(2)), insegnamento(3, settore(1)), corso(1)).
insegna(docente(26131, settore(2)), insegnamento(4, settore(1)), corso(2)).

2{ garante(docente(X, settore(Y)), corso(Z)) : 
    insegna(docente(X, settore(Y)), insegnamento(A, settore(B)), corso(Z)), 
    di_riferimento(settore(B), corso(Z)) }.

#show garante/2.
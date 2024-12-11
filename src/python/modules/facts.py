import os
import argparse

from .csv_loader import *  # Importa il modulo per caricare e pulire i dati


def docente(fatti_docenti, riga, mappa_ssd, mappa_ssd_termine):
    valori = []
    valore = riga['Matricola']
    if pd.isna(valore):
        return None

    valore = int(valore)
    valori.append(valore)

    # Leggo Cod. Settore Docente
    valore = riga['Cod. Settore Docente']
    if pd.isna(valore) and (valori[0] not in fatti_docenti):
        # default per valori null (settore non valorizzato)
        valore = 'NULL/'
    # ho già valorizzato il settore del docente con un valore non null
    elif pd.isna(valore) and valori[0] in fatti_docenti:
        return None

    # `valore` un SSD 2024, converto direttamente in SSD2015
    if (valore in mappa_ssd):
        nuova_chiave = mappa_ssd[valore]
        valore = mappa_ssd_termine[nuova_chiave.split('/')[0]]
    # altrimenti, rimuovo da '/' in poi e considero il termine
    # corrispondente al SSD
    else:
        valore = valore.split('/')[0]
        valore = mappa_ssd_termine[valore]

    valori.append(valore)

    fatto = f"docente({valori[0]}). afferisce(docente({
        valori[0]}), settore({valori[1]}))."
    fatti_docenti[valori[0]] = fatto

    return fatto


def categoria_corso(fatti_categorie, riga):
    valore = riga['Cod. Tipo Corso']

    if pd.isna(valore):
        return None
    if valore in fatti_categorie:
        return None

    fatto = f"categoria_corso({normalizza_nome(valore)})."
    fatti_categorie[valore] = fatto

    return fatto


def corso(fatti_corsi, riga):
    valori = []
    valore = riga['Cod. Corso di Studio']
    if pd.isna(valore):
        return None

    valore = int(valore)
    valori.append(valore)

    # Leggo Cod. Settore Docente
    valore = riga['Cod. Tipo Corso']
    if pd.isna(valore):
        return None

    valori.append(normalizza_nome(valore))

    fatto = f"corso({valori[0]}). afferisce(corso({
        valori[0]}), categoria_corso({valori[1]}))."
    fatti_corsi[valori[0]] = fatto

    return fatto


def docente_indeterminato_ricercatore(fatti_docenti_tipo_contratto, riga):
    valori = []
    valore = riga['Matricola']
    if pd.isna(valore):
        return None

    valore = int(valore)
    if (valore in fatti_docenti_tipo_contratto and ('contratto' not in fatti_docenti_tipo_contratto[valore])):
        return None

    valori.append(valore)

    valore = riga['Fascia']
    if pd.isna(valore):
        return None

    if 'ricercatore' in normalizza_nome(valore):
        valori.append('ricercatore')
    else:
        valori.append('indeterminato')

    fatto = f"{valori[1]}(docente({valori[0]}))."
    fatti_docenti_tipo_contratto[valori[0]] = fatto

    return fatto


def docente_contratto(fatti_docenti_tipo_contratto, riga, fatti_docenti):
    valore = riga['Cod. Settore Docente']

    # TODO: aggiungere qui 'ricercatore/indeterminato
    if not pd.isna(valore):
        return None

    valore = riga['Matricola']
    if pd.isna(valore):
        return None
    valore = int(valore)

    if valore in fatti_docenti_tipo_contratto:
        return None

    fatto = f"contratto(docente({valore}))."
    fatti_docenti_tipo_contratto[valore] = fatto

    return fatto


def insegnamento(fatti_insegnamenti, riga):
    valore = riga['Cod. Att. Form.']
    if pd.isna(valore):
        return None

    valore = f"af_{valore}"
    fatto = f"insegnamento({valore})."
    fatti_insegnamenti[valore] = fatto

    return fatto


def insegna(fatti_insegna, riga):
    matricola = riga['Matricola']
    if pd.isna(matricola):
        return None
    matricola = int(matricola)

    att_formativa = riga['Cod. Att. Form.']
    if pd.isna(att_formativa):
        return None
    att_formativa = f"af_{att_formativa}"

    corso = riga['Cod. Corso di Studio']
    if pd.isna(corso):
        return None
    corso = int(corso)

    fatto = f"insegna(docente({matricola}), insegnamento({
        att_formativa}), corso({corso}))."
    fatti_insegna.add(fatto)

    return fatto


def normalizza_settore(settore, mappa_ssd, mappa_ssd_termine):
    if pd.isna(settore):
        # default per valori null (settore non valorizzato)
        settore = 'NULL/'

    # `settore` un SSD 2024, converto direttamente in SSD2015
    if (settore in mappa_ssd):
        nuova_chiave = mappa_ssd[settore]
        settore = mappa_ssd_termine[nuova_chiave.split('/')[0]]
    # altrimenti, rimuovo da '/' in poi e considero il termine
    # corrispondente al SSD
    else:
        settore = settore.split('/')[0]
        settore = mappa_ssd_termine[settore]

    return settore


def settori_di_riferimento(fatti_settori_di_riferimento, riga, mappa_ssd, mappa_ssd_termine):
    af = riga['Cod. Att. Form.']
    if pd.isna(af):
        return None
    af = f"af_{af}"

    corso = riga['Cod. Corso di Studio']
    if pd.isna(corso):
        return None
    corso = int(corso)

    settore = riga['Cod. Settore Docente']
    settore = normalizza_settore(settore, mappa_ssd, mappa_ssd_termine)
    if (settore == 'null'):
        return None

    fatto = f"di_riferimento(settore({settore}), corso({corso}))."
    fatti_settori_di_riferimento.add(fatto)

    return fatto


def settori(fatti_settori, mappa_ssd_termine):
    for chiave, termine in mappa_ssd_termine.items():
        fatti_settori[chiave] = f"settore({termine})."

import csv_loader  # Importa il modulo per caricare e pulire i dati
import os
import argparse


def mappa_settori_nuovi_vecchi(df):
    """
    Genera una mappa dai settori SSD 2024 ai settori SSD 2015 basandosi sul DataFrame fornito.

    :param df: DataFrame contenente le colonne 'SSD 2015' e 'SSD 2024'.
    :return: Dizionario con chiavi dai valori unici di 'SSD 2015' e valori corrispondenti di 'SSD 2024'.
    """
    mappa = {}
    for _, row in df.iterrows():
        ssd_2015 = row["SSD 2015"]
        ssd_2024 = row["SSD 2024"]
        # Evita valori mancanti
        if csv_loader.pd.notna(ssd_2015) and csv_loader.pd.notna(ssd_2024):
            mappa[ssd_2024] = ssd_2015
    return mappa


def mappa_settori_termini(mappa_ssd):
    """
    Genera una mappa dove le chiavi sono i codici SSD 2015 senza il suffisso
    dopo '/' e i valori sono le stesse stringhe in formato modificato:
    minuscolo e con underscore al posto di trattini o spazi.

    :param mappa_ssd: Dizionario esistente con chiavi e valori SSD (ad esempio: {SSD 2024: SSD 2015}).
    :return: Dizionario con chiavi come codici SSD 2015 (troncati) e valori formattati.
    """
    mappa_progressiva = {}

    # Itera sui valori unici di SSD 2015
    for ssd_2015 in set(mappa_ssd.values()):
        if isinstance(ssd_2015, str):
            # Rimuove tutto ciò che viene dopo '/'
            codice_troncato = ssd_2015.split('/')[0]
            # Trasforma il codice in minuscolo e sostituisce spazi o trattini con underscore
            codice_modificato = csv_loader.normalizza_nome(codice_troncato)
        else:
            # Gestisce valori non stringa
            codice_troncato = codice_modificato = ssd_2015

        if codice_troncato not in mappa_progressiva:  # Evita duplicati
            mappa_progressiva[codice_troncato] = codice_modificato

    # Aggiungi un valore predefinito per NULL
    mappa_progressiva['NULL'] = 'null'

    return mappa_progressiva


def genera_fatti_settori(file_output, mappa_ssd):
    """
    Genera i fatti a partire dalla mappa `mappa_ssd` e li scrive nel file di output.

    :param df: DataFrame (non utilizzato direttamente, ma mantenuto per uniformità con altri metodi).
    :param file_output: Percorso del file di output.
    :param mappa_ssd: Dizionario con chiavi come codici SSD e valori come termini rappresentanti i settori.
    """
    nome_fatto = 'settore'

    try:
        # Scrivi i fatti nel file di output
        with open(file_output, 'w', encoding='utf-8') as f:
            for ssd, termine in mappa_ssd.items():
                # Genera il fatto ASP
                fatto = f"{nome_fatto}({termine})."
                f.write(fatto + '\n')  # Scrivi il fatto nel file

        print(f"Fatti `{nome_fatto}` scritti con successo in {file_output}")
    except Exception as e:
        print(f"Errore durante la scrittura dei fatti `{nome_fatto}`: {e}")


def docente(fatti_docenti, riga, mappa_ssd, mappa_ssd_termine):
    valori = []
    valore = riga['Matricola']
    if csv_loader.pd.isna(valore):
        return None

    valore = int(valore)
    valori.append(valore)

    # Leggo Cod. Settore Docente
    valore = riga['Cod. Settore Docente']
    if csv_loader.pd.isna(valore) and (valori[0] not in fatti_docenti):
        # default per valori null (settore non valorizzato)
        valore = 'NULL/'
    # ho già valorizzato il settore del docente con un valore non null
    elif csv_loader.pd.isna(valore) and valori[0] in fatti_docenti:
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

    if csv_loader.pd.isna(valore):
        return None
    if valore in fatti_categorie:
        return None

    fatto = f"categoria_corso({csv_loader.normalizza_nome(valore)})."
    fatti_categorie[valore] = fatto

    return fatto


def corso(fatti_corsi, riga):
    valori = []
    valore = riga['Cod. Corso di Studio']
    if csv_loader.pd.isna(valore):
        return None

    valore = int(valore)
    valori.append(valore)

    # Leggo Cod. Settore Docente
    valore = riga['Cod. Tipo Corso']
    if csv_loader.pd.isna(valore):
        return None

    valori.append(csv_loader.normalizza_nome(valore))

    fatto = f"corso({valori[0]}). afferisce(corso({
        valori[0]}), categoria_corso({valori[1]}))."
    fatti_corsi[valori[0]] = fatto

    return fatto


def docente_indeterminato_ricercatore(fatti_docenti_tipo_contratto, riga):
    valori = []
    valore = riga['Matricola']
    if csv_loader.pd.isna(valore):
        return None

    valore = int(valore)
    if (valore in fatti_docenti_tipo_contratto and ('contratto' not in fatti_docenti_tipo_contratto[valore])):
        return None

    valori.append(valore)

    valore = riga['Fascia']
    if csv_loader.pd.isna(valore):
        return None

    if 'ricercatore' in csv_loader.normalizza_nome(valore):
        valori.append('ricercatore')
    else:
        valori.append('indeterminato')

    fatto = f"{valori[1]}(docente({valori[0]}))."
    fatti_docenti_tipo_contratto[valori[0]] = fatto

    return fatto


def docente_contratto(fatti_docenti_tipo_contratto, riga, fatti_docenti):
    valore = riga['Cod. Settore Docente']

    # TODO: aggiungere qui 'ricercatore/indeterminato
    if not csv_loader.pd.isna(valore):
        return None

    valore = riga['Matricola']
    if csv_loader.pd.isna(valore):
        return None
    valore = int(valore)

    if valore in fatti_docenti_tipo_contratto:
        return None

    fatto = f"contratto(docente({valore}))."
    fatti_docenti_tipo_contratto[valore] = fatto

    return fatto


def insegnamento(fatti_insegnamenti, riga):
    valore = riga['Cod. Att. Form.']
    if csv_loader.pd.isna(valore):
        return None

    valore = f"af_{valore}"
    fatto = f"insegnamento({valore})."
    fatti_insegnamenti[valore] = fatto

    return fatto


def insegna(fatti_insegna, riga):
    matricola = riga['Matricola']
    if csv_loader.pd.isna(matricola):
        return None
    matricola = int(matricola)

    att_formativa = riga['Cod. Att. Form.']
    if csv_loader.pd.isna(att_formativa):
        return None
    att_formativa = f"af_{att_formativa}"

    corso = riga['Cod. Corso di Studio']
    if csv_loader.pd.isna(corso):
        return None
    corso = int(corso)

    fatto = f"insegna(docente({matricola}), insegnamento({
        att_formativa}), corso({corso}))."
    fatti_insegna.add(fatto)

    return fatto


def normalizza_settore(settore, mappa_ssd, mappa_ssd_termine):
    if csv_loader.pd.isna(settore):
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
    if csv_loader.pd.isna(af):
        return None
    af = f"af_{af}"

    corso = riga['Cod. Corso di Studio']
    if csv_loader.pd.isna(corso):
        return None
    corso = int(corso)

    settore = riga['Cod. Settore Docente']
    settore = normalizza_settore(settore, mappa_ssd, mappa_ssd_termine)
    if (settore == 'null'):
        return None

    fatto = f"di_riferimento(settore({settore}), corso({corso}))."
    fatti_settori_di_riferimento.add(fatto)

    return fatto


def genera_fatti(corsi_da_filtrare, dir_output):
    """Legge il file CSV, genera i fatti per ogni gruppo e li scrive nel file."""

    # Path di output
    # dir_output = '../../src/asp/facts/test_filter'

    # Carica i dati
    file_csv_docenti = '../../input/docenti.csv'
    df = csv_loader.carica_dati_csv(file_csv_docenti)
    if df is None:
        print("Errore nel caricamento dei dati da `docenti.csv`")
        return

    mappa_ssd = mappa_settori_nuovi_vecchi(df)
    mappa_ssd_termine = mappa_settori_termini(mappa_ssd)
    print('Mappa ssd nuovi-vecchi generata')
    genera_fatti_settori(os.path.join(
        dir_output, 'settori.asp'), mappa_ssd_termine)

    fatti_docenti_tipo_contratto = {}
    for _, riga in df.iterrows():
        # Estraggo i docenti ricercatori/tempo indeterminato
        docente_indeterminato_ricercatore(fatti_docenti_tipo_contratto, riga)

    file_csv_coperture = '../../input/coperture2425.csv'
    df = csv_loader.carica_dati_csv(file_csv_coperture)
    if df is None:
        print("Errore nel caricamento dei dati da `coperture2425.csv`")
        return

    fatti_corsi_di_studio = {}
    fatti_categorie_corso = {}
    fatti_docenti = {}
    fatti_insegnamenti = {}
    fatti_insegna = set()
    fatti_settori_di_riferimento = set()
    for _, riga in df.iterrows():
        cod_corso = riga['Cod. Corso di Studio']
        if csv_loader.pd.isna(cod_corso):
            continue
        cod_corso = int(cod_corso)

        # Filtra i corsi
        if corsi_da_filtrare and cod_corso not in corsi_da_filtrare:
            print(f'{cod_corso} escluso')
            continue

        # Estraggo i docenti
        docente(fatti_docenti, riga, mappa_ssd, mappa_ssd_termine)
        # Estraggo le categoria_corso
        categoria_corso(fatti_categorie_corso, riga)
        # Estraggo i corsi
        corso(fatti_corsi_di_studio, riga)
        # Estraggo docenti a contratto
        docente_contratto(fatti_docenti_tipo_contratto, riga, fatti_docenti)
        # Estraggo insegnamenti
        insegnamento(fatti_insegnamenti, riga)
        # Estraggo fatti insegna
        insegna(fatti_insegna, riga)
        # Estraggo i settori di riferimento per i corsi
        settori_di_riferimento(fatti_settori_di_riferimento, riga,
                               mappa_ssd, mappa_ssd_termine)

    file_csv_docenti = '../../input/docenti.csv'
    df = csv_loader.carica_dati_csv(file_csv_docenti)
    if df is None:
        print("Errore nel caricamento dei dati.")
        return

    # Stampo i fatti nei rispettivi file
    file_output = os.path.join(
        dir_output, 'categorie_corso.asp')
    with open(file_output, 'w', encoding='utf-8') as f:
        for fatto in fatti_categorie_corso.values():
            f.write(f"{fatto}\n")
    print(f"Fatti `categoria_corso\\1` scritti in {file_output}")

    file_output = os.path.join(
        dir_output, 'docenti.asp')
    with open(file_output, 'w', encoding='utf-8') as f:
        for fatto in fatti_docenti.values():
            f.write(f"{fatto}\n")
    print(f"Fatti `docente\\1` scritti in {file_output}")

    file_output = os.path.join(
        dir_output, 'corsi_di_studio.asp')
    with open(file_output, 'w', encoding='utf-8') as f:
        for fatto in fatti_corsi_di_studio.values():
            f.write(f"{fatto}\n")
    print(f"Fatti `corso\\1` scritti in {file_output}")

    file_output = os.path.join(
        dir_output, 'contratti_docenti.asp')
    with open(file_output, 'w', encoding='utf-8') as f:
        for fatto in fatti_docenti_tipo_contratto.values():
            f.write(f"{fatto}\n")
    print(f"Fatti `indeterminato\\1`, `ricercatore\\1`, `contratto\\1` scritti in {
        file_output}")

    file_output = os.path.join(
        dir_output, 'insegnamenti.asp')
    with open(file_output, 'w', encoding='utf-8') as f:
        for fatto in fatti_insegnamenti.values():
            f.write(f"{fatto}\n")
        print(f"Fatti `insegnamento\\1` scritti in {
            file_output}")
        for fatto in fatti_insegna:
            f.write(f"{fatto}\n")
        print(f"Fatti `insegna\\3` scritti in {
            file_output}")

        file_output = os.path.join(
            dir_output, 'riferimenti.asp')
    with open(file_output, 'w', encoding='utf-8') as f:
        for fatto in fatti_settori_di_riferimento:
            f.write(f"{fatto}\n")
    print(f"Fatti `di_riferimento\\2` scritti in {file_output}")


# def main():
#     try:
#         # Genera i fatti
#         genera_fatti()
#     except Exception as e:
#         print(f"Errore durante l'elaborazione dati: {e}")

def main():
    parser = argparse.ArgumentParser(description="Genera fatti ASP.")
    parser.add_argument(
        "--filter", type=str, help="Lista di ID di corsi separati da virgola da considerare.", default=None)
    args = parser.parse_args()

    # Ottieni i filtri (se presenti)
    corsi_da_filtrare = set(
        map(int, args.filter.split(','))) if args.filter else None

    try:
        # Genera i fatti
        genera_fatti(corsi_da_filtrare, '../../src/asp/facts/test_filter')
    except Exception as e:
        print(f"Errore durante l'elaborazione dati: {e}")


if __name__ == "__main__":
    main()

import csv_loader  # Importa il modulo per caricare e pulire i dati
import os


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


def genera_fatti_settori(df, file_output, mappa_ssd):
    """
    Genera i fatti a partire dalla mappa `mappa_ssd` e li scrive nel file di output.

    :param df: DataFrame (non utilizzato direttamente, ma mantenuto per uniformità con altri metodi).
    :param file_output: Percorso del file di output.
    :param mappa_ssd: Dizionario con chiavi come codici SSD e valori come terminali rappresentanti i settori.
    """
    nome_fatto = 'settore'

    try:
        # Scrivi i fatti nel file di output
        with open(file_output, 'w', encoding='utf-8') as f:
            for ssd, valore_intero in mappa_ssd.items():
                # Genera il fatto ASP
                fatto = f"{nome_fatto}({valore_intero})."
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

    fatto = f"docente({valori[0]}, settore({valori[1]}))."
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


def corso_di_studio(fatti_corsi, riga):
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

    fatto = f"corso_di_studio({valori[0]}, categoria_corso({valori[1]}))."
    fatti_corsi[valori[0]] = fatto

    return fatto


def docente_indeterminato_ricercatore(fatti_docenti_tipo_contratto, riga, fatti_docenti):
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

    # Docente che non insegna nessuna materia
    if not valori[0] in fatti_docenti:
        return None

    fatto = f"{valori[1]}({fatti_docenti[valori[0]][:-1]})."
    fatti_docenti_tipo_contratto[valori[0]] = fatto

    return fatto


def docente_contratto(fatti_docenti_tipo_contratto, riga, fatti_docenti):
    valore = riga['Cod. Settore Docente']

    if not csv_loader.pd.isna(valore):
        return None

    valore = riga['Matricola']
    if csv_loader.pd.isna(valore):
        return None
    valore = int(valore)

    if valore in fatti_docenti_tipo_contratto:
        return None

    fatto = f"contratto({fatti_docenti[valore][:-1]})."
    fatti_docenti_tipo_contratto[valore] = fatto

    return fatto


def genera_fatti():
    """Legge il file CSV, genera i fatti per ogni gruppo e li scrive nel file."""

    # Path di output
    dir_output = '../../src/asp/facts/'

    # Carica i dati
    file_csv_docenti = '../../input/docenti.csv'
    df = csv_loader.carica_dati_csv(file_csv_docenti)

    if df is None:
        print("Errore nel caricamento dei dati.")
        return

    mappa_ssd = mappa_settori_nuovi_vecchi(df)
    mappa_ssd_termine = mappa_settori_termini(mappa_ssd)

    print('Mappa ssd nuovi-vecchi generata')

    file_csv_coperture = '../../input/coperture2425.csv'
    df = csv_loader.carica_dati_csv(file_csv_coperture)

    if df is None:
        print("Errore nel caricamento dei dati.")
        return

    genera_fatti_settori(df, os.path.join(
        dir_output, 'settori.asp'), mappa_ssd_termine)

    fatti_corsi_di_studio = {}
    fatti_categorie_corso = {}
    fatti_docenti = {}
    fatti_docenti_tipo_contratto = {}

    for _, riga in df.iterrows():
        # Estraggo i docenti
        docente(fatti_docenti, riga, mappa_ssd, mappa_ssd_termine)
        # Estraggo le categoria_corso
        categoria_corso(fatti_categorie_corso, riga)
        # Estraggo i corsi
        corso_di_studio(fatti_corsi_di_studio, riga)
        # Estraggo docenti a contratto
        docente_contratto(fatti_docenti_tipo_contratto, riga, fatti_docenti)

    file_csv_docenti = '../../input/docenti.csv'
    df = csv_loader.carica_dati_csv(file_csv_docenti)
    if df is None:
        print("Errore nel caricamento dei dati.")
        return

    for _, riga in df.iterrows():
        # Estraggo i docenti ricercatori/tempo indeterminato
        docente_indeterminato_ricercatore(fatti_docenti_tipo_contratto, riga,
                                          fatti_docenti)

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
    print(f"Fatti `docente\\2` scritti in {file_output}")

    file_output = os.path.join(
        dir_output, 'corsi_di_studio.asp')
    with open(file_output, 'w', encoding='utf-8') as f:
        for fatto in fatti_corsi_di_studio.values():
            f.write(f"{fatto}\n")
    print(f"Fatti `corso_di_studio\\2` scritti in {file_output}")

    file_output = os.path.join(
        dir_output, 'contratti_docenti.asp')
    with open(file_output, 'w', encoding='utf-8') as f:
        for fatto in fatti_docenti_tipo_contratto.values():
            f.write(f"{fatto}\n")
        print(f"Fatti `indeterminato\\1`, `ricercatore\\1` scritti in {
            file_output}")


def main():

    try:
        # Genera i fatti
        genera_fatti()
    except csv_loader.CaricamentoCSVErrore as e:
        print(f"Errore durante il caricamento del CSV: {e}")


if __name__ == "__main__":
    main()

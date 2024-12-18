import re
import os

from .csv_loader import (
    carica_dati_csv,
    normalizza_nome
)

from .facts import (
    pd,
)


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
        if pd.notna(ssd_2015) and pd.notna(ssd_2024):
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
            codice_modificato = normalizza_nome(codice_troncato)
        else:
            # Gestisce valori non stringa
            codice_troncato = codice_modificato = ssd_2015

        if codice_troncato not in mappa_progressiva:  # Evita duplicati
            mappa_progressiva[codice_troncato] = codice_modificato

    # Aggiungi un valore predefinito per NULL
    mappa_progressiva['NULL'] = 'null'

    return mappa_progressiva

# Funzione per trovare la numerosita massima di un corso


def genera_mappa_corso_max(mappa_corso_categoria, input_dir):
    mappa_corso_max = {}

    file_csv_jolly = os.path.join(input_dir, 'numerosita/jolly.csv')

    file_csv_classi = os.path.join(input_dir, 'numerosita/classi.csv')

    file_csv_numerosita_l = os.path.join(
        input_dir, 'numerosita/numerosita_l.csv')
    file_csv_numerosita_lm = os.path.join(
        input_dir, 'numerosita/numerosita_lm.csv')
    file_csv_numerosita_cu = os.path.join(
        input_dir, 'numerosita/numerosita_cu.csv')

    df = carica_dati_csv(file_csv_jolly)
    if df is None:
        print("Errore nel caricamento dei dati da `jolly.csv`")
        return None

    # Creazione mappa
    mappa_corso_classe = {}
    for _, riga in df.iterrows():

        classe = riga['Classe']
        corso = int(riga['Cod. Corso di Studio'])

        if corso is None or classe is None:
            print(f"corso is {corso}")
            print(f"classe is {classe}")

        mappa_corso_classe[corso] = classe

    df = carica_dati_csv(file_csv_classi)
    if df is None:
        print("Errore nel caricamento dei dati da `classi.csv`")
        return None

    # Creazione mappa
    mappa_classe_area = {}
    for _, riga in df.iterrows():

        classe = riga['CLASSE']
        area = riga['AREA']

        if classe is None or area is None:
            print(f"area is {area}")
            print(f"classe is {classe}")

        mappa_classe_area[classe] = area

    df_l = carica_dati_csv(file_csv_numerosita_l)
    if df_l is None:
        print("Errore nel caricamento dei dati da `numerosita_l.csv`")
        return None

    mappa_area_max_l = {}
    for _, riga in df_l.iterrows():

        area = riga['Cod. Area']
        max = riga['Massimo']

        if area is None or max is None:
            print(f"area is {area}")
            print(f"max is {max}")

        mappa_area_max_l[area] = max

    df_lm = carica_dati_csv(file_csv_numerosita_lm)
    if df_lm is None:
        print("Errore nel caricamento dei dati da `numerosita_lm.csv`")
        return None

    mappa_area_max_lm = {}
    for _, riga in df_lm.iterrows():

        area = riga['Cod. Area']
        max = riga['Massimo']

        if area is None or max is None:
            print(f"area is {area}")
            print(f"max is {max}")

        mappa_area_max_lm[area] = max

    df_cu = carica_dati_csv(file_csv_numerosita_cu)
    if df_cu is None:
        print("Errore nel caricamento dei dati da `numerosita_cu.csv`")
        return None

    mappa_area_max_cu = {}
    for _, riga in df_cu.iterrows():

        area = riga['Cod. Area']
        max = riga['Massimo']

        if area is None or max is None:
            print(f"area is {area}")
            print(f"max is {max}")

        mappa_area_max_cu[area] = max

    print(mappa_corso_categoria)
    for corso, classe in mappa_corso_classe.items():
        try:
            # print(f"corso: {corso}")
            classe = mappa_corso_classe[corso]
            # print(f"classe: {classe}")
            area = mappa_classe_area[classe]
            # print(f"area: {area}")

            categoria = mappa_corso_categoria[corso][1]
            # print(f"categoria: {categoria}")
            if categoria == "l":
                max = mappa_area_max_l[area]
            elif categoria == "lm":
                max = mappa_area_max_lm[area]
            else:
                max = mappa_area_max_cu[area]

            mappa_corso_max[corso] = max
        except Exception as e:
            print(f"errore su {corso}: {e}")
            continue

    return mappa_corso_max


# Funzione per trovare la matricola in base al nome del docente
def find_matricola_by_name(nome_docente, mappa_docenti):
    for matricola, nome in mappa_docenti.items():
        # Usa regex per fare un match tra il nome e il nome completo nel CSV
        # La regex è case-insensitive grazie a re.IGNORECASE
        if re.search(r'\b' + re.escape(nome_docente) + r'\b', nome, re.IGNORECASE):
            return matricola
    return None  # Nessun match trovato


def genera_mappa_docenti(df):
    mappa_docenti = {}

    for _, riga in df.iterrows():
        matricola = int(riga['Matricola'])
        nome = riga['Cognome e Nome']

        mappa_docenti[matricola] = nome

    return mappa_docenti


def genera_mappa_presidenti(mappa_docenti, file_csv_presidenti):
    mappa_presidenti = {}

    df = carica_dati_csv(file_csv_presidenti)
    if df is None:
        print("Errore nel caricamento dei dati da `presidenti.csv`")
        return None

    for _, riga in df.iterrows():

        corso = int(riga['Matricola'])

        # Estrai il nome completo dalla seconda colonna (Nome Cognome)
        nome_cognome = riga['Nome e Cognome'].strip()
        if not nome_cognome:
            continue

        # Trova la matricola corrispondente
        matricola = find_matricola_by_name(nome_cognome, mappa_docenti)

        if not matricola:
            print(f"Nome: {nome_cognome}, Matricola non trovata")
            continue

        mappa_presidenti[corso] = matricola

    return mappa_presidenti


def genera_mappa_corso_categoria(input_dir):
    mappa_corso_categoria = {}

    file_csv_jolly = os.path.join(input_dir, 'numerosita/jolly.csv')
    df = carica_dati_csv(file_csv_jolly)
    if df is None:
        print("Errore nel caricamento dei dati da `jolly.csv`")
        return None

    categorie_descrizione = {
        "5 DI CUI 3 PO/PA": "g5",
        "4 DI CUI 2 PO/PA": "g4",
        "3 DI CUI 1 PO/PA": "g3"
    }

    for _, riga in df.iterrows():
        categoria = riga['Categoria']
        if (pd.isna(categoria)):
            continue

        try:
            corso = int(riga['Cod. Corso di Studio'])
            categoria = categorie_descrizione[categoria]
        except Exception as e:
            print(e)
            continue

        # print(f"corso:{corso}, categoria: {categoria}")
        mappa_corso_categoria[corso] = [categoria, 'null']

    return mappa_corso_categoria

import argparse
import os
import re

from modules.csv_loader import (
    carica_dati_csv,
    normalizza_nome
)
from modules.wfacts import (
    write_dic,
    write_set
)

from modules.facts import (
    docente,
    categoria_corso_speciali,
    categoria_corso,
    corso,
    docente_indeterminato_ricercatore,
    docente_contratto,
    insegnamento,
    insegna,
    normalizza_settore,
    settori_di_riferimento,
    settori,
    pd,
    garanti_per_corso,
    presidenti
)

from modules.stats import (
    carica_numerosita
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
def genera_mappa_corso_max():
    mappa_corso_max = {}

    file_csv_jolly = '../../input/numerosita/jolly.csv'

    file_csv_classi = '../../input/numerosita/classi.csv'

    file_csv_numerosita = '../../input/numerosita/numerosita.csv'

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

    df = carica_dati_csv(file_csv_numerosita)
    if df is None:
        print("Errore nel caricamento dei dati da `numerosita.csv`")
        return None

    # Creazione mappa
    mappa_area_max = {}    
    for _, riga in df.iterrows():

        area = riga['Cod. Area']
        max = riga['Massimo']

        if area is None or max is None:
            print(f"area is {area}")
            print(f"max is {max}")

        mappa_area_max[area] = max

    for corso, classe in mappa_corso_classe.items():
        try:
            classe = mappa_corso_classe[corso]
            area = mappa_classe_area[classe]
            max = mappa_area_max[area]
            mappa_corso_max[corso] = max
        except Exception as e:
            print(f"errore su {corso}")
            print(e)
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


def genera_mappa_presidenti(mappa_docenti):
    mappa_presidenti = {}

    file_csv_presidenti = '../../input/presidenti.csv'
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


def genera_fatti(corsi_da_filtrare, corsi_da_escludere, dir):
    """Legge il file CSV, genera i fatti per ogni gruppo e li scrive nel file."""

    # Carica i dati
    file_csv_docenti = '../../input/docenti.csv'
    df = carica_dati_csv(file_csv_docenti)
    if df is None:
        print("Errore nel caricamento dei dati da `docenti.csv`")
        return

    mappa_ssd = mappa_settori_nuovi_vecchi(df)
    mappa_ssd_termine = mappa_settori_termini(mappa_ssd)

    fatti_settori = {}
    settori(fatti_settori, mappa_ssd_termine)
    write_dic(fatti_settori, dir, 'settori.asp')

    mappa_docenti = genera_mappa_docenti(df)
    mappa_presidenti = genera_mappa_presidenti(mappa_docenti)
    fatti_presidenti = {}
    presidenti(fatti_presidenti, mappa_presidenti)
    write_dic(fatti_presidenti, dir, 'presidenti.asp')

    fatti_docenti_tipo_contratto = {}
    for _, riga in df.iterrows():
        # Estraggo i docenti ricercatori/tempo indeterminato
        docente_indeterminato_ricercatore(
            fatti_docenti_tipo_contratto, riga)

    file_csv_coperture = '../../input/coperture2425.csv'
    df = carica_dati_csv(file_csv_coperture)
    if df is None:
        print("Errore nel caricamento dei dati da `coperture2425.csv`")
        return

    fatti_corsi_di_studio = {}

    fatti_categorie_corso = {}
    categoria_corso_speciali(fatti_categorie_corso)

    fatti_docenti = {}
    fatti_insegnamenti = {}
    fatti_insegna = set()
    fatti_settori_di_riferimento = set()

    mappa_corso_categoria = {}

    for _, riga in df.iterrows():
        cod_corso = riga['Cod. Corso di Studio']
        if pd.isna(cod_corso):
            continue
        cod_corso = int(cod_corso)

        # Filtra i corsi
        if corsi_da_filtrare and cod_corso not in corsi_da_filtrare:
            # print(f'{cod_corso} escluso')
            continue
        if corsi_da_escludere and cod_corso in corsi_da_escludere:
            # print(f'{cod_corso} escluso')
            continue

        # Estraggo i docenti
        docente(fatti_docenti, riga, mappa_ssd, mappa_ssd_termine)
        # Estraggo le categoria_corso
        categoria_corso(fatti_categorie_corso, mappa_corso_categoria, riga)
        # Estraggo i corsi
        corso(fatti_corsi_di_studio, riga, mappa_corso_categoria)
        # Estraggo docenti a contratto
        docente_contratto(
            fatti_docenti_tipo_contratto, riga, fatti_docenti)
        # Estraggo insegnamenti
        insegnamento(fatti_insegnamenti, riga)
        # Estraggo fatti insegna
        insegna(fatti_insegna, riga)
        # Estraggo i settori di riferimento per i corsi
        settori_di_riferimento(fatti_settori_di_riferimento, riga,
                               mappa_ssd, mappa_ssd_termine)

    mappa_corso_max = genera_mappa_corso_max()
    mappa_numerosita = {}
    carica_numerosita(mappa_numerosita, mappa_corso_max)

    fatti_garanti_per_corso = {}
    garanti_per_corso(fatti_garanti_per_corso, mappa_corso_categoria, 
                    mappa_numerosita)

    # Stampo i fatti nei rispettivi file
    write_dic(fatti_categorie_corso, dir, 'categorie_corso.asp')
    write_dic(fatti_docenti, dir, 'docenti.asp')
    write_dic(fatti_corsi_di_studio, dir, 'corsi_di_studio.asp')
    write_dic(fatti_docenti_tipo_contratto, dir, 'contratti.asp')
    write_dic(fatti_insegnamenti, dir, 'insegnamenti.asp')
    write_set(fatti_insegna, dir, 'insegna.asp')
    write_set(fatti_settori_di_riferimento, dir, 'settori_di_riferimento.asp')
    write_dic(fatti_garanti_per_corso, dir, 'garanti_per_corso.asp')


def main():
    # Se un corso è presente in entrambi i filtri viene escluso
    parser = argparse.ArgumentParser(description="Genera fatti ASP.")
    parser.add_argument(
        "--filter", type=str, help="Lista di ID di corsi separati da virgola da considerare.", default=None)
    parser.add_argument(
        "--exclude", type=str, help="Lista di ID di corsi separati da virgola da escludere.", default=None)
    args = parser.parse_args()

    # Ottieni i filtri (se presenti)
    corsi_da_filtrare = set(
        map(int, args.filter.split(','))) if args.filter else set()

    corsi_da_escludere = set(
        map(int, args.exclude.split(','))) if args.exclude else set()

    nuovi_2024 = [
        3072, 3071, 3070, 5008, 5009, 5063, 3021, 3065, 5081, 3055,
        5082, 5051, 5057, 5070
    ]
    corsi_da_escludere.update(nuovi_2024)

    dir = '../../src/asp/facts/'
    # Creo cartella di output
    if not os.path.exists(dir):
        os.makedirs(dir)

    # Genera i fatti
    genera_fatti(corsi_da_filtrare, corsi_da_escludere, dir)


if __name__ == "__main__":
    main()

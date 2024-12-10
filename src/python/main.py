import argparse
import os

from modules.csv_loader import *  # Importa il modulo per caricare e pulire i dati
from modules.wfacts import *
from modules.facts import *


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


def genera_fatti(corsi_da_filtrare, dir):
    """Legge il file CSV, genera i fatti per ogni gruppo e li scrive nel file."""

    # Carica i dati
    file_csv_docenti = '../../input/docenti.csv'
    df = carica_dati_csv(file_csv_docenti)
    if df is None:
        print("Errore nel caricamento dei dati da `docenti.csv`")
        return

    mappa_ssd = mappa_settori_nuovi_vecchi(df)
    mappa_ssd_termine = mappa_settori_termini(mappa_ssd)
    write_dic(mappa_ssd_termine, dir, 'settori.asp')

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
    fatti_docenti = {}
    fatti_insegnamenti = {}
    fatti_insegna = set()
    fatti_settori_di_riferimento = set()
    for _, riga in df.iterrows():
        cod_corso = riga['Cod. Corso di Studio']
        if pd.isna(cod_corso):
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
        docente_contratto(
            fatti_docenti_tipo_contratto, riga, fatti_docenti)
        # Estraggo insegnamenti
        insegnamento(fatti_insegnamenti, riga)
        # Estraggo fatti insegna
        insegna(fatti_insegna, riga)
        # Estraggo i settori di riferimento per i corsi
        settori_di_riferimento(fatti_settori_di_riferimento, riga,
                               mappa_ssd, mappa_ssd_termine)

    file_csv_docenti = '../../input/docenti.csv'
    df = carica_dati_csv(file_csv_docenti)
    if df is None:
        print("Errore nel caricamento dei dati.")
        return

    # Stampo i fatti nei rispettivi file
    write_dic(fatti_categorie_corso, dir, 'categorie_corso.asp')
    write_dic(fatti_docenti, dir, 'docenti.asp')
    write_dic(fatti_corsi_di_studio, dir, 'corsi_di_studio.asp')
    write_dic(fatti_docenti_tipo_contratto, dir, 'contratti.asp')
    write_dic(fatti_categorie_corso, dir, 'docenti.asp')
    write_dic(fatti_insegnamenti, dir, 'insegnamenti.asp')
    write_set(fatti_insegna, dir, 'insegna.asp')
    write_set(fatti_settori_di_riferimento, dir, 'settori_di_riferimento.asp')


def main():
    parser = argparse.ArgumentParser(description="Genera fatti ASP.")
    parser.add_argument(
        "--filter", type=str, help="Lista di ID di corsi separati da virgola da considerare.", default=None)
    args = parser.parse_args()

    # Ottieni i filtri (se presenti)
    corsi_da_filtrare = set(
        map(int, args.filter.split(','))) if args.filter else None

    dir = '../../src/asp/facts/test_filter'
    try:
        # Creo cartella di output
        if not os.path.exists(dir):
            os.makedirs(dir)

        # Genera i fatti
        genera_fatti(corsi_da_filtrare, dir)
    except Exception as e:
        print(f"Errore durante l'elaborazione dati: {e}")


if __name__ == "__main__":
    main()

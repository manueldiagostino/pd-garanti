import argparse
import csv_loader  # Importa il modulo per caricare e pulire i dati
import os
import re


def genera_fatti_da_nome(df, file_output, nome_fatto, colonne):
    """Genera i fatti a partire dal DataFrame e li scrive nel file di output."""
    try:
        # Verifica che tutte le colonne richieste esistano nel DataFrame
        csv_loader.verifica_colonne_esistenti(df, colonne)

        # Scrivi i fatti nel file di output
        with open(file_output, 'w', encoding='utf-8') as f:
            fatti_unici = set()  # Usa un set per memorizzare i fatti unici

            for _, riga in df.iterrows():
                # Estrai i valori delle colonne specificate per generare il fatto
                valori = []
                for colonna in colonne:
                    valore = riga[colonna]

                    # Controlla se il valore è NaN
                    if csv_loader.pd.isna(valore):
                        continue  # Salta i valori NaN

                    # Prova a convertire il valore in intero, altrimenti usa il valore originale
                    try:
                        valore = int(valore)
                    except (ValueError, TypeError):
                        pass

                    valori.append(valore)

                # Genera il fatto ASP se ci sono valori validi
                if valori:  # Controlla che ci siano valori da scrivere
                    fatto = f"{nome_fatto}({', '.join(map(str, valori))})."
                    fatti_unici.add(fatto)  # Aggiungi al set

            # Scrivi i fatti unici nel file
            for fatto in sorted(fatti_unici):  # Ordina per leggibilità (opzionale)
                f.write(fatto + '\n')

        print(f"Fatti unici `{nome_fatto}\\{
              len(colonne)}` scritti in {file_output}")

    except csv_loader.ColonnaNonTrovataErrore as e:
        print(e)
    except Exception as e:
        print(f"Errore durante la scrittura dei fatti `{
              nome_fatto}\\{len(colonne)}`: {e}")


def genera_fatti_settori(df, file_output, mappa_ssd_int):
    """
    Genera i fatti a partire dalla mappa `mappa_ssd_int` e li scrive nel file di output.

    :param df: DataFrame (non utilizzato direttamente, ma mantenuto per uniformità con altri metodi).
    :param file_output: Percorso del file di output.
    :param mappa_ssd_int: Dizionario con chiavi come codici SSD e valori come interi progressivi.
    """
    nome_fatto = 'settore'

    try:
        # Scrivi i fatti nel file di output
        with open(file_output, 'w', encoding='utf-8') as f:
            for ssd, valore_intero in mappa_ssd_int.items():
                # Genera il fatto ASP
                fatto = f"{nome_fatto}({valore_intero})."
                f.write(fatto + '\n')  # Scrivi il fatto nel file

        print(f"Fatti `{nome_fatto}` scritti con successo in {file_output}")
    except Exception as e:
        print(f"Errore durante la scrittura dei fatti `{nome_fatto}`: {e}")


def genera_fatti_docenti(df, file_output, mappa_ssd, mappa_ssd_int):
    """Genera i fatti a partire dal DataFrame e li scrive nel file di output."""

    colonne = ['Matricola', 'Cod. Settore Docente']
    nome_fatto = 'docente'

    try:
        # Verifica che tutte le colonne richieste esistano nel DataFrame
        csv_loader.verifica_colonne_esistenti(df, colonne)

        # Scrivi i fatti nel file di output
        with open(file_output, 'w', encoding='utf-8') as f:
            fatti_unici = set()  # Usa un set per memorizzare i fatti unici

            for _, riga in df.iterrows():
                # Estrai i valori delle colonne specificate per generare il fatto
                valori = []

                # Leggo matricola
                valore = riga[colonne[0]]
                if csv_loader.pd.isna(valore):
                    continue  # Salta i valori NaN

                valore = int(valore)
                valori.append(valore)

                # Leggo Cod. Settore Docente
                valore = riga[colonne[1]]
                if csv_loader.pd.isna(valore):
                    valore = 'NULL/'  # Salta i valori NaN

                if (valore in mappa_ssd):
                    nuova_chiave = mappa_ssd[valore]
                    valore = mappa_ssd_int[nuova_chiave.split('/')[0]]
                else:
                    valore = valore.split('/')[0]
                    valore = mappa_ssd_int[valore]

                valori.append(valore)

                fatto = f"{nome_fatto}({valori[0]}, settore({valori[1]}))."
                fatti_unici.add(fatto)  # Aggiungi al set

            # Scrivi i fatti unici nel file
            for fatto in sorted(fatti_unici):
                f.write(fatto + '\n')

        print(f"Fatti unici `{nome_fatto}\\{
            len(colonne)}` scritti in {file_output}")

    except csv_loader.ColonnaNonTrovataErrore as e:
        print(e)
    except Exception as e:
        print(f"Errore durante la scrittura dei fatti `{
              nome_fatto}\\{len(colonne)}`: {e}")


def genera_fatti_corsi(df, file_output):
    """
    Genera i fatti a partire dalla mappa `mappa_ssd_int` e li scrive nel file di output.

    :param df: DataFrame (non utilizzato direttamente, ma mantenuto per uniformità con altri metodi).
    :param file_output: Percorso del file di output.
    :param mappa_ssd_int: Dizionario con chiavi come codici SSD e valori come interi progressivi.
    """
    nome_fatto = 'corso'
    colonne = ['Cod. Corso di Studio', 'Cod. Tipo Corso']

    try:
        # Verifica che tutte le colonne richieste esistano nel DataFrame
        csv_loader.verifica_colonne_esistenti(df, colonne)

        # Scrivi i fatti nel file di output
        with open(file_output, 'w', encoding='utf-8') as f:
            fatti_unici = set()  # Usa un set per memorizzare i fatti unici

            for _, riga in df.iterrows():
                # Estrai i valori delle colonne specificate per generare il fatto
                valori = []

                # Leggo matricola
                valore = riga[colonne[0]]
                if csv_loader.pd.isna(valore):
                    continue  # Salta i valori NaN

                valore = int(valore)
                valori.append(valore)

                # Leggo Cod. Settore Docente
                valore = riga[colonne[1]]
                valore = csv_loader.normalizza_nome(valore)
                valori.append(valore)

                fatto = f"{nome_fatto}({valori[0]}, categoria({valori[1]}))."
                fatti_unici.add(fatto)  # Aggiungi al set

            # Scrivi i fatti unici nel file
            for fatto in sorted(fatti_unici):
                f.write(fatto + '\n')

        print(f"Fatti unici `{nome_fatto}\\{
            len(colonne)}` scritti in {file_output}")

    except csv_loader.ColonnaNonTrovataErrore as e:
        print(e)
    except Exception as e:
        print(f"Errore durante la scrittura dei fatti `{
              nome_fatto}\\{len(colonne)}`: {e}")


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


def indeterminato(fascia):
    # Compila la regex
    pattern = r'\b(Ordinario|Associato)\b'
    return bool(re.search(pattern, str(fascia)))


def ricercatore(fascia):
    # Compila la regex
    pattern = r'\b(Ricercatore)\b'
    return bool(re.search(pattern, str(fascia)))


def contratto(fascia):
    # TODO: sistemare regex
    pattern = r'\b(L. 240/10)\b'
    return bool(re.search(pattern, str(fascia)))


def genera_fatti_docenti_indeterminato(df, file_output, colonne=['Matricola', 'Fascia']):
    """Genera i fatti per i docenti indeterminati a partire dal DataFrame e li scrive nel file di output."""
    try:
        # Verifica che tutte le colonne richieste esistano nel DataFrame
        csv_loader.verifica_colonne_esistenti(df, colonne)

        # Scrivi i fatti nel file di output
        with open(file_output, 'w', encoding='utf-8') as f:
            fatti_unici = set()  # Usa un set per memorizzare i fatti unici

            for _, riga in df.iterrows():
                # Estrai i valori delle colonne specificate per generare il fatto
                valori = []
                for colonna in colonne:
                    valore = riga[colonna]

                    # Controlla se il valore è NaN
                    if csv_loader.pd.isna(valore):
                        continue  # Salta i valori NaN

                    # Prova a convertire il valore in intero, altrimenti usa il valore originale
                    try:
                        valore = int(valore)
                    except (ValueError, TypeError):
                        pass

                    valori.append(valore)

                # Verifica la "Fascia" e determina lo stato del docente
                if indeterminato(valori[1]):
                    fatto = f"docente_indeterminato({valori[0]})"
                elif ricercatore(valori[1]):
                    fatto = f"docente_ricercatore({valori[0]})"
                elif contratto(valori[1]):
                    fatto = f"docente_contratto({valori[0]})"
                else:
                    fatto = f"docente_determinato({valori[0]})"

                fatti_unici.add(fatto)  # Aggiungi al set

            # Scrivi i fatti unici nel file
            for fatto in sorted(fatti_unici):  # Ordina per leggibilità (opzionale)
                f.write(fatto + '\n')

        print(f"Fatti unici `docente_[in]determinato\\1` scritti in {
              file_output}")

    except csv_loader.ColonnaNonTrovataErrore as e:
        print(e)
    except Exception as e:
        print(
            f"Errore durante la scrittura dei fatti `docente_[in]determinato\\1`: {e}")


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
    mappa_ssd_int = mappa_settori_termini(mappa_ssd)

    print('Mappa ssd nuovi-vecchi generata')

    file_csv_coperture = '../../input/coperture2425.csv'
    df = csv_loader.carica_dati_csv(file_csv_coperture)

    if df is None:
        print("Errore nel caricamento dei dati.")
        return

    genera_fatti_settori(df, os.path.join(
        dir_output, 'settori.asp'), mappa_ssd_int)
    genera_fatti_docenti(df, os.path.join(
        dir_output, 'docenti.asp'), mappa_ssd, mappa_ssd_int)
    genera_fatti_corsi(df, os.path.join(
        dir_output, 'corsi.asp'))

    # genera_fatti_docenti_indeterminato(
    #     df, os.path.join(dir_output, 'tipologia_contratti.asp'))
    # genera_fatti_da_nome(df, os.path.join(
    #     dir_output, 'corsi_di_studio.asp'), 'corso_di_studio', ['Cod. Corso di Studio'])


def configura_parser():
    """Configura e restituisce il parser degli argomenti."""
    parser = argparse.ArgumentParser(
        description="Genera fatti ASP utili al solver")
    parser.add_argument(
        "file_csv",  # Il CSV di input
        type=str,
        help="Il percorso del file CSV da leggere"
    )
    return parser


def main():

    try:
        # Genera i fatti
        genera_fatti()
    except csv_loader.CaricamentoCSVErrore as e:
        print(f"Errore durante il caricamento del CSV: {e}")


if __name__ == "__main__":
    main()

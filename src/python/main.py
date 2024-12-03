import argparse
import csv_loader  # Importa il modulo per caricare e pulire i dati
import os
import re


def generate_facts_from_name(df, output_file, fact_name, columns):
    """Genera i fatti a partire dal DataFrame e li scrive nel file di output."""
    try:
        # Verifica che tutte le colonne richieste esistano nel DataFrame
        csv_loader.check_columns_exist(df, columns)

        # Scrivi i fatti nel file di output
        with open(output_file, 'w', encoding='utf-8') as f:
            unique_facts = set()  # Usa un set per memorizzare i fatti unici

            for _, row in df.iterrows():
                # Estrai i valori delle colonne specificate per generare il fatto
                values = []
                for column in columns:
                    value = row[column]

                    # Controlla se il valore è NaN
                    if csv_loader.pd.isna(value):
                        continue  # Salta i valori NaN

                    # Prova a convertire il valore in intero, altrimenti usa il valore originale
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        pass

                    values.append(value)

                # Genera il fatto ASP se ci sono valori validi
                if values:  # Controlla che ci siano valori da scrivere
                    fact = f"{fact_name}({', '.join(map(str, values))})."
                    unique_facts.add(fact)  # Aggiungi al set

            # Scrivi i fatti unici nel file
            for fact in sorted(unique_facts):  # Ordina per leggibilità (opzionale)
                f.write(fact + '\n')

        print(f"Fatti `{fact_name}\\{len(columns)
                                     }` unici scritti in {output_file}")

    except csv_loader.ColumnNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Errore durante la scrittura dei fatti `{
              fact_name}\\{len(columns)}`: {e}")


def verifica_indeterminato(fascia):
    # Compila la regex
    pattern = r'\b(Ordinario|Associato)\b'
    return bool(re.search(pattern, str(fascia)))


def verifica_ricercatore(fascia):
    # Compila la regex
    pattern = r'\b(Ricercatore)\b'
    return bool(re.search(pattern, str(fascia)))


def verifica_contratto(fascia):
    # TODO: sistemare regex
    pattern = r'\b(L. 240/10)\b'
    return bool(re.search(pattern, str(fascia)))


def generate_facts_docenti_indeterminato(df, output_file, columns=['Matricola', 'Fascia']):
    """Genera i fatti a partire dal DataFrame e li scrive nel file di output."""
    try:
        # Verifica che tutte le colonne richieste esistano nel DataFrame
        csv_loader.check_columns_exist(df, columns)

        # Scrivi i fatti nel file di output
        with open(output_file, 'w', encoding='utf-8') as f:
            unique_facts = set()  # Usa un set per memorizzare i fatti unici

            for _, row in df.iterrows():
                # Estrai i valori delle colonne specificate per generare il fatto
                values = []
                for column in columns:
                    value = row[column]

                    # Controlla se il valore è NaN
                    if csv_loader.pd.isna(value):
                        continue  # Salta i valori NaN

                    # Prova a convertire il valore in intero, altrimenti usa il valore originale
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        pass

                    values.append(value)
                if (verifica_indeterminato(values[1])):
                    fact = f"docente_indeterminato({values[0]})"
                elif (verifica_ricercatore(values[1])):
                    fact = f"docente_ricercatore({values[0]})"
                elif (verifica_contratto(values[1])):
                    fact = f"docente_contratto({values[0]})"
                else:
                    fact = f"docente_determinato({values[0]})"

                unique_facts.add(fact)  # Aggiungi al set

            # Scrivi i fatti unici nel file
            for fact in sorted(unique_facts):  # Ordina per leggibilità (opzionale)
                f.write(fact + '\n')

        print(f"Fatti `docente_[in]determinato\\1` unici scritti in {
              output_file}")

    except csv_loader.ColumnNotFoundError as e:
        print(e)
    except Exception as e:
        print(
            f"Errore durante la scrittura dei fatti `docente_[in]determinato\\1`: {e}")


def generate_facts():
    """Legge il file CSV, genera i fatti per ogni gruppo e li scrive nel file."""

    # Path di output
    output_dir = '../../src/asp/facts/'

    # Carica i dati
    docenti_csv_file = '../../input/docenti.csv'
    df = csv_loader.load_csv_data(docenti_csv_file)

    if df is None:
        print("Errore nel caricamento dei dati.")
        return

    # Genera e scrive i fatti per i docenti
    generate_facts_from_name(df, os.path.join(output_dir, 'docenti.asp'), 'docente',
                             ['Matricola'])
    generate_facts_docenti_indeterminato(df, os.path.join(
        output_dir, 'tipologia_contratti.asp'))

    coperture_csv_file = '../../input/coperture2425.csv'
    df = csv_loader.load_csv_data(coperture_csv_file)

    if df is None:
        print("Errore nel caricamento dei dati.")
        return

    generate_facts_from_name(df, os.path.join(
        output_dir, 'corsi_di_studio.asp'), 'corso_di_studio', ['Cod. Corso di Studio'])


def setup_parser():
    """Configura e restituisce il parser degli argomenti."""
    parser = argparse.ArgumentParser(
        description="Genera fatti ASP ground utili al solver")
    parser.add_argument(
        "csv_file",  # Il CSV di input
        type=str,
        help="Il percorso del file CSV da leggere"
    )
    return parser


def main():

    try:
        # Genera i fatti
        generate_facts()
    except csv_loader.CSVLoaderError as e:
        print(f"Errore durante il caricamento del CSV: {e}")


if __name__ == "__main__":
    main()

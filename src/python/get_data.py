import pandas as pd
import argparse
import unicodedata

def fact_docente(matricola: int, extra: list[str]) -> str:
    """Genera il fatto docente con matricola ed eventuali informazioni extra."""
    extra_values = ", ".join(f"\"{value}\"" for value in extra)
    return f"docente({matricola}, {extra_values})."

def clean_text(text: str) -> str:
    """Rimuove caratteri non standard come spazi non separabili."""
    if isinstance(text, str):  # Controlla che il valore sia una stringa
        # Normalizza i caratteri Unicode e sostituisce spazi non separabili
        text = unicodedata.normalize("NFKC", text).replace("\xa0", " ").strip()
    return text

def is_column_integer(df: pd.DataFrame, column: str) -> bool:
    """Verifica se una colonna contiene solo numeri interi."""
    try:
        # Tenta di convertire la colonna in numerico e verifica che sia di tipo intero
        pd.to_numeric(df[column], errors='raise')
        return df[column].dtype == 'int64'
    except ValueError:
        return False

def setup_parser():
    """Configura e restituisce il parser degli argomenti."""
    parser = argparse.ArgumentParser(description="Ottieni informazioni sui docenti.")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Percorso del file CSV da leggere."
    )
    parser.add_argument(
        "--column",
        type=str,
        required=True,
        nargs='+',  # Permette più colonne
        help="Nome delle colonne extra da includere nei fatti. Specificare uno o più nomi separati da spazio."
    )
    return parser

def main():
    # Configura il parser
    parser = setup_parser()
    args = parser.parse_args()

    # Ottieni il percorso del file CSV
    csv_file = args.input
    # Lista delle colonne specificate dall'utente
    extra_columns = args.column

    try:
        # Legge il file CSV
        df = pd.read_csv(csv_file, delimiter=',')
        # Pulisce i dati
        df = df.applymap(clean_text)

        # Controlla se tutte le colonne specificate esistono
        for column in extra_columns:
            if column not in df.columns:
                print(f"Errore: La colonna '{column}' non esiste nel file CSV.")
                return

            # Verifica se la colonna è numerica (intera)
            if is_column_integer(df, column):
                # Converte i valori numerici
                df[column] = int(pd.to_numeric(df[column], errors='coerce'))

        for _, row in df.iterrows():
            extras = [row[column] for column in extra_columns]
            print(extras)

    except FileNotFoundError:
        print("Errore: File CSV non trovato!")
    except KeyError as e:
        print(f"Errore: Colonna mancante nel file CSV: {e}")
    except Exception as e:
        print(f"Errore durante la lettura del CSV: {e}")

# Avvio dello script
if __name__ == "__main__":
    main()


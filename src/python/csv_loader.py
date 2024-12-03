import pandas as pd
import unicodedata


class CSVLoaderError(Exception):
    """Eccezione base per errori di caricamento CSV."""
    pass


class FileNotFoundError(CSVLoaderError):
    """Eccezione sollevata quando il file CSV non viene trovato."""
    pass


class EmptyDataError(CSVLoaderError):
    """Eccezione sollevata quando il CSV è vuoto."""
    pass


class InvalidCSVFormatError(CSVLoaderError):
    """Eccezione sollevata per errori di formato del CSV."""
    pass


class DataCleaningError(CSVLoaderError):
    """Eccezione sollevata per errori nella pulizia dei dati."""
    pass

# Definisci un'eccezione personalizzata
class ColumnNotFoundError(Exception):
    """Eccezione per quando una colonna non viene trovata nel DataFrame."""
    pass

def check_columns_exist(df: pd.DataFrame, column_names: list[str]):
    """Controlla se tutte le colonne specificate esistono nel DataFrame. Se una o più non esistono, lancia un'eccezione."""

    missing_columns = [col for col in column_names if col not in df.columns]

    if missing_columns:
        raise ColumnNotFoundError(f"Le seguenti colonne non esistono nel DataFrame: {', '.join(missing_columns)}.")

def clean_text(text: str) -> str:
    """Pulisce i dati da caratteri non standard come spazi non separabili."""
    if isinstance(text, str):
        try:
            # Normalizza i caratteri Unicode e rimuove spazi non separabili
            text = unicodedata.normalize(
                "NFKC", text).replace("\xa0", " ").strip()
        except Exception as e:
            raise DataCleaningError(f"Errore nella pulizia del testo: {e}")
    return text


def load_csv_data(csv_file: str) -> pd.DataFrame:
    """Carica i dati da un file CSV e li pulisce."""
    try:
        # Legge il CSV in un DataFrame
        df = pd.read_csv(csv_file, delimiter=',')

        if df.empty:
            raise EmptyDataError(f"Il file '{csv_file}' è vuoto.")

        # Pulisce i dati nel DataFrame
        df = df.apply(lambda col: col.map(clean_text) if col.dtype == 'object' else col)

        return df
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Errore: Il file '{csv_file}' non è stato trovato.")
    except pd.errors.EmptyDataError:
        raise EmptyDataError(f"Errore: Il file '{csv_file}' è vuoto.")
    except pd.errors.ParserError:
        raise InvalidCSVFormatError(
            f"Errore: Formato CSV non valido nel file '{csv_file}'.")
    except Exception as e:
        raise CSVLoaderError(
            f"Errore durante il caricamento del file CSV: {e}")

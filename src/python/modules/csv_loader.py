import pandas as pd
import unicodedata


class ErroreCaricamentoCSV(Exception):
    """Eccezione base per errori di caricamento CSV."""
    pass


class FileNonTrovatoErrore(ErroreCaricamentoCSV):
    """Eccezione sollevata quando il file CSV non viene trovato."""
    pass


class CSVVuotoErrore(ErroreCaricamentoCSV):
    """Eccezione sollevata quando il CSV è vuoto."""
    pass


class FormatoCSVNonValidoErrore(ErroreCaricamentoCSV):
    """Eccezione sollevata per errori di formato del CSV."""
    pass


class PuliziaDatiErrore(ErroreCaricamentoCSV):
    """Eccezione sollevata per errori nella pulizia dei dati."""
    pass


class ColonnaNonTrovataErrore(Exception):
    """Eccezione sollevata quando una colonna non viene trovata nel DataFrame."""
    pass


def verifica_colonne_esistenti(df: pd.DataFrame, nomi_colonne: list[str]):
    """Controlla se tutte le colonne specificate esistono nel DataFrame. Se una o più non esistono, lancia un'eccezione."""
    colonne_mancanti = [
        colonna for colonna in nomi_colonne if colonna not in df.columns]
    if colonne_mancanti:
        raise ColonnaNonTrovataErrore(f"Le seguenti colonne non esistono nel DataFrame: {
                                      ', '.join(colonne_mancanti)}.")


def pulisci_testo(testo: str) -> str:
    """Pulisce i dati rimuovendo caratteri non standard come spazi non separabili."""
    if isinstance(testo, str):
        try:
            # Normalizza i caratteri Unicode e rimuove spazi non separabili
            testo = unicodedata.normalize(
                "NFKC", testo).replace("\xa0", " ").strip()
        except Exception as e:
            raise PuliziaDatiErrore(f"Errore nella pulizia del testo: {e}")
    return testo


def carica_dati_csv(file_csv: str) -> pd.DataFrame:
    """Carica i dati da un file CSV e li pulisce."""
    try:
        # Legge il CSV in un DataFrame
        df = pd.read_csv(file_csv, delimiter=',')

        if df.empty:
            raise CSVVuotoErrore(f"Il file '{file_csv}' è vuoto.")

        # Pulisce i dati nel DataFrame
        df = df.apply(lambda colonna: colonna.map(pulisci_testo)
                      if colonna.dtype == 'object' else colonna)

        return df
    except FileNotFoundError:
        raise FileNonTrovatoErrore(
            f"Errore: Il file '{file_csv}' non è stato trovato.")
    except pd.errors.EmptyDataError:
        raise CSVVuotoErrore(f"Errore: Il file '{file_csv}' è vuoto.")
    except pd.errors.ParserError:
        raise FormatoCSVNonValidoErrore(
            f"Errore: Formato CSV non valido nel file '{file_csv}'.")
    except Exception as e:
        raise ErroreCaricamentoCSV(
            f"Errore durante il caricamento del file CSV: {e}")


def normalizza_nome(nome: str) -> str:
    return nome.lower().replace('-', '_').replace(' ', '_')

import os

from .csv_loader import carica_dati_csv


def elabora_df(mappa_numerosita, df, mappa_corso_max):
    for _, riga in df.iterrows():
        tipo, codice, valore = riga
        # Aggiungi il valore come intero
        codice = int(codice)
        if codice not in mappa_corso_max:
            max = 250
            print(f"numerosita max per {codice} non trovata. Assegnata {max}")
        else:
            max = mappa_corso_max[codice]

        mappa_numerosita[codice] = [int(valore), max]


def carica_numerosita(mappa_numerosita, mappa_corso_max, input_dir):
    df = carica_dati_csv(os.path.join(
        input_dir, 'immatricolati_2023_triennali.csv'))
    if df is None:
        print("Errore nel caricamento dei dati da `immatricolati_2023_triennali`")
        return

    elabora_df(mappa_numerosita, df, mappa_corso_max)

    df = carica_dati_csv(os.path.join(
        input_dir, 'immatricolati_2023_magistrali.csv'))
    if df is None:
        print("Errore nel caricamento dei dati da `immatricolati_2023_magistrali`")
        return

    elabora_df(mappa_numerosita, df, mappa_corso_max)

    df = carica_dati_csv(os.path.join(input_dir, 'immatricolati_2023_cu.csv'))
    if df is None:
        print("Errore nel caricamento dei dati da `immatricolati_2023_cu`")
        return

    elabora_df(mappa_numerosita, df, mappa_corso_max)

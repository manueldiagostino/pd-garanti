from .csv_loader import carica_dati_csv


def elabora_df(mappa_numerosita, df):
    for _, riga in df.iterrows():
        tipo, codice, valore = riga
        # Aggiungi il valore come intero
        num_massima_default = 240
        mappa_numerosita[codice] = [int(valore), num_massima_default]


def carica_numerosita(mappa_numerosita):
    df = carica_dati_csv('../../input/immatricolati_2023_triennali.csv')
    if df is None:
        print("Errore nel caricamento dei dati da `immatricolati_2023_triennali`")
        return

    elabora_df(mappa_numerosita, df)

    df = carica_dati_csv('../../input/immatricolati_2023_magistrali.csv')
    if df is None:
        print("Errore nel caricamento dei dati da `immatricolati_2023_magistrali`")
        return

    elabora_df(mappa_numerosita, df)

    df = carica_dati_csv('../../input/immatricolati_2023_cu.csv')
    if df is None:
        print("Errore nel caricamento dei dati da `immatricolati_2023_cu`")
        return

    elabora_df(mappa_numerosita, df)

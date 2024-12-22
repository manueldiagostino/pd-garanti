from .messages import MessaggiErrore
from .facts import (
    pd,
)
from .csv_loader import (
    carica_dati_csv,
    normalizza_nome
)
from .facts import (
    docente,
    categoria_corso,
    corso,
    docente_contratto,
    insegnamento,
    insegna,
    settori_di_riferimento,
    garanti_per_corso,
)
from .stats import (
    carica_numerosita
)
import re
import os

from rich.console import Console
console = Console()


class GestoreSSD:
    _df = None  # Dataframe condiviso da tutti i metodi
    _mappa_ssd_2024_2015 = None
    _mappa_ssd_2015_termini = None
    _fatti_settori = None

    @staticmethod
    def inizializza(input_dir):
        """Carica i dati da un file CSV nel DataFrame condiviso."""
        file_docenti = os.path.join(input_dir, 'docenti.csv')

        if GestoreSSD._df is None:
            df = carica_dati_csv(file_docenti)
            if df is None:
                MessaggiErrore.errore(
                    f"Errore nel caricamento dei dati da {file_docenti}")

            GestoreSSD._df = df

    @staticmethod
    def genera_mappa_ssd_2024_2015():
        GestoreSSD._mappa_ssd_2024_2015 = {}

        for _, row in GestoreSSD._df.iterrows():
            ssd_2015 = row["SSD 2015"]
            ssd_2024 = row["SSD 2024"]

            # Evita valori mancanti
            if pd.notna(ssd_2015) and pd.notna(ssd_2024):
                GestoreSSD._mappa_ssd_2024_2015[ssd_2024] = ssd_2015

    @staticmethod
    def genera_mappa_ssd_2015_termini():
        if GestoreSSD.genera_mappa_ssd_2024_2015 is None:
            MessaggiErrore.errore(
                f"GestoreSSD.mappa_ssd_2024_2015 non inizializzata")

        GestoreSSD._mappa_ssd_2015_termini = {}

        # Itera sui valori unici di SSD 2015
        for ssd_2015 in set(GestoreSSD._mappa_ssd_2024_2015.values()):
            if isinstance(ssd_2015, str):
                # Rimuove tutto ciò che viene dopo '/'
                codice_troncato = ssd_2015.split('/')[0]
                # Trasforma il codice in minuscolo e sostituisce spazi o trattini con underscore
                codice_modificato = normalizza_nome(codice_troncato)
            else:
                # Gestisce valori non stringa
                codice_troncato = codice_modificato = ssd_2015

            if codice_troncato not in GestoreSSD._mappa_ssd_2024_2015:  # Evita duplicati
                GestoreSSD._mappa_ssd_2015_termini[codice_troncato] = codice_modificato

        # Aggiungi un valore predefinito per NULL
        GestoreSSD._mappa_ssd_2015_termini['NULL'] = 'null'

    @staticmethod
    def get_mappa_ssd_2024_2015():
        if GestoreSSD._mappa_ssd_2024_2015 is None:
            GestoreSSD.genera_mappa_ssd_2024_2015()

        return GestoreSSD._mappa_ssd_2024_2015

    @staticmethod
    def get_mappa_ssd_2015_termini():
        if GestoreSSD.genera_mappa_ssd_2015_termini is None:
            GestoreSSD.genera_mappa_ssd_2015_termini()

        return GestoreSSD._mappa_ssd_2015_termini

    @staticmethod
    def get_df():
        if GestoreSSD._df is None:
            MessaggiErrore.errore("GestoreSSD._df is None")
        return GestoreSSD._df

    @staticmethod
    def genera_fatti_settori():
        fatti_settori = {}

        for ssd_2015, termine in GestoreSSD._mappa_ssd_2015_termini.items():
            fatti_settori[ssd_2015] = f"settore({termine})."

        GestoreSSD._fatti_settori = fatti_settori

    @staticmethod
    def get_fatti_settori():
        if GestoreSSD._fatti_settori is None:
            GestoreSSD.genera_fatti_settori()
        return GestoreSSD._fatti_settori


class GestoreDocenti:
    _df_docenti = None
    _mappa_docenti = None
    _df_presidenti = None
    _mappa_presidenti = None
    _fatti_presidenti = None
    _fatti_contratti = None

    @staticmethod
    def inizializza(input_dir):
        """Carica i dati da un file CSV nel DataFrame condiviso."""
        file_docenti = os.path.join(input_dir, 'docenti.csv')

        df = carica_dati_csv(file_docenti)
        if df is None:
            MessaggiErrore.errore(
                f"Errore nel caricamento dei dati da {file_docenti}")

        GestoreDocenti._df_docenti = df

        file_presidenti = os.path.join(input_dir, 'presidenti.csv')
        df = carica_dati_csv(file_presidenti)
        if df is None:
            MessaggiErrore.errore(
                f"Errore nel caricamento dei dati da {file_presidenti}")

        GestoreDocenti._df_presidenti = df

    @staticmethod
    def genera_mappa_docenti():
        mappa_docenti = {}
        df = GestoreDocenti._df_docenti

        for _, riga in df.iterrows():
            matricola = int(riga['Matricola'])
            nome = riga['Cognome e Nome']

            mappa_docenti[matricola] = nome

        GestoreDocenti._mappa_docenti = mappa_docenti

    @staticmethod
    def get_mappa_docenti():
        if GestoreDocenti._mappa_docenti is None:
            GestoreDocenti.genera_mappa_docenti()

        return GestoreDocenti._mappa_docenti

    @staticmethod
    def get_df_docenti():
        if GestoreDocenti._df_docenti is None:
            MessaggiErrore.errore("GestoreDocenti._df_docenti is None")
        return GestoreDocenti._df_docenti

    @staticmethod
    def get_df_presidenti():
        if GestoreDocenti._df_presidenti is None:
            MessaggiErrore.errore("GestoreDocenti._df_presidenti is None")
        return GestoreDocenti._df_presidenti

    @staticmethod
    def genera_mappa_presidenti():
        mappa_presidenti = {}
        df = GestoreDocenti.get_df_presidenti()
        mappa_docenti = GestoreDocenti.get_mappa_docenti()

        for _, riga in df.iterrows():

            corso = int(riga['Matricola'])

            # Estrai il nome completo dalla seconda colonna (Nome Cognome)
            nome_cognome = riga['Nome e Cognome'].strip()
            if not nome_cognome:
                continue

            # Trova la matricola corrispondente
            matricola = find_matricola_by_name(nome_cognome, mappa_docenti)

            if not matricola:
                console.print(f"Nome: {nome_cognome}, Matricola non trovata")
                continue

            mappa_presidenti[corso] = matricola

        GestoreDocenti._mappa_presidenti = mappa_presidenti

    @staticmethod
    def get_mappa_presidenti():
        if GestoreDocenti._mappa_presidenti is None:
            GestoreDocenti.genera_mappa_presidenti()

        return GestoreDocenti._mappa_presidenti

    def genera_fatti_presidenti():
        fatti_presidenti = {}
        mappa_presidenti = GestoreDocenti._mappa_presidenti

        for corso, matricola in mappa_presidenti.items():
            fatto = f"presidente(docente({matricola}), corso({corso}))."
            fatti_presidenti[corso] = fatto

        GestoreDocenti._fatti_presidenti = fatti_presidenti

    @staticmethod
    def get_fatti_presidenti():
        if GestoreDocenti._fatti_presidenti is None:
            GestoreDocenti.genera_fatti_presidenti()

        return GestoreDocenti._fatti_presidenti

    @staticmethod
    def genera_fatti_contratti():
        fatti_docenti_tipo_contratto = {}
        df = GestoreDocenti.get_df_docenti()

        for _, riga in df.iterrows():

            valori = []
            matricola = riga['Matricola']
            if pd.isna(matricola):
                continue

            matricola = int(matricola)
            if (matricola in fatti_docenti_tipo_contratto and ('contratto' not in fatti_docenti_tipo_contratto[matricola])):
                continue

            fascia = riga['Fascia']
            if pd.isna(fascia):
                continue

            if 'ricercatore' in normalizza_nome(fascia):
                fascia = 'ricercatore'
            else:
                fascia = 'indeterminato'

            fatto = f"{fascia}(docente({matricola}))."
            fatti_docenti_tipo_contratto[matricola] = fatto

        GestoreDocenti._fatti_contratti = fatti_docenti_tipo_contratto

    @staticmethod
    def get_fatti_contratti():
        if GestoreDocenti._fatti_contratti is None:
            GestoreDocenti.genera_fatti_contratti()

        return GestoreDocenti._fatti_contratti


class GestoreCategorie:
    _df = None
    _mappa_corsi_categorie = None

    @staticmethod
    def inizializza(input_dir):
        """Carica i dati da un file CSV nel DataFrame condiviso."""
        file_jolly = os.path.join(input_dir, 'jolly.csv')

        df = carica_dati_csv(file_jolly)
        if df is None:
            MessaggiErrore.errore(
                f"Errore nel caricamento dei dati da {file_jolly}")

        GestoreCategorie._df = df

        mappa_corsi_categorie = {}
        categorie_descrizioni = {
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
                categoria = categorie_descrizioni[categoria]
            except Exception as e:
                # console.print(e)
                continue

            mappa_corsi_categorie[corso] = [categoria, 'null']

        GestoreCategorie._mappa_corsi_categorie = mappa_corsi_categorie

    @staticmethod
    def genera_mappa_corsi_categorie():
        mappa_corsi_categorie = {}
        categorie_descrizioni = {
            "5 DI CUI 3 PO/PA": "g5",
            "4 DI CUI 2 PO/PA": "g4",
            "3 DI CUI 1 PO/PA": "g3"
        }

        for _, riga in GestoreCategorie._df.iterrows():
            categoria = riga['Categoria']
            if (pd.isna(categoria)):
                continue

            try:
                corso = int(riga['Cod. Corso di Studio'])
                categoria = categorie_descrizioni[categoria]
            except Exception as e:
                # console.print(e)
                continue

            mappa_corsi_categorie[corso] = [categoria, 'null']

        GestoreCategorie._mappa_corsi_categorie = mappa_corsi_categorie

    @staticmethod
    def get_mappa_corsi_categorie():
        if GestoreCategorie._mappa_corsi_categorie is None:
            GestoreCategorie.genera_mappa_corsi_categorie()

        return GestoreCategorie._mappa_corsi_categorie


class GestoreCoperture:
    _df_coperture = None
    _corsi_da_filtrare = None
    _corsi_da_escludere = None

    _mappa_corsi_categorie = None

    _fatti_docenti = None
    _fatti_categorie_corsi = None
    _fatti_corsi = None
    _fatti_contratti = None
    _fatti_insegnamenti = None
    _fatti_insegna = None
    _fatti_settori_di_riferimento = None

    @staticmethod
    def inizializza(input_dir, corsi_da_filtrare, corsi_da_escludere):
        """Carica i dati da un file CSV nel DataFrame condiviso."""
        GestoreCoperture._corsi_da_filtrare = corsi_da_filtrare
        GestoreCoperture._corsi_da_escludere = corsi_da_escludere

        file_coperture = os.path.join(input_dir, 'coperture2425.csv')

        df = carica_dati_csv(file_coperture)
        if df is None:
            MessaggiErrore.errore(
                f"Errore nel caricamento dei dati da {file_coperture}")

        GestoreCoperture._df_coperture = df

    @staticmethod
    def genera():
        df = GestoreCoperture._df_coperture
        corsi_da_filtrare = GestoreCoperture._corsi_da_filtrare
        corsi_da_escludere = GestoreCoperture._corsi_da_escludere

        fatti_corsi = {}

        fatti_categorie_corsi = {}
        # carico le categorie speciali
        fatti_categorie_corsi['g5'] = 'categoria_corso(g5).'
        fatti_categorie_corsi['g4'] = 'categoria_corso(g4).'
        fatti_categorie_corsi['g3'] = 'categoria_corso(g3).'

        mappa_ssd_2024_2015 = GestoreMappe.get_mappa_ssd_2024_2015()
        mappa_ssd_2015_termini = GestoreMappe.get_mappa_ssd_2015_termini()
        mappa_corsi_categorie = GestoreMappe.get_mappa_corsi_categorie()

        fatti_contratti = GestoreMappe.get_fatti_contratti()

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
                # console.print(f'{cod_corso} escluso')
                continue
            if corsi_da_escludere and cod_corso in corsi_da_escludere:
                # console.print(f'{cod_corso} escluso')
                continue

            docente(fatti_docenti, riga, mappa_ssd_2024_2015,
                    mappa_ssd_2015_termini)
            categoria_corso(fatti_categorie_corsi, mappa_corsi_categorie, riga)
            corso(fatti_corsi, riga, mappa_corsi_categorie)
            docente_contratto(
                fatti_contratti, riga, fatti_docenti)
            insegnamento(fatti_insegnamenti, riga)
            insegna(fatti_insegna, riga)
            settori_di_riferimento(fatti_settori_di_riferimento, riga,
                                   mappa_ssd_2024_2015, mappa_ssd_2015_termini)

        GestoreCoperture._fatti_docenti = fatti_docenti
        GestoreCoperture._fatti_categorie_corsi = fatti_categorie_corsi
        GestoreCoperture._fatti_corsi = fatti_corsi
        GestoreCoperture._fatti_contratti = fatti_contratti
        GestoreCoperture._fatti_insegna = fatti_insegna
        GestoreCoperture._fatti_insegnamenti = fatti_insegnamenti
        GestoreCoperture._fatti_settori_di_riferimento = fatti_settori_di_riferimento

        GestoreCoperture._mappa_corsi_categorie = mappa_corsi_categorie

    @staticmethod
    def get_mappa_corsi_categorie():
        if GestoreCoperture._mappa_corsi_categorie is None:
            GestoreCoperture.genera()
        return GestoreCoperture._mappa_corsi_categorie

    @staticmethod
    def get_fatti_docenti():
        if GestoreCoperture._fatti_docenti is None:
            GestoreCoperture.genera()
        return GestoreCoperture._fatti_docenti

    @staticmethod
    def get_fatti_categorie_corsi():
        if GestoreCoperture._fatti_categorie_corsi is None:
            GestoreCoperture.genera()
        return GestoreCoperture._fatti_categorie_corsi

    @staticmethod
    def get_fatti_corsi():
        if GestoreCoperture._fatti_corsi is None:
            GestoreCoperture.genera()
        return GestoreCoperture._fatti_corsi

    @staticmethod
    def get_fatti_contratti():
        if GestoreCoperture._fatti_contratti is None:
            GestoreCoperture.genera()
        return GestoreCoperture._fatti_contratti

    @staticmethod
    def get_fatti_insegnamenti():
        if GestoreCoperture._fatti_insegnamenti is None:
            GestoreCoperture.genera()
        return GestoreCoperture._fatti_insegnamenti

    @staticmethod
    def get_fatti_insegna():
        if GestoreCoperture._fatti_insegna is None:
            GestoreCoperture.genera()
        return GestoreCoperture._fatti_insegna

    @staticmethod
    def get_fatti_settori_di_riferimento():
        if GestoreCoperture._fatti_settori_di_riferimento is None:
            GestoreCoperture.genera()
        return GestoreCoperture._fatti_settori_di_riferimento


class GestoreNumerosita:
    _input_dir = None
    _df_jolly = None
    _df_classi = None
    _df_numerosita_l = None
    _df_numerosita_lm = None
    _df_numerosita_cu = None

    _mappa_corsi_max = None
    _mappa_numerosita = None
    _fatti_garanti_per_corso = None

    @staticmethod
    def inizializza(input_dir):
        GestoreNumerosita._input_dir = input_dir

        file_csv_jolly = os.path.join(input_dir, 'numerosita/jolly.csv')
        file_csv_classi = os.path.join(input_dir, 'numerosita/classi.csv')
        file_csv_numerosita_l = os.path.join(
            input_dir, 'numerosita/numerosita_l.csv')
        file_csv_numerosita_lm = os.path.join(
            input_dir, 'numerosita/numerosita_lm.csv')
        file_csv_numerosita_cu = os.path.join(
            input_dir, 'numerosita/numerosita_cu.csv')

        # Caricamento jolly.csv
        df = carica_dati_csv(file_csv_jolly)
        if df is None:
            MessaggiErrore.errore(
                "Errore nel caricamento dei dati da `jolly.csv`")
        else:
            GestoreNumerosita._df_jolly = df

        # Caricamento classi.csv
        df = carica_dati_csv(file_csv_classi)
        if df is None:
            MessaggiErrore.errore(
                "Errore nel caricamento dei dati da `classi.csv`")
        else:
            GestoreNumerosita._df_classi = df

        # Caricamento numerosita_l.csv
        df = carica_dati_csv(file_csv_numerosita_l)
        if df is None:
            MessaggiErrore.errore(
                "Errore nel caricamento dei dati da `numerosita_l.csv`")
        else:
            GestoreNumerosita._df_numerosita_l = df

        # Caricamento numerosita_lm.csv
        df = carica_dati_csv(file_csv_numerosita_lm)
        if df is None:
            MessaggiErrore.errore(
                "Errore nel caricamento dei dati da `numerosita_lm.csv`")
        else:
            GestoreNumerosita._df_numerosita_lm = df

        # Caricamento numerosita_cu.csv
        df = carica_dati_csv(file_csv_numerosita_cu)
        if df is None:
            MessaggiErrore.errore(
                "Errore nel caricamento dei dati da `numerosita_cu.csv`")
        else:
            GestoreNumerosita._df_numerosita_cu = df

    @staticmethod
    def genera():
        df = GestoreNumerosita._df_jolly
        mappa_corso_classe = {}
        for _, riga in df.iterrows():

            classe = riga['Classe']
            corso = int(riga['Cod. Corso di Studio'])

            if corso is None or classe is None:
                console.print(f"corso is {corso}")
                console.print(f"classe is {classe}")

            mappa_corso_classe[corso] = classe

        df = GestoreNumerosita._df_classi
        mappa_classe_area = {}
        for _, riga in df.iterrows():

            classe = riga['CLASSE']
            area = riga['AREA']

            if classe is None or area is None:
                console.print(f"area is {area}")
                console.print(f"classe is {classe}")

            mappa_classe_area[classe] = area

        df_l = GestoreNumerosita._df_numerosita_l
        mappa_area_max_l = {}
        for _, riga in df_l.iterrows():

            area = riga['Cod. Area']
            max = riga['Massimo']

            if area is None or max is None:
                console.print(f"area is {area}")
                console.print(f"max is {max}")

            mappa_area_max_l[area] = max

        df_lm = GestoreNumerosita._df_numerosita_lm
        mappa_area_max_lm = {}
        for _, riga in df_lm.iterrows():

            area = riga['Cod. Area']
            max = riga['Massimo']

            if area is None or max is None:
                console.print(f"area is {area}")
                console.print(f"max is {max}")

            mappa_area_max_lm[area] = max

        df_cu = GestoreNumerosita._df_numerosita_cu
        mappa_area_max_cu = {}
        for _, riga in df_cu.iterrows():

            area = riga['Cod. Area']
            max = riga['Massimo']

            if area is None or max is None:
                console.print(f"area is {area}")
                console.print(f"max is {max}")

            mappa_area_max_cu[area] = max

        mappa_corsi_max = {}
        mappa_corsi_categorie = GestoreMappe.get_mappa_corsi_categorie()
        for corso, classe in mappa_corso_classe.items():
            try:
                # console.print(f"corso: {corso}")
                classe = mappa_corso_classe[corso]
                # console.print(f"classe: {classe}")
                area = mappa_classe_area[classe]
                # console.print(f"area: {area}")

                categoria = mappa_corsi_categorie[corso][1]
                # console.print(f"categoria: {categoria}")
                if categoria == "l":
                    max = mappa_area_max_l[area]
                elif categoria == "lm":
                    max = mappa_area_max_lm[area]
                else:
                    max = mappa_area_max_cu[area]

                mappa_corsi_max[corso] = max
            except Exception as e:
                console.print(f"[red]genera_mappa_corsi_max errore su {
                    corso}: {e}[/red]")
                continue

        GestoreNumerosita._mappa_corsi_max = mappa_corsi_max

        mappa_numerosita = {}
        carica_numerosita(mappa_numerosita, GestoreNumerosita._mappa_corsi_max,
                          GestoreNumerosita._input_dir)
        GestoreNumerosita._mappa_numerosita = mappa_numerosita

        GestoreNumerosita.genera_fatti_garanti_per_corso()

    @staticmethod
    def genera_fatti_garanti_per_corso():
        fatti_garanti_per_corso = {}

        garanti_per_corso(fatti_garanti_per_corso, GestoreMappe.get_mappa_corsi_categorie(
        ), GestoreNumerosita.get_mappa_numerosita())
        GestoreNumerosita._fatti_garanti_per_corso = fatti_garanti_per_corso

    @staticmethod
    def get_mappa_corsi_max():
        if GestoreNumerosita._mappa_corsi_max is None:
            GestoreNumerosita.genera()
        return GestoreNumerosita._mappa_corsi_max

    @staticmethod
    def get_mappa_numerosita():
        if GestoreNumerosita._mappa_numerosita is None:
            GestoreNumerosita.genera()
        return GestoreNumerosita._mappa_numerosita

    @staticmethod
    def get_fatti_garanti_per_corso():
        if GestoreNumerosita._fatti_garanti_per_corso is None:
            GestoreNumerosita.genera()
        return GestoreNumerosita._fatti_garanti_per_corso


class GestoreMappe:

    @staticmethod
    def inizializza(input_dir, corsi_da_filtrare, corsi_da_escludere):
        GestoreSSD.inizializza(input_dir)
        GestoreSSD.genera_mappa_ssd_2024_2015()
        GestoreSSD.genera_mappa_ssd_2015_termini()

        GestoreDocenti.inizializza(input_dir)

        GestoreCategorie.inizializza(os.path.join(input_dir, 'numerosita'))
        GestoreCategorie.genera_mappa_corsi_categorie()
        GestoreCoperture.inizializza(
            input_dir, corsi_da_filtrare, corsi_da_escludere)
        GestoreCoperture.genera()

        GestoreNumerosita.inizializza(input_dir)
        GestoreNumerosita.genera()

    @staticmethod
    def get_mappa_ssd_2024_2015():
        return GestoreSSD.get_mappa_ssd_2024_2015()

    @staticmethod
    def get_mappa_ssd_2015_termini():
        return GestoreSSD.get_mappa_ssd_2015_termini()

    @staticmethod
    def get_fatti_settori():
        return GestoreSSD.get_fatti_settori()

    @staticmethod
    def get_df_docenti():
        return GestoreDocenti.get_df_docenti()

    @staticmethod
    def get_mappa_docenti():
        return GestoreDocenti.get_mappa_docenti()

    @staticmethod
    def get_mappa_presidenti():
        return GestoreDocenti.get_mappa_presidenti()

    @staticmethod
    def get_fatti_presidenti():
        return GestoreDocenti.get_fatti_presidenti()

    @staticmethod
    def get_fatti_contratti():
        return GestoreDocenti.get_fatti_contratti()

    @staticmethod
    def get_mappa_corsi_categorie():
        return GestoreCategorie.get_mappa_corsi_categorie()

    @staticmethod
    def get_fatti_categorie_corsi():
        return GestoreCoperture.get_fatti_categorie_corsi()

    @staticmethod
    def get_fatti_docenti():
        return GestoreCoperture.get_fatti_docenti()

    @staticmethod
    def get_fatti_settori_di_riferimento():
        return GestoreCoperture.get_fatti_settori_di_riferimento()

    @staticmethod
    def get_fatti_corsi():
        return GestoreCoperture.get_fatti_corsi()

    @staticmethod
    def get_fatti_insegna():
        return GestoreCoperture.get_fatti_insegna()

    @staticmethod
    def get_fatti_insegnamenti():
        return GestoreCoperture.get_fatti_insegnamenti()

    @staticmethod
    def get_mappa_corsi_max():
        return GestoreNumerosita.get_mappa_corsi_max()

    @staticmethod
    def get_mappa_numerosita():
        return GestoreNumerosita.get_mappa_numerosita()

    @staticmethod
    def get_fatti_garanti_per_corso():
        return GestoreNumerosita.get_fatti_garanti_per_corso()


# Funzione per trovare la matricola in base al nome del docente
def find_matricola_by_name(nome_docente, mappa_docenti):
    for matricola, nome in mappa_docenti.items():
        # Usa regex per fare un match tra il nome e il nome completo nel CSV
        # La regex è case-insensitive grazie a re.IGNORECASE
        if re.search(r'\b' + re.escape(nome_docente) + r'\b', nome, re.IGNORECASE):
            return matricola
    return None  # Nessun match trovato

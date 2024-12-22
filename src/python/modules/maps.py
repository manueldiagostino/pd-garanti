import stat
from typing import NoReturn
import stat
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
                valori.append('ricercatore')
            else:
                valori.append('indeterminato')

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


base_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "../../"))

input_dir = os.path.join(base_dir, "input")
print(input_dir)
asp_dir = os.path.join(base_dir, "src/asp")
facts_dir = os.path.join(asp_dir, "facts")
results_dir = os.path.join(asp_dir, "results")


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


def genera_mappa_corso_max(mappa_corso_categoria, input_dir):
    mappa_corso_max = {}

    file_csv_jolly = os.path.join(input_dir, 'numerosita/jolly.csv')

    file_csv_classi = os.path.join(input_dir, 'numerosita/classi.csv')

    file_csv_numerosita_l = os.path.join(
        input_dir, 'numerosita/numerosita_l.csv')
    file_csv_numerosita_lm = os.path.join(
        input_dir, 'numerosita/numerosita_lm.csv')
    file_csv_numerosita_cu = os.path.join(
        input_dir, 'numerosita/numerosita_cu.csv')

    df = carica_dati_csv(file_csv_jolly)
    if df is None:
        console.print("Errore nel caricamento dei dati da `jolly.csv`")
        return None

    # Creazione mappa
    mappa_corso_classe = {}
    for _, riga in df.iterrows():

        classe = riga['Classe']
        corso = int(riga['Cod. Corso di Studio'])

        if corso is None or classe is None:
            console.print(f"corso is {corso}")
            console.print(f"classe is {classe}")

        mappa_corso_classe[corso] = classe

    df = carica_dati_csv(file_csv_classi)
    if df is None:
        console.print("Errore nel caricamento dei dati da `classi.csv`")
        return None

    # Creazione mappa
    mappa_classe_area = {}
    for _, riga in df.iterrows():

        classe = riga['CLASSE']
        area = riga['AREA']

        if classe is None or area is None:
            console.print(f"area is {area}")
            console.print(f"classe is {classe}")

        mappa_classe_area[classe] = area

    df_l = carica_dati_csv(file_csv_numerosita_l)
    if df_l is None:
        console.print("Errore nel caricamento dei dati da `numerosita_l.csv`")
        return None

    mappa_area_max_l = {}
    for _, riga in df_l.iterrows():

        area = riga['Cod. Area']
        max = riga['Massimo']

        if area is None or max is None:
            console.print(f"area is {area}")
            console.print(f"max is {max}")

        mappa_area_max_l[area] = max

    df_lm = carica_dati_csv(file_csv_numerosita_lm)
    if df_lm is None:
        console.print("Errore nel caricamento dei dati da `numerosita_lm.csv`")
        return None

    mappa_area_max_lm = {}
    for _, riga in df_lm.iterrows():

        area = riga['Cod. Area']
        max = riga['Massimo']

        if area is None or max is None:
            console.print(f"area is {area}")
            console.print(f"max is {max}")

        mappa_area_max_lm[area] = max

    df_cu = carica_dati_csv(file_csv_numerosita_cu)
    if df_cu is None:
        console.print("Errore nel caricamento dei dati da `numerosita_cu.csv`")
        return None

    mappa_area_max_cu = {}
    for _, riga in df_cu.iterrows():

        area = riga['Cod. Area']
        max = riga['Massimo']

        if area is None or max is None:
            console.print(f"area is {area}")
            console.print(f"max is {max}")

        mappa_area_max_cu[area] = max

    console.print(mappa_corso_categoria)
    for corso, classe in mappa_corso_classe.items():
        try:
            # console.print(f"corso: {corso}")
            classe = mappa_corso_classe[corso]
            # console.print(f"classe: {classe}")
            area = mappa_classe_area[classe]
            # console.print(f"area: {area}")

            categoria = mappa_corso_categoria[corso][1]
            # console.print(f"categoria: {categoria}")
            if categoria == "l":
                max = mappa_area_max_l[area]
            elif categoria == "lm":
                max = mappa_area_max_lm[area]
            else:
                max = mappa_area_max_cu[area]

            mappa_corso_max[corso] = max
        except Exception as e:
            console.print(f"[red]genera_mappa_corso_max errore su {
                          corso}: {e}[/red]")
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


def genera_mappa_docenti_settore(df):
    mappa_docenti_settore = {}

    for _, riga in df.iterrows():
        matricola = int(riga['Matricola'])
        settore = riga['SSD 2024']

        mappa_docenti_settore[matricola] = settore

    return mappa_docenti_settore


def genera_mappa_presidenti(mappa_docenti, file_csv_presidenti):
    mappa_presidenti = {}

    df = carica_dati_csv(file_csv_presidenti)
    if df is None:
        console.print("Errore nel caricamento dei dati da `presidenti.csv`")
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
            console.print(f"Nome: {nome_cognome}, Matricola non trovata")
            continue

        mappa_presidenti[corso] = matricola

    return mappa_presidenti


def genera_mappa_corso_categoria(input_dir):
    mappa_corso_categoria = {}

    file_csv_jolly = os.path.join(input_dir, 'numerosita/jolly.csv')
    df = carica_dati_csv(file_csv_jolly)
    if df is None:
        console.print("Errore nel caricamento dei dati da `jolly.csv`")
        return None

    categorie_descrizione = {
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
            categoria = categorie_descrizione[categoria]
        except Exception as e:
            console.print(e)
            continue

        # console.print(f"corso:{corso}, categoria: {categoria}")
        mappa_corso_categoria[corso] = [categoria, 'null']

    return mappa_corso_categoria

from modules.maps import (
    mappa_settori_nuovi_vecchi,
    mappa_settori_termini,
    genera_mappa_corso_categoria,
    genera_mappa_corso_max,
    genera_mappa_docenti,
    genera_mappa_presidenti
)
from modules.solver import (
    solve_program
)
from modules.stats import (
    carica_numerosita
)
from modules.facts import (
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
from modules.wfacts import (
    write_dic,
    write_set
)
from modules.csv_loader import (
    carica_dati_csv,
    normalizza_nome
)
import argparse
import os

from rich.console import Console
console = Console()


base_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "../../"))

input_dir = os.path.join(base_dir, "input")
print(input_dir)
asp_dir = os.path.join(base_dir, "src/asp")
facts_dir = os.path.join(asp_dir, "facts")
results_dir = os.path.join(asp_dir, "results")


def genera_fatti(corsi_da_filtrare, corsi_da_escludere, dir):
    """Legge il file CSV, genera i fatti per ogni gruppo e li scrive nel file."""

    # Carica i dati
    file_csv_docenti = os.path.join(input_dir, "docenti.csv")
    df = carica_dati_csv(file_csv_docenti)
    if df is None:
        console.print(f"Errore nel caricamento dei dati da {file_csv_docenti}")
        return

    mappa_ssd = mappa_settori_nuovi_vecchi(df)
    mappa_ssd_termine = mappa_settori_termini(mappa_ssd)

    fatti_settori = {}
    settori(fatti_settori, mappa_ssd_termine)
    write_dic(fatti_settori, dir, 'settori.asp')

    mappa_docenti = genera_mappa_docenti(df)
    mappa_presidenti = genera_mappa_presidenti(
        mappa_docenti, os.path.join(input_dir, 'presidenti.csv'))
    fatti_presidenti = {}
    presidenti(fatti_presidenti, mappa_presidenti)
    write_dic(fatti_presidenti, dir, 'presidenti.asp')

    fatti_docenti_tipo_contratto = {}
    for _, riga in df.iterrows():
        # Estraggo i docenti ricercatori/tempo indeterminato
        docente_indeterminato_ricercatore(
            fatti_docenti_tipo_contratto, riga)

    file_csv_coperture = os.path.join(input_dir, "coperture2425.csv")
    df = carica_dati_csv(file_csv_coperture)
    if df is None:
        console.print(f"Errore nel caricamento dei dati da {
                      file_csv_coperture}")
        return

    fatti_corsi_di_studio = {}

    fatti_categorie_corso = {}
    categoria_corso_speciali(fatti_categorie_corso)

    fatti_docenti = {}
    fatti_insegnamenti = {}
    fatti_insegna = set()
    fatti_settori_di_riferimento = set()

    mappa_corso_categoria = genera_mappa_corso_categoria(input_dir)

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

        # Estraggo i docenti
        docente(fatti_docenti, riga, mappa_ssd, mappa_ssd_termine)
        # Estraggo le categoria_corso
        categoria_corso(fatti_categorie_corso, mappa_corso_categoria, riga)
        # Estraggo i corsi
        corso(fatti_corsi_di_studio, riga, mappa_corso_categoria)
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

    mappa_corso_max = genera_mappa_corso_max(mappa_corso_categoria, input_dir)
    mappa_numerosita = {}
    carica_numerosita(mappa_numerosita, mappa_corso_max, input_dir)

    fatti_garanti_per_corso = {}
    garanti_per_corso(fatti_garanti_per_corso,
                      mappa_corso_categoria, mappa_numerosita)

    # Stampo i fatti nei rispettivi file
    write_dic(fatti_categorie_corso, facts_dir, 'categorie_corso.asp')
    write_dic(fatti_docenti, facts_dir, 'docenti.asp')
    write_dic(fatti_corsi_di_studio, facts_dir, 'corsi_di_studio.asp')
    write_dic(fatti_docenti_tipo_contratto, facts_dir, 'contratti.asp')
    write_dic(fatti_insegnamenti, facts_dir, 'insegnamenti.asp')
    write_set(fatti_insegna, facts_dir, 'insegna.asp')
    write_set(fatti_settori_di_riferimento,
              facts_dir, 'settori_di_riferimento.asp')
    write_dic(fatti_garanti_per_corso, facts_dir, 'garanti_per_corso.asp')


class ClingoArgsAction(argparse.Action):
    """
    Azione personalizzata per convertire gli argomenti di Clingo in una lista.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values.split() if values else [])


def parse_arguments():
    """Crea e configura il parser degli argomenti."""
    parser = argparse.ArgumentParser(description="Genera fatti ASP.")
    parser.add_argument(
        "--filter", type=str,
        help="Lista di ID di corsi separati da virgola da considerare.",
        default=None
    )
    parser.add_argument(
        "--exclude", type=str,
        help="Lista di ID di corsi separati da virgola da escludere.",
        default=None
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Abilita la modalità verbose per il solver.")
    parser.add_argument(
        "--mode", type=str, choices=["full", "gringo", "clingo", "none"],
        default="full", help="Modalità di esecuzione: full (rigenera i fatti), gringo, clingo, none (rigenera solo i fatti).")
    parser.add_argument(
        "--clingo-args", action=ClingoArgsAction, type=str, help="Argomenti classici di Clingo separati da spazio.", default="")
    return parser.parse_args()


def main():
    args = parse_arguments()

    # Ottieni i filtri (se presenti)
    corsi_da_filtrare = set(
        map(int, args.filter.split(','))) if args.filter else set()
    corsi_da_escludere = set(
        map(int, args.exclude.split(','))) if args.exclude else set()

    nuovi_2024 = [
        3072, 3071, 3070, 5008, 5009, 5063, 3021, 3065, 5081, 3055,
        5082, 5051, 5057, 5070
    ]
    corsi_da_escludere.update(nuovi_2024)

    # Creo cartella di output
    if not os.path.exists(facts_dir):
        os.makedirs(facts_dir)

    if args.mode in ["full", "none"]:
        # Genera i fatti
        genera_fatti(corsi_da_filtrare, corsi_da_escludere, facts_dir)

    # Chiamata al solver in base alla modalità specificata
    if args.mode == "none":
        console.print(
            "Solver disabilitato. Fatti generati senza eseguire il solver.")
    else:
        solve_program(mode=args.mode, verbose=args.verbose,
                      arguments=args.clingo_args)


if __name__ == "__main__":
    main()

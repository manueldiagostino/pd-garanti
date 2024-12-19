import signal
import os
import clingo

from rich.console import Console
console = Console()

# Percorso principale del progetto
base_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "../../../src"))
print(base_dir)


# Directory per gli script ASP
asp_dir = os.path.join(base_dir, "asp")
facts_dir = os.path.join(asp_dir, "facts")
results_dir = os.path.join(asp_dir, "results")

# File principali
files_to_include = [
    os.path.join(asp_dir, "main.lp"),
    os.path.join(asp_dir, "preferenze.lp")
]

# Funzione per leggere i file dalla directory dei facts


def read_files(directory):
    content = ""
    console.print(f"Lettura file dalla directory: {directory}")
    for filename in sorted(os.listdir(directory)):  # Ordine deterministico
        if filename.endswith(".asp"):
            console.print(f"Leggendo il file: {filename}")
            with open(os.path.join(directory, filename), "r") as file:
                content += file.read() + "\n"
    return content

# Leggi il contenuto dei file ASP


def load_program():
    # Leggi i facts
    facts_content = read_files(facts_dir)
    # Leggi i file principali
    program_content = ""
    for file in files_to_include:
        if not os.path.exists(file):
            raise FileNotFoundError(f"File non trovato: {file}")
        with open(file, "r") as f:
            program_content += f.read() + "\n"
    return program_content + facts_content


# Flag per interrompere il solving
stop_solving = False


def signal_handler(signum, frame):
    """Gestore dei segnali per Ctrl+C."""
    global stop_solving
    stop_solving = True
    console.print(
        "[bold yellow]Ricevuto Ctrl+C: interruzione in corso...[/bold yellow]")


def solve_program(mode="full", verbose=True, arguments=[]):
    """
    Esegue il solver con la modalità specificata.

    Args:
        mode (str): Modalità di esecuzione. Può essere "full", "gringo", o "clingo".
        verbose (bool): Se True, stampa i dettagli delle soluzioni.
        arguments (list): Argomenti da passare al controllo di Clingo.
    """
    global stop_solving
    stop_solving = False  # Resetta il flag all'inizio
    # Imposta il gestore per Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    try:
        complete_program = load_program()  # Funzione che carica il programma ASP
        results_file = os.path.join(results_dir, "solution.txt")

        # Pulisce il file dei risultati se esiste
        if os.path.exists(results_file):
            os.remove(results_file)

        def on_model(model):
            if stop_solving:
                ctl.interrupt()  # Interrompe la ricerca in corso
                raise KeyboardInterrupt  # Genera un'interruzione

            model_symbols = model.symbols(atoms=True)
            with open(results_file, "a") as f:
                f.write(f"Model trovato: {model_symbols}\n")
            if verbose:
                console.print(
                    f"[bold green]Model trovato: [/bold green]")
                print(model_symbols)

        ctl = clingo.Control(arguments)
        ctl.add("base", [], complete_program)
        ctl.ground([("base", [])])

        console.print("[bold blue]Avvio del solving...[/bold blue]")
        result = ctl.solve(on_model=on_model)

        if stop_solving:
            console.print(
                "[bold yellow]Esecuzione interrotta dall'utente.[/bold yellow]")
        elif result.satisfiable:
            console.print(
                f"[bold green]Soluzione trovata![/bold green] Risultati salvati in: [magenta]{results_file}[/magenta]")
        else:
            console.print("[bold red]Nessuna soluzione trovata.[/bold red]")

    except KeyboardInterrupt:
        console.print(
            "[bold yellow]Esecuzione interrotta manualmente.[/bold yellow]")
    except FileNotFoundError as e:
        console.print(f"[bold red]Errore:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]Errore durante il solving:[/bold red] {e}")
    finally:
        # Ripristina il comportamento predefinito
        signal.signal(signal.SIGINT, signal.SIG_DFL)


# Esegui solo se lo script è chiamato direttamente
if __name__ == "__main__":
    # Modalità di default
    solve_program(verbose="verbose")

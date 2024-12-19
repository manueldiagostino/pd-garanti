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


def solve_program(verbose="verbose"):
    """
    Esegue il solver con la modalità specificata.

    Args:
        mode (str): Modalità di esecuzione. Può essere "verbose", "quiet", o "none".
    """
    if verbose == "none":
        return

    try:
        complete_program = load_program()
        results_file = os.path.join(results_dir, "solution.txt")

        # Pulisce il file dei risultati se esiste
        if os.path.exists(results_file):
            os.remove(results_file)

        def on_model(model):
            model_symbols = model.symbols(atoms=True)
            with open(results_file, "a") as f:
                f.write(f"Model trovato:{model_symbols}\n")
            if verbose == "verbose":
                print(
                    f"Model trovato: {model_symbols}")

        ctl = clingo.Control(
            arguments=['-n', '2']
        )
        ctl.add("base", [], complete_program)
        ctl.ground([("base", [])])
        result = ctl.solve(on_model=on_model)

        if result.satisfiable:
            if verbose in ["verbose", "quiet"]:
                console.print(f"Soluzione trovata! Risultati salvati in: [magenta]{
                              results_file}[/magenta]")
        else:
            console.print("Nessuna soluzione trovata.")
    except FileNotFoundError as e:
        console.print(f"Errore: {e}")
    except Exception as e:
        console.print(f"Errore durante il solving: {e}")


# Esegui solo se lo script è chiamato direttamente
if __name__ == "__main__":
    # Modalità di default
    solve_program(verbose="verbose")

import os

from rich.console import Console
from rich.table import Table

console = Console()


def write_dic(fatti, dir_output, nome_file):
    # Stampo i fatti nei rispettivi file
    file_output = os.path.join(
        dir_output, f"{nome_file}")
    with open(file_output, 'w', encoding='utf-8') as f:
        for fatto in fatti.values():
            f.write(f"{fatto}\n")
    console.print(f"[bold magenta]{file_output}[/bold magenta] scritto")


def write_set(fatti, dir_output, nome_file):
    # Stampo i fatti nei rispettivi file
    file_output = os.path.join(
        dir_output, f"{nome_file}")
    with open(file_output, 'w', encoding='utf-8') as f:
        for fatto in fatti:
            f.write(f"{fatto}\n")
    console.print(f"[bold magenta]{file_output}[/bold magenta] scritto")

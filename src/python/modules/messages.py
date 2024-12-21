from rich.panel import Panel
from rich.text import Text
from rich.console import Console


class MessaggiErrore:
    _console = Console()

    @staticmethod
    def errore(messaggio: str, titolo: str = "Errore"):
        """Mostra un messaggio di errore in un pannello rosso e lancia un'eccezione."""
        pannello = Panel(Text(messaggio, style="bold red"),
                         title=titolo, border_style="red")
        MessaggiErrore._console.print(pannello)
        raise ValueError(messaggio)

    @staticmethod
    def avviso(messaggio: str, titolo: str = "Avviso"):
        """Mostra un messaggio di avviso in un pannello giallo e lancia un'eccezione Warning."""
        pannello = Panel(Text(messaggio, style="bold yellow"),
                         title=titolo, border_style="yellow")
        MessaggiErrore._console.print(pannello)
        raise Warning(messaggio)

    @staticmethod
    def successo(messaggio: str, titolo: str = "Successo"):
        """Mostra un messaggio di successo in un pannello verde."""
        pannello = Panel(Text(messaggio, style="bold green"),
                         title=titolo, border_style="green")
        MessaggiErrore._console.print(pannello)
        # Nessuna eccezione, perché indica che tutto è andato a buon fine.

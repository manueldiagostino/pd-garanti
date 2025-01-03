# pd-garanti

Progetto del corso di Programmazione Dichiarativa (6 CFU)

Ottimizzazione Coperture Garanti Accademici

## Esecuzione

È necessario aver installato [Anaconda](https://docs.anaconda.com/anaconda/install/) o [Miniconda](https://docs.anaconda.com/miniconda/install/).

Procedere poi creando l'environment di esecuzione a partire dal file
`environment.yml`:

```bash
conda env create -n garanti --file environment.yml
```

e attivarlo:

```bash
conda activate garanti
```

A questo punto è possibile eseguire il programma tramite

```bash
python src/python/main.py
```

### Opzioni

```bash
usage: main.py [-h] [--filter FILTER] [--exclude EXCLUDE] [--verbose]
               [--mode {full,clingo,none}] [--clingo-args CLINGO_ARGS]

Genera fatti ASP.

options:
  -h, --help            show this help message and exit
  --filter FILTER       Lista di ID di corsi separati da virgola da considerare.
  --exclude EXCLUDE     Lista di ID di corsi separati da virgola da escludere.
  --verbose             Abilita la modalità verbose per il solver.
  --mode {full,clingo,none}
                        Modalità di esecuzione: full (rigenera i fatti), clingo (esegue
                        solo il solver), none (rigenera solo i fatti).
  --clingo-args CLINGO_ARGS
                        Argomenti per Clingo separati da spazio.
```

## Risultati

In caso di riuscita dell'esecuzione, apparirà il messaggio:

```bash
Soluzione trovata! Risultati salvati in:
src/asp/results/solution.txt
Tabella generata con successo! Salvata in:
src/asp/results/table.xlsx
```

in cui è indicato il percorso della tabella dei risultati.

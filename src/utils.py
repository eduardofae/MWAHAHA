from enum import Enum

class InputTypes(Enum):
    WP = 'word_pair'
    HL = 'headline'

import pandas as pd
def read_data(path: str = 'data/corpus/task-a-en.tsv') -> list[tuple[str, str, InputTypes]]:
    return [
        (input['id'], f'{input['word1']}, {input['word2']}', InputTypes.WP)
        if input['headline'] == '-'
        else (input['id'], input['headline'], InputTypes.HL)
        for _, input in 
        pd.read_csv(path, sep = '\t').iterrows()
    ]

from pathlib import Path
def write_data(data: str, path: str = 'data/outs/jokes.csv') -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    pd.Series(data).to_csv(file_path, index=False, header=['Jokes'])

def get_last_processed_id(path: str = 'data/outs/jokes.csv') -> str | None:
    """Get the ID of the last processed joke from the output file."""
    file_path = Path(path)
    if not file_path.exists():
        return None
    
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return None
        return df['id'].iloc[-1]
    except Exception:
        return None

def append_joke(joke_id: str, joke: str, path: str = 'data/outs/jokes.csv', is_first: bool = False) -> None:
    """Append a single joke with its ID to the output file."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    mode = 'w' if is_first else 'a'
    with open(file_path, mode, encoding='utf-8') as f:
        if is_first:
            f.write('id,joke\n')  # Write header for first joke
        # Escape quotes and handle newlines for CSV format
        escaped_joke = joke.replace('"', '""')
        if ',' in joke or '\n' in joke or '"' in joke:
            f.write(f'{joke_id},"{escaped_joke}"\n')
        else:
            f.write(f'{joke_id},{escaped_joke}\n')
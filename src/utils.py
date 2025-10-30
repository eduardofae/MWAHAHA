from enum import Enum

class InputTypes(Enum):
    WP = 'word_pair'
    HL = 'headline'

import pandas as pd
def read_data(path: str = 'data/corpus/task-a-en.tsv') -> list[tuple[str, InputTypes]]:
    return [
        (f'{input['word1']}, {input['word2']}', InputTypes.WP)
        if input['headline'] == '-'
        else (input['headline'], InputTypes.HL)
        for _, input in 
        pd.read_csv(path, sep = '\t').iterrows()
    ]

from pathlib import Path
def write_data(data: str, path: str = 'data/outs/jokes.csv') -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    pd.Series(data).to_csv(file_path, index=False, header=['Jokes'])
from judge import Judge
from utils import InputTypes, DEFAULT_JOKES_PATH, DEFAULT_INPUT_PATH, read_jokes, read_inputs, write_data
from agent import DEFAULT_MODEL, DEFAULT_BACKEND
import numpy as np
from dataclasses import dataclass, asdict
from typing import Optional
from tqdm import trange
import json
from pathlib import Path

@dataclass
class Match():
    id: str
    input: str
    input_type: InputTypes
    models: list[str]
    jokes: list[str]
    winner: Optional[str] = None

class Arena():
    out_path = 'data/outs/arena.json'

    def __init__(
        self, 
        judge_model: str = DEFAULT_MODEL,
        judge_backend: str = DEFAULT_BACKEND,
        inputs_path: str = DEFAULT_INPUT_PATH,
        jokes_path: str = DEFAULT_JOKES_PATH
    ):
        # Create judge for each input type with the specified model/backend
        self.judges = {
            input_type: Judge(input_type, model=judge_model, backend=judge_backend)
            for input_type in InputTypes
        }
        self.inputs = read_inputs(inputs_path)
        self.jokes = read_jokes(jokes_path)

    def _gen_match(self) -> Match:
        input = self.inputs[
            np.random.choice(len(self.inputs))
        ]
        possible_jokes = self.jokes[input[0]]
        chosen_jokes = [
            possible_jokes[i]
            for i in 
            np.random.choice(len(possible_jokes), 2, replace=False)
        ]
        chosen_jokes = list(zip(*chosen_jokes))
        return Match(
            input[0], input[1], input[2],
            chosen_jokes[0], chosen_jokes[1]
        )

    def match(self, match: Match) -> str:
        judge = self.judges[match.input_type]
        winner = judge.select(match.input, match.jokes)
        return match.models[winner]

    def run(self, num_matches: int = 50) -> None:
        winners = []
        for _ in trange(num_matches):
            match = self._gen_match()
            match.winner = self.match(match)
            winners.append(asdict(match))
        self.save(winners)
    
    def save(self, results: list[Match]):
        file_path = Path(self.out_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        open(file_path, 'w', encoding='utf-8').write(json.dumps(results))

arena = Arena()
arena.run(5)
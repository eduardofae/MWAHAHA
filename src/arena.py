from judge import Judge
from agent import DEFAULT_MODEL, DEFAULT_BACKEND
from utils import InputTypes, DEFAULT_JOKES_PATH, DEFAULT_INPUT_PATH, read_jokes, read_inputs
import numpy as np

# Typing
from dataclasses import dataclass, asdict
from typing import Optional

# Progress Bar
from tqdm import trange

# Store/Load Data
import json
from pathlib import Path

DEFAULT_MODELS_PATH = 'data/outs/models.json'
DEFAULT_OUTPUT_PATH = 'data/outs/arena.jsonl'

@dataclass
class Model():
    name: str
    elo: float
    wins: int
    n_matches: int

@dataclass
class Match():
    id: str
    input: str
    input_type: InputTypes
    models: list[str]
    jokes: list[str]
    winner: Optional[str] = None

class Arena():
    def __init__(
        self, 
        judge_model: str = DEFAULT_MODEL,
        judge_backend: str = DEFAULT_BACKEND,
        inputs_path: str = DEFAULT_INPUT_PATH,
        jokes_path: str = DEFAULT_JOKES_PATH,
        models_path: str = DEFAULT_MODELS_PATH,
        out_path: str = DEFAULT_OUTPUT_PATH
    ):
        # Create judge for each input type with the specified model/backend
        self.judges = {
            input_type: Judge(input_type, model=judge_model, backend=judge_backend)
            for input_type in InputTypes
        }
        self.out_path = out_path
        self.models_path = models_path
        self.inputs = read_inputs(inputs_path)
        self.jokes = read_jokes(jokes_path)
        self.models = self._get_models()

    def _get_models(self) -> list[Model]:
        file_path = Path(self.models_path)
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            first_joke_key = next(iter(self.jokes))
            return { 
                joke.model: Model(joke.model, 0.0, 0, 0)
                for joke in self.jokes[first_joke_key]
            }
        else:
            return {
                model['name']: Model(**model)
                for model in json.loads(
                    open(file_path, 'r', encoding='utf-8')\
                        .read()
                )
            }

    def _gen_match(self) -> Match:
        input = np.random.choice(self.inputs)
        possible_jokes = self.jokes[input.id]
        chosen_jokes = np.random.choice(possible_jokes, 2, replace=False)
        models = [joke.model for joke in chosen_jokes]
        jokes  = [joke.joke  for joke in chosen_jokes]
        return Match(
            input.id, input.input, input.input_type,
            models, jokes
        )
    
    def _update_models(self, models: tuple[str, str], winner: str) -> None:
        for model_name in models:
            model = self.models[model_name]
            model.n_matches += 1
            if model_name == winner:
                model.wins += 1

    def _run_match(self, match: Match) -> str:
        judge = self.judges[match.input_type]
        winner_id = judge.select(match.input, match.jokes)
        winner = match.models[winner_id]
        self._update_models(match.models, winner)
        return winner

    def run(self, num_matches: int = 50) -> None:
        for _ in trange(num_matches):
            match = self._gen_match()
            match.winner = self._run_match(match)
            self._save(match)
    
    def _save(self, result: Match):
        # Save Match
        file_path = Path(self.out_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        result_dict = asdict(result)
        open(file_path, 'a', encoding='utf-8')\
            .write(json.dumps(result_dict) + '\n')
        
        # Save Leaderboard State
        file_path = Path(self.models_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        models_dict = [asdict(model) for model in self.models.values()]
        open(file_path, 'w', encoding='utf-8')\
            .write(json.dumps(models_dict))

arena = Arena()
arena.run()
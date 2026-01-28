from judge import Judge
from agent import DEFAULT_MODEL, DEFAULT_BACKEND
from utils import InputTypes, Input, Joke, DEFAULT_JOKES_PATH, DEFAULT_INPUT_PATH, DEFAULT_OUTPUT_PATH, read_jokes, read_inputs
import numpy as np

# Typing
from dataclasses import dataclass, asdict
from typing import Optional
from enum import StrEnum

# Progress Bar
from tqdm import trange

# Store/Load Data
import json
from pathlib import Path

# Bradley-Terry scores e Matriz de Covariância 
import pandas as pd
from scipy.optimize import minimize

DEFAULT_MODELS_PATH = f'{DEFAULT_OUTPUT_PATH}/models.json'
ALL_INPUTS = -1
EVERY_TIME = 1
NO_WARMUP = 0

class OutputTypes(StrEnum):
    ARENA = 'arena'
    SCORE = 'scores'

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
    joke_ids: list[int]
    models: list[str]
    jokes: list[str]
    winner: Optional[str] = None
    prob_select: float = 0.0

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
        self.out_path = Path(out_path)
        self.models_path = Path(models_path)
        self.inputs = read_inputs(inputs_path)
        self.jokes = read_jokes(jokes_path)
        self.models = self._get_models()

    def _get_models(self) -> list[Model]:
        if self.models_path.exists():
            return {
                model['name']: Model(**model)
                for model in json.loads(
                    open(self.models_path, 'r', encoding='utf-8')\
                        .read()
                )
            }
        self.models_path.parent.mkdir(parents=True, exist_ok=True)
        first_joke_key = next(iter(self.jokes))
        return { 
            joke.model: Model(joke.model, 0.0, 0, 0)
            for joke in self.jokes[first_joke_key]
        }
    
    def _get_full_out_path(self, input_id: str, out_type: OutputTypes) -> Path:
        return Path(
            f'{self.out_path}/{out_type}/{input_id}.{'jsonl' if out_type == OutputTypes.ARENA else 'json'}'
        )

    def _get_match_results(self, input_id: str) -> list[Match]:
        out_path = self._get_full_out_path(input_id, OutputTypes.ARENA)
        if not out_path.exists(): return []
        return [
            json.loads(match)
            for match in open(out_path, 'r', encoding='utf-8')
        ]
    
    def _update_match_count(self, input: Input) -> None:
        results = self._get_match_results(input.id)
        for match_info in results:
            match = Match(**match_info)
            self.jokes[match.id][match.joke_ids[0]].num_matches[match.joke_ids[1]] += 1
            self.jokes[match.id][match.joke_ids[1]].num_matches[match.joke_ids[0]] += 1

    def _compute_bt_scores(self, input: Input) -> tuple[list[float], list[list[float]]]:
        df = pd.DataFrame(self._get_match_results(input.id))
        
        n_jokes = len(self.jokes[input.id])

        if df.empty:    
            return np.zeros(n_jokes), np.eye(n_jokes) * 10.0
        
        initial_guess = np.zeros(n_jokes)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x)})

        df[['joke_a', 'joke_b']] = pd.DataFrame(df['joke_ids'].tolist(), index=df.index)
        df[['model_a', 'model_b']] = pd.DataFrame(df['models'].tolist(), index=df.index)
        
        def negative_log_likelihood(params):
            score_a = params[df['joke_a'].values.astype(int)]
            score_b = params[df['joke_b'].values.astype(int)]
            diff = score_a - score_b
            signs = np.where(df['winner'] == df['model_b'], -1, 1)
            return np.sum(np.logaddexp(0, signs * diff))
        
        result = minimize(
            negative_log_likelihood, 
            initial_guess, 
            method='SLSQP',
            constraints=constraints,
            options={'disp': False}
        )

        scores = result.x
        try:
            res_bfgs = minimize(negative_log_likelihood, scores, method='BFGS')
            covariance = res_bfgs.hess_inv
        except:
            covariance = np.eye(n_jokes)

        return scores, covariance

    def _select_pair_active_sampling(self, input: Input, possible_jokes: list[Joke]) -> Match:
        candidates = []
        scores_utility = []

        for i, joke1 in enumerate(possible_jokes):
            for j in range(i + 1, len(possible_jokes)):
                var_diff = (
                    self.covariance_matrix[i, i] + 
                    self.covariance_matrix[j, j] - 
                    2 * self.covariance_matrix[i, j]
                )
                std_dev = np.sqrt(max(var_diff, 1e-6))
                count = joke1.num_matches[j]
                term_current = std_dev / (count + 1.0)
                term_future = std_dev / (count + 2.0)
                utility = term_current - term_future
                candidates.append((i, j))
                scores_utility.append(utility)

        scores_utility = np.array(scores_utility)
        probabilities = scores_utility / np.sum(scores_utility)        
        idx = np.random.choice(len(candidates), p=probabilities)
        joke_ids = candidates[idx]
        models = [possible_jokes[i].model for i in joke_ids]
        jokes  = [possible_jokes[i].joke  for i in joke_ids]
        return Match(
            input.id, input.input, input.input_type,
            joke_ids, models, jokes,
            prob_select= probabilities[idx]
        )
    
    def _random_match(self, input: Input, possible_jokes: list[Joke]) -> Match:
        joke_ids = np.random.choice(len(possible_jokes), 2, replace=False)
        selected = possible_jokes[joke_ids]
        models = [joke.model for joke in selected]
        jokes  = [joke.joke  for joke in selected]
        return Match(
            input.id, input.input, input.input_type,
            joke_ids, models, jokes,
            prob_select= 1.0 / (len(possible_jokes) * (len(possible_jokes) - 1) / 2)
        )

    def _gen_match(self, input: Input, cur_matches: int, warmup_matches: int) -> Match:
        possible_jokes = self.jokes[input.id]
        if cur_matches < warmup_matches:
            return self._random_match(input, possible_jokes)
        return self._select_pair_active_sampling(input, possible_jokes)
    
    def _update_models(self, models: list[str], winner: str) -> None:
        for i, model_name in enumerate(models):
            self.models[model_name].n_matches += 1
        self.models[winner].wins += 1

    def _run_match(self, match: Match) -> str:
        judge = self.judges[match.input_type]
        winner_id = judge.select(match.input, match.jokes)
        winner = match.models[winner_id]
        self.jokes[match.id][match.joke_ids[0]].num_matches[match.joke_ids[1]] += 1
        self.jokes[match.id][match.joke_ids[1]].num_matches[match.joke_ids[0]] += 1
        self._update_models(match.models, winner)
        return winner

    def run(self, num_matches: int = 50, num_inputs: int = ALL_INPUTS, random: bool = True, batch_size: int = EVERY_TIME, warmup_matches: int = NO_WARMUP) -> None:
        inputs = self.inputs
        if random: np.random.shuffle(inputs)
        if num_inputs == ALL_INPUTS or num_inputs > len(self.inputs): 
            num_inputs = len(self.inputs)
        outer_pbar = trange(num_inputs, desc='Input', unit='input')
        for input_idx in outer_pbar:
            input = inputs[input_idx]
            outer_pbar.set_postfix(id=input.id)
            self._update_match_count(input)
            _, self.covariance_matrix = self._compute_bt_scores(input)
            for cur_match in trange(num_matches, leave=False, desc='Match', unit='match'):
                match = self._gen_match(input, cur_match, warmup_matches)
                match.winner = self._run_match(match)
                self._save(match)
                if (cur_match + 1) % batch_size == 0:
                    _, self.covariance_matrix = self._compute_bt_scores(input)
            scores, _ = self._compute_bt_scores(input)
            self._save_scores(scores, input)
    
    def _save_scores(self, scores: list[float], input: Input):
        ranking = np.argsort(scores)[::-1]
        final_scores = [
            {
                'joke': self.jokes[input.id][idx].joke,
                'model': self.jokes[input.id][idx].model,
                'score': round(scores[idx], 2),
                'match_distribution': { 
                    self.jokes[input.id][id].model: matches
                    for id, matches in self.jokes[input.id][idx].num_matches.items()
                    if id != idx
                },
                'total_matches': sum(self.jokes[input.id][idx].num_matches.values())
            }
            for idx in ranking[:5]
        ]
        out_path = self._get_full_out_path(input.id, OutputTypes.SCORE)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        open(out_path, 'w', encoding='utf-8')\
            .write(json.dumps(final_scores))

    def _save(self, result: Match):
        # Save Match
        out_path = self._get_full_out_path(result.id, OutputTypes.ARENA)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        result_dict = asdict(result)
        open(out_path, 'a', encoding='utf-8')\
            .write(json.dumps(result_dict) + '\n')
        
        # Save Leaderboard State
        self.models_path.parent.mkdir(parents=True, exist_ok=True)
        models_dict = [asdict(model) for model in self.models.values()]
        open(self.models_path, 'w', encoding='utf-8')\
            .write(json.dumps(models_dict))

arena = Arena()
arena.run()
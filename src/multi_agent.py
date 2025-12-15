from tqdm import trange
from comedian import Comedian
from reviewer import Reviewer
from utils import InputTypes
from agent import DEFAULT_MODEL, DEFAULT_BACKEND

class MultiAgent():
    def __init__(
        self, 
        score_threshold: int = 8, 
        num_tries: int = 30,
        comedian_model: str = DEFAULT_MODEL,
        comedian_backend: str = DEFAULT_BACKEND,
        reviewer_model: str = DEFAULT_MODEL,
        reviewer_backend: str = DEFAULT_BACKEND
    ):
        # Create comedians for each input type with the specified model/backend
        self.comedian = {
            input_type: Comedian(input_type, model=comedian_model, backend=comedian_backend)
            for input_type in InputTypes
        }
        # Create reviewers for each input type with the specified model/backend
        self.reviewer = {
            input_type: Reviewer(input_type, model=reviewer_model, backend=reviewer_backend)
            for input_type in InputTypes
        }

        self.score_threshold = score_threshold
        self.num_tries = num_tries

    def gen_joke(self, input: str, input_type: InputTypes) -> str:
        best_score = -1
        best_joke = ''
        comedian = self.comedian[input_type]
        reviewer = self.reviewer[input_type]

        iter = trange(self.num_tries, desc="Tries", unit='Joke(s)', leave=False)
        for _ in iter:
            joke = comedian.gen_joke(input)
            score = reviewer.evaluate(input, joke)
            if score > best_score:
                best_joke = joke
                if score >= self.score_threshold: break
                best_score = score
    
        iter.close()
        comedian.reset()
        reviewer.reset()
        return best_joke

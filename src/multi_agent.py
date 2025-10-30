from tqdm import trange
from comedian import Comedian
from reviewer import Reviewer
from utils import InputTypes

class MultiAgent():
    def __init__(self, score_threshold: int = 8, num_tries: int = 30):
        self.comedian = {
            input_type: Comedian(input_type)
            for input_type in InputTypes
        }
        self.reviewer = Reviewer()

        self.score_threshold = score_threshold
        self.num_tries = num_tries

    def gen_joke(self, input: str, input_type: InputTypes) -> str:
        best_score = -1
        best_joke = ''
        comedian = self.comedian[input_type]

        iter = trange(self.num_tries, desc="Tries", unit='Joke(s)', leave=False)
        for _ in iter:
            joke = comedian.gen_joke(input)
            score = self.reviewer.evaluate(joke)
            if score > best_score:
                best_joke = joke
                if score >= self.score_threshold: break
                best_score = score
    
        iter.close()
        comedian.reset()
        self.reviewer.reset()
        return best_joke

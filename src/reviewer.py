from agent import Agent

class Reviewer(Agent):
    def __init__(self):
        instruction =  "You're the best joke evaluator in the world. \
                        Your job is to evaluate a joke and give it a rating from 0 to 10. \
                        You should be VERY critical and think well about your judgments; we only want the best joke. \
                        You may only answer with the score of the joke, without giving explanation or context to it."
        super().__init__(instruction)
    
    # TODO: Test if the joke follows user input
    def evaluate(self, input: str) -> int:
        while True:
            try: return int(self.chat(input))
            except: pass
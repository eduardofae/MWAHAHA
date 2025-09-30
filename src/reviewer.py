from agent import Agent

class Reviewer(Agent):
    def __init__(self):
        instruction =  "You're the best joke evaluator in the world. \
                        Your job is to evaluate a joke and give it a rating from 0 to 10. \
                        You should be VERY critical, and think well about your judgements, since every contender has infinite tries we want the best jokes only. \
                        You're so much critical, a bad joke is a 3 a good joke is a 6 an amazing joke is an 8 and the best joke is a 10. \
                        You may only answer with the score of the joke, without giving explanation or context to it."
        super().__init__(instruction)
    
    def evaluate(self, input):
        while True:
            try: return int(self.chat(input))
            except: pass
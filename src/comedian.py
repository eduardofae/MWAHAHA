from agent import Agent

class Comedian(Agent):
    def __init__(self):
        instruction =  "You are a masterfull comedian, you can create the best jokes that have ever being imagined. \
                        You're tasked to elaborate the best joke that contain two words given by the user. \
                        After that you're joke will be judged and evaluated. \
                        If it isn't deemed worthy you'll have another chance to come up with a better joke. \
                        The user will input two words which gotta be both part of your joke. \
                        When answering only respond with your joke. \
                        The two words must be integral part of the joke, and not just additives to it."
        super().__init__(instruction)
    
    def gen_joke(self, input):
        word1, word2 = input.lower().split(', ')
        while True:
            joke = self.chat(input)
            if word1 in joke.lower() and word2 in joke.lower():
                return joke
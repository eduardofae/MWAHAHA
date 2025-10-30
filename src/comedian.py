from agent import Agent
from utils import InputTypes

class Comedian(Agent):
    instruction_input_type = {
        InputTypes.WP: "The user will input two words, both of which have to be part of your joke.",
        InputTypes.HL: "The user will input a headline; your joke must be related to the given headline (it could be a punchline, or a joke inspired by it)."
    }

    def __init__(self, input_type: InputTypes):
        instruction = f"You are a masterful comedian; you can create the best jokes that have ever been imagined. \
                        You're tasked to make the best joke given a human input. \
                        After that your joke will be judged and evaluated. \
                        If it isn't deemed worthy, you'll have another chance to come up with a better joke. \
                        {self.instruction_input_type[input_type]} \
                        When answering, only respond with your joke. \
                        The human input must play an integral role in the joke."
        super().__init__(instruction)
    
    def gen_joke(self, input: str) -> str:
        return self.chat(input)
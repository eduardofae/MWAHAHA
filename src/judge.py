from agent import Agent, DEFAULT_MODEL, DEFAULT_BACKEND
from utils import InputTypes
import re
import numpy as np
from tqdm import tqdm

class Judge(Agent):
    MAX_RETRIES = 5  # Maximum attempts to get a valid score

    instruction_input_type = {
        InputTypes.WP: """WORD PAIR CRITERIA - The joke MUST:
- Include BOTH given words explicitly in the text (automatic 0 if missing)
- Use the words in a meaningful way, not just shoehorned in
- Create a clever connection between the two words""",
        InputTypes.HL: """HEADLINE CRITERIA - The joke MUST:
- Be clearly related to the headline's topic and context
- Work as a comedic extension of the headline (punchline, commentary, or inspired twist)
- Preserve the essence/theme of the original headline"""
    }
    
    def __init__(self, input_type: InputTypes, model: str = DEFAULT_MODEL, backend: str = DEFAULT_BACKEND):
        instruction = f"""You are an expert joke evaluator. Your job is to select the better joke from 2 candidates based on specific criteria.

{self.instruction_input_type[input_type]}

GENERAL QUALITY CRITERIA:
- Humor: Is it actually funny? Does it have a clear comedic payoff?
- Cleverness: Is the joke witty or just obvious?
- Conciseness: Is it tight and well-crafted, or rambling?

You will receive the ORIGINAL INPUT and two jokes (JOKE1 and JOKE2) to select which is the better one.
You MUST answer with ONLY a single number 1 or 2, indicating which joke was the best in the given context.
Do not include any explanation, context, or additional text - just the number."""
        super().__init__(instruction, model=model, backend=backend)
    
    def select(self, original_input: str, jokes: list[str]) -> int:
        prompt = f"ORIGINAL INPUT: {original_input}\n"
        for i, joke in enumerate(jokes):
            prompt += f'JOKE{i}: {joke}\n'
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.chat(prompt)
                # Try to extract a number from the response
                # First try direct conversion
                try:
                    best_joke = int(response.strip())
                    if best_joke and (best_joke == 1 or best_joke == 2):
                        return best_joke-1 # Transform to 0-1 to be used as index
                    
                except ValueError:
                    # Try to find a number in the response using regex
                    numbers = re.findall(r'\b(\d+)\b', response)
                    if numbers: 
                        best_joke = int(numbers[0])
                        if best_joke and (best_joke == 1 or best_joke == 2):
                            return best_joke-1 # Transform to 0-1 to be used as index
                
                # If we get here, the response was invalid
                tqdm.write(f"Warning: Invalid selection response (attempt {attempt + 1}/{self.MAX_RETRIES}): {response}")
                
            except KeyboardInterrupt:
                # Always allow user to interrupt
                raise
            except Exception as e:
                tqdm.write(f"Warning: Error selecting better joke (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
        
        # If all retries failed, return a default score
        tqdm.write(f"Error: Could not select the better joke after {self.MAX_RETRIES} attempts. Choosing at random.")
        return np.random.randint(0, 2)
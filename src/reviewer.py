from agent import Agent, DEFAULT_MODEL, DEFAULT_BACKEND
from utils import InputTypes
import re

class Reviewer(Agent):
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
        instruction = f"""You are an expert joke evaluator. Your job is to evaluate jokes based on specific criteria.

{self.instruction_input_type[input_type]}

GENERAL QUALITY CRITERIA:
- Humor: Is it actually funny? Does it have a clear comedic payoff?
- Cleverness: Is the joke witty or just obvious?
- Conciseness: Is it tight and well-crafted, or rambling?

SCORING GUIDE:
- 0-3: Fails the input criteria OR not funny at all
- 4-5: Meets criteria but weak humor
- 6-7: Good joke, meets criteria well
- 8-9: Excellent joke, creative use of input
- 10: Perfect, hilarious, masterful

You will receive the ORIGINAL INPUT and the JOKE to evaluate.
You MUST answer with ONLY a single number from 0 to 10, nothing else.
Do not include any explanation, context, or additional text - just the number."""
        super().__init__(instruction, model=model, backend=backend)
    
    def evaluate(self, original_input: str, joke: str) -> int:
        prompt = f"ORIGINAL INPUT: {original_input}\nJOKE: {joke}"
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.chat(prompt)
                # Try to extract a number from the response
                # First try direct conversion
                try:
                    score = int(response.strip())
                    if 0 <= score <= 10:
                        return score
                except ValueError:
                    # Try to find a number in the response using regex
                    numbers = re.findall(r'\b(\d+)\b', response)
                    if numbers:
                        score = int(numbers[0])
                        if 0 <= score <= 10:
                            return score
                
                # If we get here, the response was invalid
                print(f"Warning: Invalid score response (attempt {attempt + 1}/{self.MAX_RETRIES}): {response}")
                
            except KeyboardInterrupt:
                # Always allow user to interrupt
                raise
            except Exception as e:
                print(f"Warning: Error getting score (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
        
        # If all retries failed, return a default score
        print(f"Error: Could not get valid score after {self.MAX_RETRIES} attempts. Using default score of 5.")
        return 5
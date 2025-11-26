from agent import Agent, DEFAULT_MODEL, DEFAULT_BACKEND
import re

class Reviewer(Agent):
    MAX_RETRIES = 5  # Maximum attempts to get a valid score
    
    def __init__(self, model: str = DEFAULT_MODEL, backend: str = DEFAULT_BACKEND):
        instruction =  "You're the best joke evaluator in the world. \
                        Your job is to evaluate a joke and give it a rating from 0 to 10. \
                        You should be VERY critical and think well about your judgments; we only want the best joke. \
                        You MUST answer with ONLY a single number from 0 to 10, nothing else. \
                        Do not include any explanation, context, or additional text - just the number."
        super().__init__(instruction, model=model, backend=backend)
    
    # TODO: Test if the joke follows user input
    def evaluate(self, input: str) -> int:
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.chat(input)
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
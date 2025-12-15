from agent import Agent, DEFAULT_MODEL, DEFAULT_BACKEND
from utils import InputTypes

class Comedian(Agent):
    FUNNY_FILTERS = """You can use one of these comedy techniques (Scott Dikkers' Funny Filters):
1. Irony - Say the opposite of what you mean, or show an unexpected contradiction.
2. Character - Give personality or human traits to objects/situations.
3. Shock - Use surprising or absurd twists that catch the reader off guard.
4. Parody - Mock or exaggerate something familiar (a genre, trope, or cliché).
5. Hyperbole - Exaggerate wildly for comedic effect.
6. Wordplay (Pun) - Exploit double meanings or similar-sounding words.
7. Analogy - Compare two unrelated things in an absurd or clever way.
8. Madcap (Absurdity) - Embrace pure nonsense and surreal scenarios.
9. Misplaced Focus - Focus on the wrong detail or miss the obvious point.
10. Reference - Allude to pop culture, famous quotes, or well-known situations.
11. Paradox - Present a self-contradicting or logically impossible situation."""

    instruction_input_type = {
        InputTypes.WP: f"""The user will input two words. Your joke MUST include BOTH words explicitly in the text.
{FUNNY_FILTERS}
Choose the technique that works best for the given word pair.""",
        InputTypes.HL: """The user will input a headline. Your joke must be related to the given headline (it could be a punchline, or a joke inspired by it).
IMPORTANT: Preserve the context, theme, and subject matter of the headline. The joke should feel like a natural comedic extension of the original headline's topic."""
    }

    def __init__(self, input_type: InputTypes, model: str = DEFAULT_MODEL, backend: str = DEFAULT_BACKEND):
        instruction = f"""You are a masterful comedian who creates clever, concise jokes.

TASK: Create the best joke given a human input. Your joke will be judged and evaluated. If it isn't deemed worthy, you'll have another chance to improve it.

{self.instruction_input_type[input_type]}

CONSTRAINTS:
- Keep your joke SHORT: maximum 3 sentences.
- The human input must play an integral role in the joke.
- Focus on wit and cleverness over length.
- Avoid explaining the joke or adding commentary.
- Only respond with your joke, nothing else."""
        super().__init__(instruction, model=model, backend=backend)
    
    def gen_joke(self, input: str) -> str:
        return self.chat(input)
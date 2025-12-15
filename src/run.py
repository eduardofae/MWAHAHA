import argparse
from tqdm import tqdm
from multi_agent import MultiAgent
from utils import read_data, append_joke, get_last_processed_id

THRESHOLD = 8
TRIES = 30

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate jokes from corpus')
parser.add_argument('--continue', dest='continue_from_last', action='store_true',
                    help='Continue from the last processed joke in the output file')
args = parser.parse_args()

data = read_data()

# Default: Use Ollama with gemma3:4b
# agent = MultiAgent(THRESHOLD, TRIES)

# Example: Use Fuelix API with Claude Sonnet
agent = MultiAgent(
    THRESHOLD, TRIES,
    comedian_model='claude-sonnet-4-5',
    comedian_backend='fuelix',
    reviewer_model='claude-sonnet-4-5',
    reviewer_backend='fuelix'
)

# Example: Mix backends - Fuelix for comedian, Ollama for reviewer
# agent = MultiAgent(
#     THRESHOLD, TRIES,
#     comedian_model='gpt-5',
#     comedian_backend='fuelix',
#     reviewer_model='gpt-5',
#     reviewer_backend='fuelix'
# )

# Available Fuelix models: claude-sonnet-4-5, gpt-5, gemini-2.5-flash

# If continuing, find where to resume
start_index = 0
if args.continue_from_last:
    last_id = get_last_processed_id()
    if last_id:
        # Find the index after the last processed ID
        for i, (joke_id, _, _) in enumerate(data):
            if joke_id == last_id:
                start_index = i + 1
                break
        print(f"Continuing from joke {start_index + 1} (last processed: {last_id})")
    else:
        print("No previous jokes found, starting from the beginning")

# Process jokes starting from the determined index
pbar = tqdm(total=len(data) - start_index, desc='Jokes', unit='Joke(s)', initial=0)
try:
    for i in range(start_index, len(data)):
        joke_id, input, input_type = data[i]
        joke = agent.gen_joke(input, input_type)
        # Only write header if this is truly the first joke (not continuing)
        is_first = (i == 0 and start_index == 0)
        append_joke(joke_id, joke, is_first=is_first)
        pbar.update(1)
except KeyboardInterrupt:
    print("\n\nInterrupted by user. Progress has been saved.")
    print(f"To continue, run: python src/run.py --continue")
finally:
    pbar.close()
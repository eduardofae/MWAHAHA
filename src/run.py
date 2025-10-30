from tqdm import tqdm
from multi_agent import MultiAgent
from utils import read_data, write_data

THRESHOLD = 8
TRIES = 30

jokes = []
data = read_data()
agent = MultiAgent(THRESHOLD, TRIES)
for input, input_type in tqdm(data, desc='Jokes', unit='Joke(s)'):
    jokes.append(agent.gen_joke(input, input_type))

write_data(jokes)
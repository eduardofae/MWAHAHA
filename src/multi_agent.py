from tqdm import tqdm
from comedian import Comedian
from reviewer import Reviewer

words = ['Banana, Dinosaur', 'Mom, Dad', 'Dinner, Fate', 'Politics, Fear', 'Whale, Drums', 'French, Couch', 'Destiny, Desire', 'Bank, School', 'Pizza, Gasoline']
jokes = []

THRESHOLD = 8
TRIES = 30

comedian = Comedian()
reviewer = Reviewer()
for word_pair in tqdm(words, desc="Word Pairs"):
    best_score = 0
    best_joke = ''
    for _ in tqdm(range(TRIES), desc="Tries"):
        joke = comedian.gen_joke(word_pair)
        score = reviewer.evaluate(joke)
        if score > best_score:
            best_score = score
            best_joke = joke
        if score >= THRESHOLD: break
    jokes.append(best_joke)
    comedian.reset()
    reviewer.reset()

for joke in jokes:
    print(joke)
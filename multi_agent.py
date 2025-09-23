import ollama
from tqdm import tqdm

model_name = 'gemma3:4b'

joker_inst = [
    {"role": "system", "content": "You are a masterfull comedian, you can create the best jokes that have ever being imagined. You're tasked to elaborate the best joke that contain two words given by the user. After that you're joke will be judged and evaluated. If it isn't deemed worthy you'll have another chance to come up with a better joke. The user will input two words which gotta be both part of your joke. When answering only respond with your joke. The two words must be integral part of the joke, and not just additives to it.="},
]

reviewer_inst = [
    {"role": "system", "content": "You're the best joke evaluator in the world. Your job is to evaluate a joke and give it a rating from 0 to 10. You should be VERY critical, and think well about your judgements, since every contender has infinite tries we want the best jokes only. You're so much critical, a bad joke is a 3 a good joke is a 6 an amazing joke is an 8 and the best joke is a 10. You may only answer with the score of the joke, without giving explanation or context to it."},
]

words = ['Banana, Dinosaur', 'Mom, Dad', 'Dinner, Fate', 'Politics, Fear', 'Whale, Drums', 'Sponge Bob, Couch', 'Destiny, Desire', 'Bank, School', 'Pizza, Gasoline']
jokes = []

for word_pair in tqdm(words):
    accepted = False 
    joker_chat = joker_inst.copy()
    reviewer_chat = reviewer_inst.copy()
    for _ in tqdm(range(30)):
        best_score = 0
        best_joke = ''
        # Gen joke
        joker_chat.append({"role": "user", "content": word_pair})
        joker_response = ollama.chat(model=model_name, messages=joker_chat).message.content
        joker_chat.append({"role": "assistant", "content": joker_response})
        while True:
            # Evaluate joke
            reviewer_chat.append({"role": "user", "content": joker_response})
            reviewer_response = ollama.chat(model=model_name, messages=reviewer_chat).message.content
            reviewer_chat.append({"role": "assistant", "content": reviewer_response})
            try:
                score = int(reviewer_response)
            except:
                continue
            if score > best_score:
                if score >= 8:
                    accepted = True
                best_joke = score
                best_joke = joker_response
            break
        if accepted:
            break
    jokes.append(best_joke)
for joke in jokes:
    print(joke)
import ollama
DEFAULT_MODEL = 'gemma3:4b'

class Agent():
    INSTRUCTION = ''
    MODEL = ''
    cur_chat = []

    def __init__(self, instruction: str, model:str = DEFAULT_MODEL):
        self.INSTRUCTION = instruction
        self.MODEL = model
        self.reset()
    
    def chat(self, input: str) -> str:
        self.cur_chat.append({"role": "user", "content": input})
        response = ollama.chat(model=self.MODEL, messages=self.cur_chat).message.content
        self.cur_chat.append({"role": "assistant", "content": response})
        return response

    def reset(self) -> None:
        self.cur_chat = [
            {"role": "system", "content": self.INSTRUCTION},
        ]
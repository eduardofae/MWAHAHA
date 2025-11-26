import ollama
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DEFAULT_MODEL = 'gemma3:4b'
DEFAULT_BACKEND = 'ollama'
# DEFAULT_MODEL = 'deepseek-r1:8b'

# Fuelix API models for easy testing:
# - claude-sonnet-4-5
# - gpt-5
# - gemini-2.5-flash

class Agent():
    INSTRUCTION = ''
    MODEL = ''
    BACKEND = ''
    cur_chat = []

    def __init__(self, instruction: str, model: str = DEFAULT_MODEL, backend: str = DEFAULT_BACKEND):
        self.INSTRUCTION = instruction
        self.MODEL = model
        self.BACKEND = backend
        self.reset()
    
    def chat(self, input: str) -> str:
        self.cur_chat.append({"role": "user", "content": input})
        try:
            if self.BACKEND == 'ollama':
                response = self._chat_ollama()
            elif self.BACKEND == 'fuelix':
                response = self._chat_fuelix()
            else:
                raise ValueError(f"Unknown backend: {self.BACKEND}")
            
            self.cur_chat.append({"role": "assistant", "content": response})
            return response
        except KeyboardInterrupt:
            # Always allow user to interrupt
            self.cur_chat.pop()  # Remove the user message we just added
            raise
        except Exception as e:
            # Remove the user message we just added since the call failed
            self.cur_chat.pop()
            raise Exception(f"{self.BACKEND} API error: {e}") from e
    
    def _chat_ollama(self) -> str:
        """Call the Ollama API."""
        response = ollama.chat(
            model=self.MODEL, 
            messages=self.cur_chat
        ).message.content
        return response
    
    def _chat_fuelix(self) -> str:
        """Call the Fuelix API."""
        api_token = os.getenv('FUELIX_API_TOKEN')
        api_url = os.getenv('FUELIX_API_URL', 'https://api.fuelix.ai/v1/chat/completions')
        
        if not api_token:
            raise ValueError("FUELIX_API_TOKEN not set in environment variables")
        
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'messages': self.cur_chat,
            'model': self.MODEL
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        # Extract the content from the response
        # Assuming OpenAI-compatible format: data['choices'][0]['message']['content']
        return data['choices'][0]['message']['content']

    def reset(self) -> None:
        self.cur_chat = [
            {"role": "system", "content": self.INSTRUCTION},
        ]
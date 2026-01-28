import ollama
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

DEFAULT_MODEL = 'gemma3:4b'
DEFAULT_BACKEND = 'ollama'
# DEFAULT_MODEL = 'deepseek-r1:8b'

# Fuelix API models for easy testing:
# - claude-sonnet-4-5
# - gpt-5
# - gemini-2.5-

# AI/ML API models for easy testing:
# - gpt-3.5-turbo-instruct
# - gpt-4o
# - deepseek/deepseek-r1
# - deepseek/deepseek-chat

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
            elif self.BACKEND == 'aimlapi':
                response = self._chat_aimlapi()
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

    def _chat_aimlapi(self):
        api_token = os.getenv('AIMLAPI_API_TOKEN')
        api_url = os.getenv('AIMLAPI_API_URL', 'https://api.aimlapi.com/v1')
        
        if not api_token:
            raise ValueError("AIMLAPI_API_TOKEN not set in environment variables")

        api = OpenAI(api_key=api_token, base_url=api_url)
        
        params = {
            'model': self.MODEL,
            'temperature': 0.2,
            'max_tokens': 300,
            'top_p': 1,
            'frequency_penalty': 0,
            'presence_penalty': 0,
        }

        response = api.chat.completions.create(
            model=params['model'],
            messages=self.cur_chat,
            temperature = params['temperature'],
            max_tokens = params['max_tokens'],
            top_p = params['top_p'],
            frequency_penalty = params['frequency_penalty'],
            presence_penalty = params['presence_penalty'],
        )

        return response.choices[0].message.content

    def reset(self) -> None:
        self.cur_chat = [
            {"role": "system", "content": self.INSTRUCTION},
        ]
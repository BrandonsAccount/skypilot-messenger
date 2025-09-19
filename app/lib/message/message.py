#!/usr/bin/env python3
from typing import Any, Dict
import json
from datetime import datetime

def safe_load_json(path):
    '''Load JSON content from a file, returning an empty dict if the file is empty.'''
    with open(path) as f:
        content = f.read().strip()
        if not content:
            return {}
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in '{path}': {e}")

class Message():
    def __init__(self
                 , user_id: str = ""
                 , session_id: str = ""
                 , prompt: str = ""
                 , llm_provider: str = "openai"
                 , llm: str = "gpt-5-nano"
                 , user_profile: str = None
                 ):
        self.user_id = user_id
        self.session_id = session_id
        self.prompt = prompt
        self.llm_provider = llm_provider
        self.llm = llm
        self.user_profile = user_profile

        # WHAT: The conversation attribute is a list that holds the sequence of messages exchanged in the session.
        self.conversation = []

        # WHAT: The following attributes are populated from JSON files. They provide the necessary context and structure for the conversation.
        # WHY: This design allows for easy updates and modifications to the conversation structure without changing the code.
        self.instructions = safe_load_json("lib/message/instructions.json")
        self.options = safe_load_json("lib/message/options.json")
        self.capabilities = {}
        self.resources = safe_load_json("lib/message/resources.json")
        self.output_schema = safe_load_json("lib/message/output-schema.json")

    def set_prompt(self, prompt: str):
        self.prompt = prompt
        self.conversation.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })

    def set_feedback(self, feedback: str):
        self.conversation.append({
            "role": "assistant",
            "content": feedback,
            "timestamp": datetime.now().isoformat()
        })

    def set_llm_response(self, response: Dict[str, Any]):
        self.conversation.append({
            "role": "system",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

    def get_contents(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "prompt": self.prompt,
            "user_profile": self.user_profile,
            "llm_provider": self.llm_provider,
            "llm": self.llm,
            "conversation": self.conversation,
            "instructions": self.instructions,
            "options": self.options,
            "capabilities": self.capabilities,
            "resources": self.resources,
            "output_schema": self.output_schema
        }
# -*- coding: utf-8 -*-

from typing import Generator

from openai import OpenAI

from .base import BaseProvider


class OpenAIProvider(BaseProvider):
    def initialize_client(self) -> None:
        self.client = OpenAI(api_key=self.config.get("openai", {}).get("api_key"))
        self.model = self.config["current"]["model"]
        self.max_tokens = self.config.get("openai", {}).get("max_tokens", 2000)
        self.temperature = self.config.get("openai", {}).get("temperature", 0.7)

    def stream_chat(
        self, system_prompt: str, user_content: str
    ) -> Generator[str, None, None]:
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_content,
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

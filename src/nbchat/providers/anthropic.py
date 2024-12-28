from typing import Generator

from anthropic import Anthropic

from .base import BaseProvider


class AnthropicProvider(BaseProvider):
    def initialize_client(self) -> None:
        self.client = Anthropic(api_key=self.config.get("anthropic", {}).get("api_key"))
        self.model = self.config["current"]["model"]
        self.max_tokens = self.config.get("anthropic", {}).get("max_tokens", 4000)

    def stream_chat(
        self, system_prompt: str, user_content: str
    ) -> Generator[str, None, None]:
        messages = [
            {
                "role": "user",
                "content": user_content,
            }
        ]

        response = self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=messages,
            max_tokens=self.max_tokens,
            stream=True,
        )

        for chunk in response:
            if hasattr(chunk, "type"):
                if chunk.type == "content_block_delta":
                    yield chunk.delta.text
                elif chunk.type == "message_delta":
                    continue
                elif chunk.type == "error":
                    print(f"Error: {chunk}")
                    break

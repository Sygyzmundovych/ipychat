# -*- coding: utf-8 -*-

from typing import Generator

from anthropic import Anthropic

from .base import BaseProvider


class AnthropicProvider(BaseProvider):
    def initialize_client(self) -> None:
        api_key = self.config.get("anthropic", {}).get("api_key")
        if api_key is None or api_key == "":
            self.console.print(
                "[red]Set [bold]ANTHROPIC_API_KEY[/bold] in your environment, or run [bold]ipychat config[/bold].[/red]"
            )
            self.client = None
            return

        self.client = Anthropic(api_key=api_key)
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

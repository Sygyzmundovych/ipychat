# -*- coding: utf-8 -*-

from typing import Generator

import google.generativeai as genai

from .base import BaseProvider


class GoogleProvider(BaseProvider):
    def initialize_client(self) -> None:
        api_key = self.config.get("google", {}).get("api_key")
        if api_key is None or api_key == "":
            self.console.print(
                "[red]Set [bold]GOOGLE_API_KEY[/bold] in your environment, or run [bold]ipychat config[/bold].[/red]"
            )
            self.client = None
            return

        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.config["current"]["model"])
        self.temperature = self.config.get("google", {}).get("temperature", 0.7)

    def stream_chat(
        self, system_prompt: str, user_content: str
    ) -> Generator[str, None, None]:
        messages = [
            {
                "role": "user",
                "parts": [f"{system_prompt}\n\n{user_content}"],
            }
        ]

        response = self.client.generate_content(
            messages,
            stream=True,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature
            ),
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text
                yield chunk.text

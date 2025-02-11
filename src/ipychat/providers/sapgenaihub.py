# -*- coding: utf-8 -*-

from typing import Generator
from .base import BaseProvider

from gen_ai_hub.orchestration.models.message import SystemMessage, UserMessage
from gen_ai_hub.orchestration.models.llm import LLM
from gen_ai_hub.orchestration.models.template import Template, TemplateValue
from gen_ai_hub.orchestration.models.config import OrchestrationConfig
from gen_ai_hub.orchestration.service import OrchestrationService

class SAPGenAIHubProvider(BaseProvider):
    def initialize_client(self) -> None:
        api_key = self.config.get("sapgenaihub", {}).get("api_key")
        if not api_key:
            self.console.print(
                "[red]Set [bold]SAP GenAI Hub orchestration API[/bold] in your environment, or run [bold]ipychat config[/bold].[/red]"
            )
            self.client = None
            return

        llm = LLM(
            name=self.config["current"]["model"],
            version="latest",
            parameters={"max_tokens": 256, "temperature": 0.2}
        )

        template = Template(
            messages=[
                SystemMessage("{{?system_prompt}}"),
                UserMessage("{{?query}}")
            ],
            defaults=[
                TemplateValue(name="system_prompt", value="You are a helpful principal engineer and principal data scientist with access to the current IPython environment."),
                TemplateValue(name="query", value="What can I do in IPython?")
            ]
        )

        config = OrchestrationConfig(
            template=template,
            llm=llm
        )

        self.client = OrchestrationService(api_url=api_key, config=config)

    def stream_chat(
        self, system_prompt: str, user_content: str
    ) -> Generator[str, None, None]:
        if not self.client:
            raise ValueError("Client is not initialized.")

        response = self.client.stream(
            config=self.client.config,
            template_values=[
                TemplateValue(name="system_prompt", value=system_prompt),
                TemplateValue(name="query", value=user_content)
            ],
            stream_options={
                'chunk_size': 1
            }
        )

        for chunk in response:
            yield chunk.orchestration_result.choices[0].delta.content
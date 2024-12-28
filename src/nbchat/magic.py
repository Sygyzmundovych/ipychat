# -*- coding: utf-8 -*-

from IPython.core.magic import Magics, line_magic, magics_class
from rich.console import Console

from .config import load_config, save_config
from .context import get_context_for_variables
from .models import AVAILABLE_MODELS, get_model_by_name
from .providers import get_provider
from .ui import display_model_table, select_with_arrows

console = Console()


@magics_class
class NBChatMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        self._config = load_config()
        self.debug = True
        self.provider = get_provider(self._config, self.debug)

    @line_magic
    def chat(self, line):
        """Line magic for quick questions."""
        return self._handle_query(line)

    @line_magic
    def chat_config(self, line):
        """Configure chat parameters."""

        current = self._config.get("current", {})
        print("Current configuration:")
        print(f"Provider: {current.get('provider')}")
        print(f"Model: {current.get('model')}")

        if current.get("provider") == "openai":
            openai_config = self._config.get("openai", {})
            print(f"Temperature: {openai_config.get('temperature')}")
            print(f"Max tokens: {openai_config.get('max_tokens')}")

        display_model_table()
        model_names = [m.name for m in AVAILABLE_MODELS]
        model_name = select_with_arrows(
            "Which model would you like to use?",
            model_names,
        )

        try:
            model = get_model_by_name(model_name)
            if "current" not in self._config:
                self._config["current"] = {}

            self._config["current"]["model"] = model.name
            self._config["current"]["provider"] = model.provider

            save_config(self._config)
            self.provider = get_provider(self._config, self.debug)
            print(f"Model changed to {model.name}")
        except ValueError as e:
            print(f"Error: {e}")
            return

    def _handle_query(self, query: str):
        """Handle chat queries."""
        context = get_context_for_variables(self.shell.user_ns, query)

        history = []
        for session_id in range(1, len(self.shell.history_manager.input_hist_raw)):
            cmd = self.shell.history_manager.input_hist_raw[session_id]
            if cmd.strip() and not cmd.startswith("%"):
                history.append(f"In [{session_id}]: {cmd}")

        system_prompt = "You are a helpful principal engineer and principal data scientist with access to the current IPython environment."
        user_content = f"Recent IPython history:\n{''.join(history[-5:])}\n\nContext:\n{context}\n\nQuestion: {query}"

        self.provider.stream_with_display(system_prompt, user_content)
        return None


def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    ipython.register_magics(NBChatMagics)

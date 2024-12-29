# -*- coding: utf-8 -*-

from IPython.core.magic import Magics, line_magic, magics_class
from rich.console import Console
from traitlets import Bool
from traitlets.config.configurable import Configurable

from .config import load_config, save_config
from .context import get_context_for_variables
from .models import AVAILABLE_MODELS, get_model_by_name
from .providers import get_provider
from .ui import display_model_table, select_with_arrows

console = Console()


@magics_class
class IPyChatMagics(Magics, Configurable):
    debug = Bool(False, help="Start ipychat in debug mode").tag(config=True)

    def __init__(self, shell):
        Magics.__init__(self, shell)
        Configurable.__init__(self, config=shell.config)
        self._config = load_config()
        self.provider = get_provider(self._config, self.debug)

    @line_magic
    def ask(self, line):
        """Line magic for quick questions."""
        return self._handle_query(line)

    @line_magic
    def models(self, line):
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

        self.provider.stream_response(system_prompt, user_content)
        return None


def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    # Check if any of our magics already exist
    magic_names = ["ask", "models"]
    existing_magics = [
        name for name in magic_names if name in ipython.magics_manager.magics["line"]
    ]

    if existing_magics:
        console.print(
            f"[yellow]Warning: The following magic commands already exist: {', '.join(existing_magics)}"
        )
        console.print("They will be overridden by ipychat.[/yellow]")

    ipython.register_magics(IPyChatMagics)

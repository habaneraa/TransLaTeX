import sys
import warnings
warnings.filterwarnings('ignore')

from textual.app import App
from textual.binding import Binding

from trans_latex.ui.preparation import ConfigScreen
from trans_latex.ui.welcome import WelcomeScreen
from trans_latex.ui.progress import ProgressScreen


class TransLaTeXTUI(App):
    TITLE = "TransLaTeX"
    SUB_TITLE = "A tool for translating LaTeX projects with your favorite LLM."
    CSS_PATH = [
        "ui/screen.tcss",
        "ui/pages.tcss",
        "ui/progress.tcss"
    ]
    BINDINGS = [
        Binding("ctrl+d", "toggle_dark", "Toggle dark mode"),
        Binding("ctrl+c", "quit", "Quit", show=True, priority=True),
        Binding("ctrl+backslash", "command_palette", show=True, priority=True),
    ]

    def on_mount(self) -> None:
        self.push_screen(WelcomeScreen())
    
    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
    
    def action_dismiss_welcome(self) -> None:
        self.pop_screen()
        self.start()
    
    def on_welcome_screen_start(self, event):
        self.action_dismiss_welcome()
    
    def start(self) -> None:
        def launch_translation(result: bool) -> None:
            self.push_screen(ProgressScreen())
        self.push_screen(ConfigScreen(), launch_translation)
    


from textual.screen import Screen
from textual.widgets import Markdown, Button
from textual.message import Message

from trans_latex.ui.localization.string_res import resources


class WelcomeScreen(Screen):

    class Start(Message):
        pass

    def compose(self):
        yield Markdown(resources.get(r'welcome_md'))
        yield Button(resources.get(r'start'), variant='success', id='welcome-start')
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.post_message(self.Start())
        event.stop()

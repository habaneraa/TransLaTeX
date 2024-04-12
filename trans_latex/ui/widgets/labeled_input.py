from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Input, Label


class InputWithLabel(Widget):

    DEFAULT_CSS = """
    InputWithLabel {
        layout: horizontal;
        height: auto;
        margin: 1 4 0 4
    }
    InputWithLabel Label {
        padding: 1;
        width: 20;
        text-align: right;
    }
    InputWithLabel Input {
        width: 1fr;
    }
    """

    def __init__(self, input_label: str, **input_kwargs) -> None:
        self.input_label = input_label
        self.input_kwargs = input_kwargs
        super().__init__()

    def compose(self) -> ComposeResult:  
        yield Label(self.input_label)
        yield Input(**self.input_kwargs)

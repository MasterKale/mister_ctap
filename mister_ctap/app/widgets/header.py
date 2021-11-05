from rich.console import RenderableType
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from textual import events
from textual.reactive import Reactive
from textual.widgets import Header


class MisterCtapHeader(Header):
    """Override the default Header for Styling

    Borrowed from https://github.com/sirfuzzalot/textual-inputs/blob/main/examples/simple_form.py
    """

    def __init__(self) -> None:
        super().__init__()
        self.tall = True

    def render(self) -> Table:
        header_table = Table.grid(padding=(0, 1), expand=True)
        header_table.add_column(justify="left", ratio=0, width=8)
        header_table.add_column("title", justify="center", ratio=1)
        header_table.add_column("clock", justify="right", width=8)
        header_table.add_row(
            "🔐", self.full_title, self.get_clock() if self.clock else ""
        )
        header: RenderableType
        header = (
            Panel(header_table, style=header_table.style) if self.tall else header_table
        )
        return header

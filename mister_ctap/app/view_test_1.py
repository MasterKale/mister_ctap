from rich.console import Group
from rich.panel import Panel

from textual.app import App
from textual import events
from textual.widgets import (
    Footer,
    ScrollView,
    Button,
)


class ViewTest1(App):
    async def on_load(self, event: events.Load) -> None:
        """
        Bind hotkeys
        """
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event: events.Mount) -> None:
        """
        Two-column layout with list on left and tabs on right
        """
        # Dock Footer first (will be hidden otherwise)
        await self.view.dock(Footer(), edge="bottom")

        # Create a scrollview and dock it
        self.container = ScrollView()
        await self.view.dock(self.container, edge="top")

        # Prepare some tall panels
        panel1 = Panel("Hello", style="black on red", height=8)
        panel2 = Panel("World", style="black on blue", height=4)
        panel3 = Panel("!", style="black on green", height=8)

        # Group everything together
        group = Group(panel1, panel2, panel3)

        # Set contents of the scrollview
        await self.container.update(group)


ViewTest1.run(title="View Test 1", log="textual_view_test_1.log")

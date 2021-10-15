import uuid
import json

from rich.json import JSON
from textual.app import App
from textual import events, log
from textual.widgets import (
    Header,
    Footer,
    ScrollView,
    Button,
    TreeControl,
    TreeClick,
)

from mister_ctap.core.authenticators import (
    get_authenticators,
    parse_authenticator_options,
    only_supported_authenticator_options,
    wink,
)
from mister_ctap.app.view_models import (
    AuthenticatorListData,
    AuthenticatorViewModel,
)


class MisterCtapApp(App):
    body: ScrollView

    async def on_load(self, event: events.Load) -> None:
        """
        Bind hotkeys
        """
        await self.bind("q", "quit", "Quit")
        await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")

    async def on_mount(self, event: events.Mount) -> None:
        """
        Two-column layout with list on left and tabs on right
        """

        self.body = ScrollView(gutter=1, contents="Credentials Go Here")
        tree = TreeControl(
            "Authenticators",
            {},
            padding=(1, 2),
        )

        # Display the data
        await tree.root.expand()

        # Add Header / Footer / Sidebar
        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(ScrollView(tree), edge="left", size=45, name="sidebar")

        # Add Body to remaining space
        await self.view.dock(self.body, edge="right")

        async def display_authenticators() -> None:
            # await sidebar.update("Authenticators go here")
            # Add data to tree view
            for authr in get_authenticators():
                model = AuthenticatorViewModel(
                    raw=authr,
                    aaguid=str(uuid.UUID(bytes=authr.info.aaguid)),
                    options=parse_authenticator_options(authr),
                )

                tree_data = AuthenticatorListData(authenticator=model)
                await tree.add(tree.root.id, model.aaguid, tree_data.dict())

        await self.call_later(display_authenticators)

    async def handle_tree_click(self, message: TreeClick[dict]) -> None:
        node_data = AuthenticatorListData.parse_obj(message.node.data)
        model = node_data.authenticator

        # Filter out unsupported options
        supported_options = only_supported_authenticator_options(model.options)
        options = JSON.from_data(supported_options).text

        # Try and visually notify the user which authenticator they're looking at
        wink(model.raw)

        await self.body.update(f"Supported options for {model.aaguid}:\n{options}")


MisterCtapApp.run(title="Mister CTAP", log="textual.log")

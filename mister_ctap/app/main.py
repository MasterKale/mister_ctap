import uuid
import json
from typing import List

from rich.json import JSON
from rich.markdown import Markdown
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
from mister_ctap.app.widgets import AuthenticatorsList, MisterCtapHeader


class MisterCtapApp(App):
    body: ScrollView
    authenticators_list_container: ScrollView
    auth_view_models: List[AuthenticatorViewModel] = []

    def _get_authenticators(self) -> List[AuthenticatorViewModel]:
        return [
            AuthenticatorViewModel(
                raw=authr,
                aaguid=str(uuid.UUID(bytes=authr.info.aaguid)),
                options=parse_authenticator_options(authr),
            )
            for authr in get_authenticators()
        ]

    async def on_load(self, event: events.Load) -> None:
        """
        Bind hotkeys
        """
        await self.bind("q", "quit", "Quit")
        await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("r", "reload_authenticators", "Reload")

    async def on_mount(self, event: events.Mount) -> None:
        """
        Two-column layout with list on left and tabs on right
        """
        # authenticators = self._get_authenticators()
        # authenticators_list = AuthenticatorsList(
        #     authenticators, self.handle_select_authenticator
        # )
        self.authenticators_list_container = ScrollView()

        # Add Header / Footer / Sidebar
        await self.view.dock(MisterCtapHeader(), edge="top")
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(
            self.authenticators_list_container, edge="left", size=45, name="sidebar"
        )

        # Add Body to remaining space
        self.body = ScrollView(gutter=1)
        await self.view.dock(self.body, edge="right")

        # Display authenticators
        await self.action_reload_authenticators()

    async def handle_select_authenticator(
        self, authenticator: AuthenticatorViewModel
    ) -> None:
        # Filter out unsupported options
        supported_options = only_supported_authenticator_options(authenticator.options)
        # options = str(JSON.from_data(supported_options).text)
        supported_options_simple = list(supported_options.keys())
        supported_options_simple.sort()
        options = ", ".join(supported_options_simple)

        # Try and visually notify the user which authenticator they're looking at
        wink(authenticator.raw)

        body_content: List[str] = [
            f"# AAGUID: {authenticator.aaguid}",
            "**Supported options:**",
            f"> {options}",
        ]

        await self.body.update(Markdown("\n".join(body_content)))

    async def action_reload_authenticators(self):
        authenticators = self._get_authenticators()
        authenticators_list = AuthenticatorsList(
            authenticators, self.handle_select_authenticator
        )
        await self.authenticators_list_container.update(authenticators_list)
        self.authenticators_list_container.refresh(layout=True)
        await self.body.update("<-- Select an authenticator to continue")


MisterCtapApp.run(title="Mister CTAP", log="textual.log")

from typing import Callable, List, Awaitable
from rich.tree import Tree

from textual.widget import Widget
from textual.widgets import TreeControl, TreeClick
from textual.widgets._tree_control import TreeNode, NodeID, NodeDataType
from rich.json import JSON

from mister_ctap.app.view_models import AuthenticatorViewModel, AuthenticatorListData


class AuthenticatorsList(TreeControl):
    # Props
    authenticators: List[AuthenticatorViewModel] = []
    on_select_authenticator: Callable[[AuthenticatorViewModel], Awaitable[None]]
    label = "Authenticators"

    def __init__(
        self,
        authenticators: List[AuthenticatorViewModel],
        on_select_authenticator: Callable[[AuthenticatorViewModel], None],
    ):
        super().__init__(self.label, {}, padding=(1, 2))
        self.authenticators = authenticators
        self.on_select_authenticator = on_select_authenticator

    async def on_mount(self) -> None:
        # Display the data
        await self.root.expand()
        await self.display_authenticators()

    async def handle_tree_click(self, message: TreeClick[dict]) -> None:
        # Don't crash if a tree node doesn't have authenticator data
        if not message.node.data:
            return
        node_data = AuthenticatorListData.parse_obj(message.node.data)
        auth_view_model = node_data.authenticator

        await self.on_select_authenticator(auth_view_model)

    async def display_authenticators(self):
        for auth_view_model in self.authenticators:
            tree_data = AuthenticatorListData(authenticator=auth_view_model)
            await self.add(self.root.id, auth_view_model.aaguid, tree_data.dict())

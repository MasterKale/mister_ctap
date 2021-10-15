from pydantic import BaseModel
from fido2.ctap2 import Ctap2

from mister_ctap.core.structs import AuthenticatorOptions


class AuthenticatorViewModel(BaseModel):
    raw: Ctap2
    aaguid: str
    options: AuthenticatorOptions

    class Config:
        arbitrary_types_allowed = True


class AuthenticatorListData(BaseModel):
    authenticator: AuthenticatorViewModel

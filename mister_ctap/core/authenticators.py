from typing import List

from fido2.ctap2.base import Ctap2
from fido2.hid import CtapHidDevice

from mister_ctap.core.structs import AuthenticatorOptions


def get_authenticators() -> List[Ctap2]:
    return [Ctap2(dev) for dev in CtapHidDevice.list_devices()]


def parse_authenticator_options(authenticator: Ctap2) -> AuthenticatorOptions:
    return AuthenticatorOptions.parse_obj(authenticator.info.options)


def only_supported_authenticator_options(options: AuthenticatorOptions) -> dict:
    return {key: val for key, val in options.dict().items() if val is True}

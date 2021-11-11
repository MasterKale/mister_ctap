from typing import List
from fido2.ctap2.base import Ctap2, CredentialManagement

from mister_ctap.core.structs import EnumerateRpsResponse, EnumerateCredentialsResponse


def authorize_credential_management(authenticator: Ctap2) -> CredentialManagement:
    pass


def get_rps(cred_man: CredentialManagement) -> List[EnumerateRpsResponse]:
    pass


def get_rp_discoverable_credentials(
    cred_man: CredentialManagement,
    rp: EnumerateRpsResponse,
) -> List[EnumerateCredentialsResponse]:
    pass

from typing import Literal, Optional
from pydantic import BaseModel


class PublicKeyCredentialUserEntity(BaseModel):
    id: bytes
    name: Optional[str]
    displayName: Optional[str]


class PublicKeyCredentialDescriptor(BaseModel):
    id: bytes
    type: Literal["public-key"] = "public-key"


class AuthenticatorOptions(BaseModel):
    """
    https://fidoalliance.org/specs/fido-v2.1-rd-20201208/fido-client-to-authenticator-protocol-v2.1-rd-20201208.html#option-id
    """

    plat: bool = False
    rk: bool = False
    clientPin: Optional[bool] = None
    up: bool = True
    uv: Optional[bool] = None
    pinUvAuthToken: Optional[bool] = None
    noMcGaPermissionsWithClientPin: Optional[bool] = False
    largeBlobs: Optional[bool] = None
    ep: Optional[bool] = None
    bioEnroll: Optional[bool] = None
    userVerificationMgmtPreview: Optional[bool] = None
    uvBioEnroll: Optional[bool] = None
    authnrCfg: Optional[bool] = None
    uvAcfg: Optional[bool] = None
    credMgmt: Optional[bool] = None
    credentialMgmtPreview: Optional[bool] = None
    setMinPINLength: Optional[bool] = None
    makeCredUvNotRqd: Optional[bool] = False
    alwaysUv: Optional[bool] = None


class PublicKeyCredentialRpEntity(BaseModel):
    id: str
    name: Optional[str] = None


class EnumerateRpsResponse(BaseModel):
    """
    https://fidoalliance.org/specs/fido-v2.1-rd-20201208/fido-client-to-authenticator-protocol-v2.1-rd-20201208.html#enumeratingRPs
    """

    rp: PublicKeyCredentialRpEntity
    rp_id_hash: bytes
    total_rps: int


class EnumerateCredentialsResponse(BaseModel):
    """
    https://fidoalliance.org/specs/fido-v2.1-rd-20201208/fido-client-to-authenticator-protocol-v2.1-rd-20201208.html#enumeratingCredentials
    """

    user: PublicKeyCredentialUserEntity
    credential: PublicKeyCredentialDescriptor
    # public_key: PublicKeyCOSE
    cred_protect: Optional[int] = None
    large_blob_key: Optional[int] = None

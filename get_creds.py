import uuid
from rich import print
from base64 import urlsafe_b64encode
from hashlib import sha256
from typing import List

from fido2.hid import CtapHidDevice
from fido2.client import Fido2Client, WindowsClient
from fido2.server import Fido2Server
from getpass import getpass
from fido2.ctap2 import CredentialManagement, Ctap2, ClientPin
from getpass import getpass

from mister_ctap.core.structs import (
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialUserEntity,
    AuthenticatorOptions,
    EnumerateRpsResponse,
    EnumerateCredentialsResponse,
)

try:
    from fido2.pcsc import CtapPcscDevice
except ImportError:
    CtapPcscDevice = None

ctap: Ctap2 = None
for dev in CtapHidDevice.list_devices():
    if ctap:
        break

    ctap = Ctap2(dev)

if not ctap:
    raise Exception("No authenticator available")

print("[CTAP OPTIONS]")
parsed_opts = AuthenticatorOptions.parse_obj(ctap.info.options)
# Show only supported options
print({key: val for key, val in parsed_opts.dict().items() if val is True})
# Pretty-print UUID
print(uuid.UUID(bytes=ctap.info.aaguid))

if not parsed_opts.clientPin:
    raise Exception("PIN not set for the device!")

if not parsed_opts.credMgmt and not parsed_opts.credentialMgmtPreview:
    raise Exception("Authenticator does not support credential management")

client_pin = ClientPin(ctap)

# Get token with cm permissions
if parsed_opts.pinUvAuthToken:
    print("Touch your authenticator device now...")
    pin_token = client_pin.get_uv_token(ClientPin.PERMISSION.CREDENTIAL_MGMT)
else:
    pin = getpass("Please enter PIN:")
    pin_token = client_pin.get_pin_token(pin, ClientPin.PERMISSION.CREDENTIAL_MGMT)

cred_man = CredentialManagement(ctap, client_pin.protocol, pin_token)

enumerated_rps = cred_man.enumerate_rps()
num_rps = len(enumerated_rps)
print(f"Enumerating {num_rps} Registered RP's")

for enumerated in enumerated_rps:
    parsed_rp = EnumerateRpsResponse.parse_obj(
        {
            "rp": enumerated[3],
            "rp_id_hash": enumerated[4],
            "total_rps": enumerated[5],
        }
    )

    # print(parsed_rp)
    print(f"\n[RP Info]")
    print(f'     RP ID: "{parsed_rp.rp.id}"')
    print(f'RP ID Hash: "{parsed_rp.rp_id_hash.hex()}"')

    rp_id_hash = parsed_rp.rp_id_hash
    rp_creds = cred_man.enumerate_creds(rp_id_hash)

    parsed_creds: List[EnumerateCredentialsResponse] = []
    for idx, cred in enumerate(rp_creds):
        # Map numeric keys to actual properties
        raw_cred = {
            "user": cred[6],
            "credential": cred[7],
        }

        # Gracefully handle potentially missing properties
        try:
            raw_cred["cred_protect"] = cred[9]
        except:
            pass

        try:
            raw_cred["large_blob_key"] = cred[10]
        except:
            pass

        parsed_cred = EnumerateCredentialsResponse.parse_obj(raw_cred)
        parsed_creds.append(parsed_cred)

    for idx, parsed_cred in enumerate(parsed_creds):
        # print(parsed_cred)
        # cred_pubkey = cred[8]
        # print(cred_pubkey)

        cred_id_base64 = urlsafe_b64encode(parsed_cred.credential.id).decode("utf-8")
        cred_num = idx + 1
        user_id_str = parsed_cred.user.id.decode("utf-8")

        print(f"\n    [Discoverable Credential #{cred_num}]")
        print(f'    Credential ID: "{cred_id_base64}"')
        print(f'          User ID: "{user_id_str}"')
        print(f'        User Name: "{parsed_cred.user.name}"')

    print(f"\nDeleting Credential #1...")
    # cred_man.delete_cred(rp_creds[0][7])
    cred_id_base64 = urlsafe_b64encode(parsed_creds[0].credential.id).decode("utf-8")
    print(f"Deleted Credential ID {cred_id_base64}")

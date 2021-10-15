from rich import print

from fido2.hid import CtapHidDevice
from fido2.client import Fido2Client, WindowsClient
from fido2.server import Fido2Server
from getpass import getpass
from fido2.ctap2 import CredentialManagement
import sys
import ctypes

try:
    from fido2.pcsc import CtapPcscDevice
except ImportError:
    CtapPcscDevice = None


def enumerate_devices():
    for dev in CtapHidDevice.list_devices():
        yield dev
    if CtapPcscDevice:
        for dev in CtapPcscDevice.list_devices():
            yield dev


use_prompt = False
pin = None
uv = "discouraged"

if WindowsClient.is_available() and not ctypes.windll.shell32.IsUserAnAdmin():
    # Use the Windows WebAuthn API if available, and we're not running as admin
    client = WindowsClient("https://example.com")
else:
    # Locate a device
    for dev in enumerate_devices():
        print(dev)
        client = Fido2Client(dev, "https://example.com")
        if client.info.options.get("rk"):
            use_prompt = not (CtapPcscDevice and isinstance(dev, CtapPcscDevice))
            break
    else:
        print("No Authenticator with support for resident key found!")
        sys.exit(1)

    # Prefer UV if supported
    if client.info.options.get("uv"):
        uv = "preferred"
        print("Authenticator supports User Verification")
    elif client.info.options.get("clientPin"):
        # Prompt for PIN if needed
        pin = getpass("Please enter PIN: ")
    else:
        print("PIN not set, won't use")


server = Fido2Server({"id": "example.com", "name": "Example RP"}, attestation="direct")

user = {"id": b"user_id", "name": "A. User"}

# Prepare parameters for makeCredential
create_options, state = server.register_begin(
    user,
    resident_key=True,
    user_verification=uv,
    authenticator_attachment="cross-platform",
)

# Create a credential
if use_prompt:
    print("\nTouch your authenticator device now...\n")

result = client.make_credential(create_options["publicKey"], pin=pin)


# Complete registration
auth_data = server.register_complete(
    state, result.client_data, result.attestation_object
)
credentials = [auth_data.credential_data]

print("New credential created!")

print("CLIENT DATA:", result.client_data)
print("ATTESTATION OBJECT:", result.attestation_object)
print()
print("CREDENTIAL DATA:", auth_data.credential_data)


# Prepare parameters for getAssertion
request_options, state = server.authenticate_begin(user_verification=uv)

# Authenticate the credential
if use_prompt:
    print("\nTouch your authenticator device now...\n")

selection = client.get_assertion(request_options["publicKey"], pin=pin)
result = selection.get_response(0)  # There may be multiple responses, get the first.

print("USER ID:", result.user_handle)

# Complete authenticator
server.authenticate_complete(
    state,
    credentials,
    result.credential_id,
    result.client_data,
    result.authenticator_data,
    result.signature,
)

print("Credential authenticated!")

print("CLIENT DATA:", result.client_data)
print()
print("AUTHENTICATOR DATA:", result.authenticator_data)

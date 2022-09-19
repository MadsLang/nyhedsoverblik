import oci
from borneo import NoSQLHandle, NoSQLHandleConfig, Regions
from borneo.iam import SignatureProvider
from credentials import TENANT_ID, USER_ID, PRIVATE_KEY, FINGERPRINT, PASS_PHRASE


config_with_key_file = {
    "user": USER_ID,
    "key_file": PRIVATE_KEY,
    "fingerprint": FINGERPRINT,
    "tenancy": TENANT_ID,
    "region": 'eu-stockholm-1 '
}
oci.config.validate_config(config_with_key_file)





# create AuthorizationProvider
provider = SignatureProvider(
    tenant_id=TENANT_ID,
    user_id=USER_ID,
    fingerprint=FINGERPRINT,
    private_key=PRIVATE_KEY,
    region='eu-stockholm-1',
    pass_phrase=PASS_PHRASE
)

# create handle config using the correct desired region as endpoint, add a
# default compartment.
config = NoSQLHandleConfig(Regions.EU_STOCKHOLM_1).set_authorization_provider(
    provider).set_default_compartment('sandbox')

# create the handle
handle = NoSQLHandle(config)

print("hello world!")



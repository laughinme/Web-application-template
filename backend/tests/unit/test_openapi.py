from app.core.errors import ErrorCode
from app.main import create_app
from tests.conftest import build_settings


def test_openapi_publishes_the_error_contract() -> None:
    # The frontend generates its types from this schema, including the list of error codes.
    schema = create_app(build_settings()).openapi()

    assert schema["components"]["schemas"]["ErrorCode"]["enum"] == [
        code.value for code in ErrorCode
    ]
    responses = schema["paths"]["/api/v1/users/me"]["get"]["responses"]
    assert responses["4XX"]["content"]["application/json"]["schema"]["$ref"].endswith("/Problem")

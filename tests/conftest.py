from dataclasses import dataclass

import pytest
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2


@dataclass
class LambdaContext:
    function_name: str = "test"
    memory_limit_in_mb: int = 128
    invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:test"
    aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"


@pytest.fixture()
def lambda_context() -> LambdaContext:
    return LambdaContext()


@pytest.fixture()
def api_gw_event() -> APIGatewayProxyEventV2:
    event_body = {
        "headers": {},
        "body": "",
        "requestContext": {
            "http": {
                "method": "GET",
                "path": "/",
                "protocol": "HTTP/1.1",
                "sourceIp": "192.168.0.1/32",
                "userAgent": "agent",
            },
            "stage": "$default",
        },
        "queryStringParameters": {
            "league_id": "48242",
            "team_name": "Singing%20Frogs",
        },
        "rawPath": "/",
    }
    return APIGatewayProxyEventV2(event_body)

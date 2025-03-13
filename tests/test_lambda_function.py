from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEventV2
from aws_lambda_powertools.utilities.typing import LambdaContext

from lambda_function import lambda_handler


def test_lambda_handler(api_gw_event: APIGatewayProxyEventV2, lambda_context: LambdaContext) -> None:
    response = lambda_handler(event=api_gw_event, context=lambda_context)
    assert response["statusCode"] == 200
    assert "BEGIN:VCALENDAR" in response["body"]

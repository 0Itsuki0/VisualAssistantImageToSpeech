from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway, 
    RemovalPolicy,
    Duration, 
    aws_iam as iam
)
from constructs import Construct

class ImageToSpeechAwsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.OPENAI_API_KEY = "openai_api_key_placeholder"
        self.build_lambda()
        self.build_api_gateway()

    def build_lambda(self):
        self.lambda_from_image = _lambda.DockerImageFunction(
            scope=self,
            id="image_to_speech",
            function_name="image_to_speech",
            code=_lambda.DockerImageCode.from_image_asset(
                directory="lambda_function"
            ), 
            timeout=Duration.minutes(5)
        )
        self.lambda_from_image.add_environment(
            key="OPENAI_API_KEY",
            value=self.OPENAI_API_KEY
        )
        
        self.lambda_from_image.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW, 
                actions=[
                    "polly:SynthesizeSpeech"
                ], 
                resources=["*"]
            )
        )
        
        self.lambda_from_image.apply_removal_policy(RemovalPolicy.DESTROY)


    def build_api_gateway(self):

        self.apigateway_role = iam.Role(
            scope=self, 
            id="apigatewayLambdaRole", 
            role_name="apigatewayLambdaRole", 
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com")
        )
        
        self.apigateway_role.apply_removal_policy(RemovalPolicy.DESTROY)
        self.apigateway_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonAPIGatewayPushToCloudWatchLogs")
        )
        self.apigateway_role.apply_removal_policy(RemovalPolicy.DESTROY)
        
        self.apigateway = apigateway.RestApi(
            scope=self, 
            id="imageToSpeechAPI", 
            rest_api_name="imageToSpeechAPI", 
            cloud_watch_role=True,
            endpoint_types=[apigateway.EndpointType.REGIONAL],
            deploy=True,
            binary_media_types=["*/*"]
        )
        
        self.apigateway.apply_removal_policy(RemovalPolicy.DESTROY)
        
        self.apigateway.root.add_proxy(
            default_integration = apigateway.LambdaIntegration(
                handler = self.lambda_from_image,
                proxy = True,
                content_handling = apigateway.ContentHandling.CONVERT_TO_TEXT,
                credentials_role=self.apigateway_role,
            )
        )
        
        self.lambda_from_image.grant_invoke(self.apigateway_role)

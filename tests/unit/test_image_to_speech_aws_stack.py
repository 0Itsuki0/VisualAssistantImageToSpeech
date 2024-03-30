import aws_cdk as core
import aws_cdk.assertions as assertions

from image_to_speech_aws.image_to_speech_aws_stack import ImageToSpeechAwsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in image_to_speech_aws/image_to_speech_aws_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ImageToSpeechAwsStack(app, "image-to-speech-aws")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

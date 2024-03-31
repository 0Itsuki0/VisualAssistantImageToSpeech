
from PIL import Image
from io import BytesIO
import base64
import os

from openai import OpenAI

openai = OpenAI(
	api_key=os.getenv("OPENAI_API_KEY")
)

import boto3
from botocore.response import StreamingBody
polly = boto3.client('polly')
voice_id_jp = "Takumi"
voice_id_en = "Matthew"


def handler(event, context):
    print(event)
    try: 
        base64_original = event['body']
        image_format, base64_resized = process_image(base64_original)
        image_description = describe_image(image_format, base64_resized)
        audio_stream = text_to_voice(image_description)
        base_64_audio_stream = base64.b64encode(audio_stream.read()).decode('utf-8')
        return {
            'headers': { "Content-Type": "audio/mpeg" },
            'statusCode': 200,
            'body': base_64_audio_stream,
            'isBase64Encoded': True
        }
    except Exception as error:
        print(error)       
        return {
            'headers': { "Content-type": "text/html" },
            'statusCode': 400,
            'body': f"Error occured: {error}"
        }
    
    
    
def resize_image(img: Image) -> Image:
    image_resize = img
    if (image_resize.width > image_resize.height):
        while (image_resize.width > 2000 or image_resize.height > 768):
            image_resize = image_resize.resize((image_resize.width // 2, image_resize.height // 2))   
    else: 
        while (image_resize.height > 2000 or image_resize.width > 768):
            image_resize = image_resize.resize((image_resize.width // 2, image_resize.height // 2))   

    return image_resize



def process_image(base64_image_string: str) -> tuple[str, str]:
    img = Image.open(BytesIO(base64.b64decode(base64_image_string)))
    img_resize = resize_image(img)
    buffered = BytesIO()
    img_resize.save(buffered, format=img.format)
    return (img.format, base64.b64encode(buffered.getvalue()).decode('utf-8'))

    
def describe_image(image_format: str, base64_image: str) -> str:
    response = openai.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text", 
                        "text": "You are a visual assistant."
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": "Describe the image within 50 words. If the image is a document, article, or a form, summarize the content within 50 words."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_format};base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    
    return response.choices[0].message.content

def text_to_voice(text: str) -> StreamingBody:
    response = polly.synthesize_speech(
        Engine='standard',
        # LanguageCode='ja-JP',
        LanguageCode = "en-US",
        OutputFormat='mp3',
        Text=text,
        TextType='text',
        VoiceId=voice_id_en
    )
    return response['AudioStream']
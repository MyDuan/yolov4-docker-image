import boto3
client = boto3.client('sagemaker-runtime')
img = open('test.jpg', 'rb').read()
response = client.invoke_endpoint(
    EndpointName='yolov4-model-endpoint',
        Body=bytearray(img),
            ContentType='image/jpeg',
                Accept='image/jpeg'
                )

result = response['Body'].read()
print(result)
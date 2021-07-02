import boto3


def handler(event, context):

    bucket = event["Parameters"]["S3bucket"]
    key = event["Parameters"]["S3key"]
    s3 = boto3.resource("s3")
    obj = s3.Object(
        bucket_name=bucket,
        key=key,
    )
    obj_body = obj.get()["Body"].read()

    # sagemakerのapiを叩く
    client = boto3.client("sagemaker-runtime", region_name="ap-northeast-1")
    response = client.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        Body=bytearray(obj_body),
        ContentType="image/jpeg",
        Accept="image/jpeg",
    )
    result = json.loads(response["Body"].read())

    return 200
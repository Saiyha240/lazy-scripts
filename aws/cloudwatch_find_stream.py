import boto3


class Found(Exception): pass


"""
Easily delete log groups using regex
"""

# Checking /aws/lambda/test-dev-collection-builder...
# 2019/03/20/[$LATEST]f07282db6f754d3a923c26e6f6dc75eb


regions = boto3.session.Session().get_available_regions('logs')
region = 'ap-northeast-1'

stream_name = '2019/08/05/[$LATEST]9bdb4da74beb4677b374d3d6b4d17283'

client = boto3.client('logs', region_name=region)
next_token = None

response = client.describe_log_groups(
    logGroupNamePrefix='/'
)

try:
    while True:
        for log_group in response['logGroups']:
            print('Checking {0}...'.format(log_group['logGroupName']))

            streams = client.describe_log_streams(
                logGroupName=log_group['logGroupName']
            )

            if len(streams['logStreams']):
                for stream in streams['logStreams']:
                    if stream_name == stream['logStreamName']:
                        print('FOUND')
                        raise Found

        if 'nextToken' not in response:
            break

        response = client.describe_log_groups(
            logGroupNamePrefix='/',
            nextToken=response['nextToken']
        )
except Found:
    pass

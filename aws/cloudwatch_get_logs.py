import datetime
from typing import NamedTuple

import boto3

PROFILE = 'dnp-dmps-stg'
LOG_GROUP = '/aws/lambda/DnpPosStg24-a0026d-stg24-code-stack-APIHandler-PZ5TEF54GUQQ'


class LogItem(NamedTuple):
    timestamp: int
    message: str
    ingestionTime: int


class StreamItem(NamedTuple):
    logStreamName: str
    creationTime: int
    firstEventTimestamp: int
    lastEventTimestamp: int
    lastIngestionTime: int
    uploadSequenceToken: str
    arn: str
    storedBytes: int


def log_events_time_range(**kwargs):
    utc_now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    start_time = utc_now - datetime.timedelta(**kwargs)
    end_time = utc_now + datetime.timedelta(**kwargs)

    return start_time, end_time


def boto_client(service: str):
    session = boto3.Session(profile_name=PROFILE)
    client = session.client(service)

    return client


def boto_resource(service: str):
    session = boto3.Session(profile_name=PROFILE)
    resource = session.resource(service)

    return resource


def get_log_streams(log_group_name: str, next_token: str = None) -> StreamItem:
    cw_logs_client = boto_client('logs')

    parameters = dict(
        logGroupName=log_group_name,
        orderBy='LastEventTime',
        descending=True,
        nextToken=next_token
    )

    if next_token is None:
        del parameters['nextToken']

    response = cw_logs_client.describe_log_streams(**parameters)

    for stream in response['logStreams']:
        yield StreamItem(*list(stream.values()))

    if 'nextToken' in response:
        get_log_streams(log_group_name, next_token=response['nextToken'])


def get_log_events(log_group_name: str, log_stream_name: str, next_token: str = None) -> LogItem:
    cw_logs_client = boto_client('logs')

    start_time, end_time = log_events_time_range(hours=1)

    parameters = dict(
        logGroupName=log_group_name,
        logStreamName=log_stream_name,
        startTime=int(start_time.timestamp() * 1000),
        endTime=int(end_time.timestamp() * 1000),
        nextToken=next_token
    )

    if next_token is None:
        del parameters['nextToken']

    response = cw_logs_client.get_log_events(**parameters)

    for log_item in response['events']:
        yield LogItem(*list(log_item.values()))

    if 'nextToken' in response:
        get_log_streams(log_group_name, log_stream_name, next_token=response['nextToken'])


def run():
    for stream in get_log_streams(LOG_GROUP):
        for log_item in get_log_events(LOG_GROUP, stream.logStreamName):
            print(log_item.message)


if __name__ == '__main__':
    run()

"""
Finds log groups with partial matching name and deletes them

Parameters:
    --search-name The partial/full name of the log group/s
    --regions List of regions to search for LogGroups

Example:
    python cloudwatch_logs_deleter.py --name /aws/lambda/test --regions ap-northeast-1 us-west-1
    python cloudwatch_logs_deleter.py --name aws --regions ap-northeast-1
"""
import argparse
import re
from argparse import Namespace
from typing import List, Dict

import boto3


def get_all_log_groups(log_group_name: str, region: str, next_token: str = None) -> List[Dict]:
    cloud_watch_client = boto3.client('logs', region_name=region)

    log_groups = []

    parameters = {
        'nextToken': next_token
    }

    if next_token is None:
        del parameters['nextToken']

    try:
        response = cloud_watch_client.describe_log_groups(**parameters)

        if 'nextToken' in response:
            log_groups += get_all_log_groups(next_token=response['nextToken'])

        log_groups += response['logGroups']

        for log_group in log_groups:
            if re.search(log_group_name, log_group['logGroupName']):
                yield log_group['logGroupName']
    except cloud_watch_client.exceptions.UnrecognizedClientException:
        pass


def get_regions(regions: List) -> List:
    regions_all = boto3.session.Session().get_available_regions('logs')

    for region in regions:
        if region in regions_all:
            yield region


def run(args: Namespace) -> None:
    for region in get_regions(args.regions):
        client = boto3.client('logs', region_name=region)
        print(f'[{region}]')

        for log_group in get_all_log_groups(args.name, region):
            print(f'\t{log_group}')
            # client.delete_log_group(logGroupName=log_group)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Finds log groups with partial matching name and deletes them'
    )

    parser.add_argument('--name', type=str, required=True)
    parser.add_argument('--regions', nargs="+", required=True)

    args = parser.parse_args()

    run(args)

"""
Finds the stacks where a resource with a specific type exists

Parameters:
    --resource-type The resource type with respect to AWS CloudFormation

Example:
    python cloudformation_resource_finder.py --resource-type SecurityGroup
"""
import argparse
from collections import defaultdict
from typing import Dict

import boto3

cf_client = boto3.client('cloudformation')


def get_stacks(next_token: str = None):
    stacks = []

    options = {
        'NextToken': next_token,
        'StackStatusFilter': [
            'CREATE_COMPLETE',
            'CREATE_IN_PROGRESS',
            'ROLLBACK_FAILED',
            'ROLLBACK_COMPLETE',
            'DELETE_FAILED',
            'UPDATE_COMPLETE'
        ]
    }

    if next_token is None:
        del options['NextToken']

    response = cf_client.list_stacks(**options)

    cloudformation = boto3.resource('cloudformation')

    if 'NextToken' in response:
        stacks += get_stacks(next_token=response['NextToken'])

    stacks += [cloudformation.Stack(stack['StackName']) for stack in response['StackSummaries']]

    return stacks


def find_resource_in_stacks(resource_type: str) -> Dict:
    results = defaultdict(list)

    for stack in get_stacks():
        for resource in stack.resource_summaries.all():
            if resource_type in resource.resource_type:
                results[stack.name].append(resource)

    return results


def run(resource_type: str) -> None:
    stacks = find_resource_in_stacks(resource_type)

    for stack_name in stacks.keys():
        print(f"[{stack_name}]")
        for resource in stacks[stack_name]:
            print(f'\t {resource.resource_type}: {resource.logical_id}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Finds the stacks where a resource with a specific type exists'
    )

    parser.add_argument('--resource-type', type=str, required=True)

    args = parser.parse_args()

    run(args.resource_type)

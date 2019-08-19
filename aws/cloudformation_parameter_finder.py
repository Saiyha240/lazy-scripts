"""
Finds the stack where a specified parameter value was used

Parameters:
    --parameter-value The value or part of the value of the parameter

Example:
    python cloudformation_parameter_finder.py --parameter-value value
"""
import argparse
import re

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


def run(parameter_value: str) -> None:
    for stack in get_stacks():
        stack_parameters = stack.parameters

        if stack_parameters is None:
            continue

        results = []

        for parameter in stack_parameters:
            if re.search(parameter_value, parameter['ParameterValue']):
                results.append((parameter['ParameterKey'], parameter['ParameterValue']))

        if results:
            print(f'[{stack.name}]')
            for parameter in results:
                print(f'\t {parameter[0]}: {parameter[1]}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Finds the stack where a specified parameter value was used'
    )

    parser.add_argument('--parameter-value', type=str, required=True)

    args = parser.parse_args()

    run(args.parameter_value)

"""
Finds non-existing resources in AWS and deletes their LogGroups. Currently supports the ff:
    API Gateway Execution Logs
    CodeBuild Logs
    Lambda Logs

Example:
    python cloudwatch_logs_missing_resource_logs_deleter.py
"""
import logging
import re
from typing import Dict, List

import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

lambda_client = boto3.client('lambda')
cloud_watch_client = boto3.client('logs')
code_build_client = boto3.client('codebuild')
apig_client = boto3.client('apigateway')


# class LogGroup:
#
#     def __init__(self, client: str, method: str) -> None:
#         self.client = boto3.client(client)
#         self.get_all_method = getattr(self.client, method)
#         self.method_parameters = {}
#         self.token_name = 'nextToken'
#
#         super().__init__()
#
#     def get_log_groups(self, prefix: str = '/', next_token: str = None):
#         log_groups = []
#
#         parameters = {
#             'logGroupNamePrefix': prefix,
#             'nextToken': next_token
#         }
#
#         if next_token is None:
#             del parameters['nextToken']
#
#         response = cloud_watch_client.describe_log_groups(**parameters)
#
#         if 'nextToken' in response:
#             log_groups += get_all_log_groups(next_token=response['nextToken'])
#
#         log_groups += [log_group['logGroupName'] for log_group in response['logGroups']]
#
#         return sorted(log_groups, key=lambda s: s.lower())
#
#     def get_resources(self, next_token: str = None):
#         lambda_functions = []
#
#         if next_token is not None:
#             self.method_parameters[self.token_name] = next_token
#
#         response = lambda_client.list_functions(**self.method_parameters)
#
#         if self.token_name in response:
#             lambda_functions += get_all_functions(marker=response[self.token_name])
#
#         lambda_functions += [lambda_function['FunctionName'] for lambda_function in response['Functions']]
#
#         return sorted(lambda_functions, key=lambda s: s.lower())
#
#
# class LambdaLogGroup(LogGroup):
#
#     def __init__(self) -> None:
#         super().__init__('lambda', 'list_functions')
#
#         self.marker_name = 'nextToken'
#
#
# class ApiGatewayLogGroup(LogGroup):
#     def __init__(self) -> None:
#         super().__init__('apigateway', 'get_rest_apis')
#
#         self.marker_name = 'position'
#
#
# class CodeBuildLogGroup(LogGroup):
#     def __init__(self) -> None:
#         super().__init__('codebuild', 'list_projects')
#
#         self.marker_name = 'NextToken'


def get_all_log_groups(prefix: str = '', next_token: str = None) -> List[Dict]:
    log_groups = []

    parameters = {
        'logGroupNamePrefix': prefix,
        'nextToken': next_token
    }

    if next_token is None:
        del parameters['nextToken']

    if prefix == '':
        del parameters['logGroupNamePrefix']

    response = cloud_watch_client.describe_log_groups(**parameters)

    if 'nextToken' in response:
        log_groups += get_all_log_groups(next_token=response['nextToken'])

    log_groups += [log_group['logGroupName'] for log_group in response['logGroups']]

    return sorted(log_groups, key=lambda s: s.lower())


def get_all_functions(marker: str = None) -> List[Dict]:
    lambda_functions = []

    parameters = {
        'Marker': marker
    }

    if marker is None:
        del parameters['Marker']

    response = lambda_client.list_functions(**parameters)

    if 'NextMark' in response:
        lambda_functions += get_all_functions(marker=response['NextMark'])

    lambda_functions += [lambda_function['FunctionName'] for lambda_function in response['Functions']]

    return sorted(lambda_functions, key=lambda s: s.lower())


def get_all_apis(next_token: str = None) -> List[Dict]:
    apis = []

    parameters = {
        'position': next_token
    }

    if next_token is None:
        del parameters['position']

    response = apig_client.get_rest_apis(**parameters)

    if 'NextToken' in response:
        apis += get_all_apis(next_token=response['position'])

    apis += [api['id'] for api in response['items']]

    return sorted(apis, key=lambda s: s.lower())


def get_all_code_build_projects(next_token: str = None) -> List[Dict]:
    projects = []

    parameters = {
        'sortOrder': 'ASCENDING',
        'sortBy': 'NAME',
        'nextToken': next_token
    }

    if next_token is None:
        del parameters['nextToken']

    response = code_build_client.list_projects(**parameters)

    if 'nextToken' in response:
        projects += get_all_code_build_projects(next_token=response['nextToken'])

    projects += [project_name for project_name in response['projects']]

    return sorted(projects, key=lambda s: s.lower())


def delete_log_groups(prefix: str, resources: List[str], suffix: str = '') -> None:
    log_groups = get_all_log_groups(prefix=prefix)
    deleted_log_groups = []

    for log_group in log_groups:
        try:
            log_group_function_name = re.search(f'^{prefix}(.+){suffix}$', log_group).group(1)
        except AttributeError:
            continue

        if log_group_function_name not in resources:
            print(f'Deleting: {log_group}')

            deleted_log_groups.append(log_group)
            cloud_watch_client.delete_log_group(logGroupName=log_group)

    return deleted_log_groups


def run() -> None:
    lambda_functions = get_all_functions()
    code_build_projects = get_all_code_build_projects()
    apig_apis = get_all_apis()

    logger.info(delete_log_groups('/aws/lambda/', lambda_functions))
    logger.info(delete_log_groups('/aws/codebuild/', code_build_projects))
    logger.info(delete_log_groups('API-Gateway-Execution-Logs_', apig_apis, suffix='/.+'))


if __name__ == '__main__':
    run()

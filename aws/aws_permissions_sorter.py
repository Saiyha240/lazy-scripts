"""
Sorts the permissions inside an AWS Policy Document

Parameters:
    --aws-policy-file The AWS Policy Document in json

Example:
    ./policy.json

        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    ...
                    "Action": [
                        "cloudfront:*"
                        "apigateway:*",
                    ]
                }
            ]
        }

    python aws_permissions_sorter.py --aws-policy-file ./policy.json
"""
import argparse
import json


def run(policy_file: str) -> None:
    with open(policy_file, 'r') as f:
        data = json.load(f)

        for statement in data['Statement']:
            statement['Action'].sort(key=str.casefold)

        json.dump(data, open(policy_file, 'w'), indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sorts the permissions inside an AWS Policy Document')

    parser.add_argument('--aws-policy-file', type=str, required=True)

    args = parser.parse_args()

    run(args.aws_policy_file)

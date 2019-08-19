"""
Edits the aws credentials file to insert keys for MFA enabled services in AWS

Parameters:
    --mfa-serial-number The serial number of the MFA device
    --mfa-token The generated token from the MFA device
    --aws-cred-dir Location of the credentials file
    --aws-profile-name Name of the profile inside the credentials file where the keys will be injected to

Example:
    python aws_creds.py --mfa-serial-number a --mfa-token b --aws-cred-dir c --aws-profile-name d
"""
import argparse
import configparser
from argparse import Namespace

import boto3


def run(args: Namespace) -> None:
    client = boto3.client('sts')

    response = client.get_session_token(
        SerialNumber=args.mfa_serial_number,
        TokenCode=args.mfa_token
    )

    config = configparser.ConfigParser()
    config.sections()

    config.read(args.mfa_cred_dir)

    for key in config[args.aws_profile_name]:
        if key == 'aws_access_key_id':
            config['dnp-temp']['aws_access_key_id'] = response['Credentials']['AccessKeyId']
        elif key == 'aws_secret_access_key':
            config['dnp-temp']['aws_secret_access_key'] = response['Credentials']['SecretAccessKey']
        elif key == 'aws_session_token':
            config['dnp-temp']['aws_session_token'] = response['Credentials']['SessionToken']

    with open(args.mfa_cred_dir, 'w') as configfile:
        config.write(configfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Edits the aws credentials file to insert keys for MFA enabled services in AWS'
    )

    parser.add_argument('--mfa-serial-number', type=str, required=True)
    parser.add_argument('--mfa-token', type=str, required=True)
    parser.add_argument('--aws-cred-dir', type=str, required=True)
    parser.add_argument('--aws-profile-name', type=str, required=True)

    args = parser.parse_args()

    run(args)

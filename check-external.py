#!/usr/bin/python3

import argparse
import hashlib
import hmac
import json
import sys
import urllib.parse
from datetime import datetime

import requests


class ConfigurationError(Exception):
    pass


def load_configuration(configuration_file: str) -> dict:
    try:
        with open(configuration_file, "rt") as f:
            configuration = json.load(f)
    except (IOError, ValueError) as e:
        raise ConfigurationError("could not load configuration file from {}: {}".format(configuration_file, e))

    # verify the configuration file
    real_username = (configuration.get("username") or "").strip()
    real_password = (configuration.get("password") or "").strip()
    if not real_username:
        raise ConfigurationError("no username found in configuration file")
    if not real_password:
        raise ConfigurationError("no password found in configuration file")

    configuration["username"] = real_username
    configuration["password"] = real_password

    duo_configuration = configuration.get("duo") or {}
    if not duo_configuration or not isinstance(duo_configuration, dict):
        raise ConfigurationError("no duo configuration in configuration file")

    ikey = (duo_configuration.get("ikey") or "").strip()
    skey = (duo_configuration.get("skey") or "").strip()
    host = (duo_configuration.get("host") or "").strip()

    if not ikey:
        raise ConfigurationError("missing duo integration key")
    if not skey:
        raise ConfigurationError("missing duo secret key")
    if not host:
        raise ConfigurationError("missing duo host name")

    duo_configuration["ikey"] = ikey
    duo_configuration["skey"] = skey
    duo_configuration["host"] = host

    return configuration


def sign(skey: str, method: str, host: str, path: str, date: str, params: dict):
    canonical_params = []
    for (key, value) in sorted((urllib.parse.quote(key, "~"), urllib.parse.quote(value, "~")) for (key, value) in list(params.items())):
        canonical_params.append("{}={}".format(key, value))

    parts = [
        date,
        method.upper(),
        host.lower(),
        path,
        "&".join(canonical_params),
    ]

    skey = skey.encode("utf-8")
    sig = hmac.new(skey, "\n".join(parts).encode("utf-8"), hashlib.sha1)
    return sig.hexdigest()


def call_duo(username: str, configuration: dict) -> bool:
    ikey = configuration["ikey"]
    skey = configuration["skey"]
    host = configuration["host"]

    now = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S -0000")
    path = "/auth/v2/auth"
    headers = {"Date": now}
    data = {"username": username, "factor": "auto", "device": "auto"}
    auth = (ikey, sign(skey, "POST", host, path, now, data))

    r = requests.post("https://{}{}".format(host, path), headers=headers, data=data, auth=auth)
    return r.status_code == 200


def main(configuration_file: str) -> int:
    try:
        configuration = load_configuration(configuration_file)

        # username comes first on stdin pipe, then the password.
        # we cannot function if we do not have these.
        username = sys.stdin.readline().strip()
        password = sys.stdin.readline().strip()

        if username == "":
            print("user provided no username")
            sys.exit(1)
        if password == "":  # noqa S105
            print("user provided no password")
            sys.exit(1)

        if username == configuration["username"] and password == configuration["password"]:
            if call_duo(username, configuration["duo"]):
                return 0
            else:
                print("second factor failed")
        else:
            print("username or password did not match")

        return 1
    except Exception as e:
        print("could not authenticate user: {}".format(e))
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="check-external")
    parser.add_argument(
        "configuration",
        metavar="FILE",
        help="the path to the authentication configuration",
    )
    args = parser.parse_args()
    sys.exit(main(args.configuration))

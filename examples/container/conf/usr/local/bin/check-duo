#!/usr/bin/python3

import argparse
import hashlib
import hmac
import json
import os
import sys
import typing
import urllib.parse
from datetime import datetime
from http.cookies import SimpleCookie

import requests
from redis import Redis
from schema import And, Optional, Schema, SchemaError, Use  # type: ignore


class ConfigurationError(Exception):
    pass


def load_configuration(configuration_file: str) -> dict:
    try:
        with open(configuration_file, "rt", encoding="utf8") as f:
            configuration = json.load(f)
    except (IOError, ValueError) as e:
        raise ConfigurationError(
            f"could not load configuration file from {configuration_file}: {e}",
        ) from e

    schema = Schema(
        {
            "username": And(str, Use(str.strip), len),
            "password": And(str, Use(str.strip), len),
            "duo": {
                "ikey": And(str, Use(str.strip), len),
                "skey": And(str, Use(str.strip), len),
                "host": And(str, Use(str.strip), len),
            },
            "session": {
                "name": And(str, Use(str.strip), len),
                "expiry": And(Use(int), lambda x: x >= 0),
            },
            "cache": {
                "host": And(str, Use(str.strip), len),
                Optional("port"): And(Use(int), lambda x: x > 0),
                Optional("db"): And(Use(int), lambda x: 0 <= x <= 15),
                Optional("prefix"): And(str, Use(str.strip), len),
            },
        },
    )

    try:
        return schema.validate(configuration)
    except SchemaError as e:
        raise ConfigurationError from e


def sign(skey: str, host: str, path: str, date: str, params: dict) -> str:
    canonical_params = []
    for (key, value) in sorted(
        (urllib.parse.quote(key, "~"), urllib.parse.quote(value, "~"))
        for (key, value) in list(params.items())
    ):
        canonical_params.append(f"{key}={value}")

    parts = [
        date,
        "POST",
        host.lower(),
        path,
        "&".join(canonical_params),
    ]

    sig = hmac.new(skey.encode("utf-8"), "\n".join(parts).encode("utf-8"), hashlib.sha1)
    return sig.hexdigest()


def check_duo(username: str, ip_address: str, configuration: dict) -> bool:
    ikey = configuration["ikey"]
    skey = configuration["skey"]
    host = configuration["host"]

    now = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S -0000")
    request_path = "/auth/v2/auth"
    request_headers = {"Date": now}
    request_data = {
        "username": username,
        "factor": "auto",
        "device": "auto",
        "ipaddr": ip_address,
        "pushinfo": f"IP={ip_address}",
    }

    r = requests.post(
        f"https://{host}{request_path}",
        headers=request_headers,
        data=request_data,
        auth=(ikey, sign(skey, host, request_path, now, request_data)),
    )
    try:
        data = r.json()
    except json.JSONDecodeError as e:
        print(f"unable to parse duo response: {e}")
        return False

    if r.status_code != 200:
        print(
            f"received {r.status_code} from duo: {data['message']}, {data['message_detail']}",
        )
        return False

    response = data.get("response")
    if response is None:
        print("empty response from duo")
        return False

    return response.get("result", "deny") == "allow"


def get_cookie(cookies: str, cookie_name: str) -> typing.Optional[str]:
    parsed_cookies: dict = SimpleCookie(cookies)
    if cookie_name not in parsed_cookies:
        print(f"no cookie named {cookie_name} found in cookies")
        return None

    # see if this key is in redis. if it is then the session is valid and the
    # user is authorized and can continue without doing 2FA again.
    return parsed_cookies[cookie_name].value


def main(configuration_file: str) -> int:
    configuration = load_configuration(configuration_file)

    # username comes first on stdin pipe, then the password.
    # we cannot function if we do not have these.
    username = sys.stdin.readline().strip()
    password = sys.stdin.readline().strip()

    ip_address = os.environ.get("IP", "").strip()
    request_host = os.environ.get("HTTP_HOST", "").strip()
    request_path = os.environ.get("URI", "").strip()
    context = os.environ.get("CONTEXT", "").strip()
    cookies = os.environ.get("COOKIE", "").strip()

    if username == "":
        print(
            f"user provided no username from {ip_address} for {request_host}{request_path}",
        )
        return 1
    if password == "":  # noqa S105
        print(
            f"user provided no password from {ip_address} for {request_host}{request_path}",
        )
        return 1

    if not (
        username == configuration["username"] and password == configuration["password"]
    ):
        print(
            f"username or password did not match from {ip_address} for {request_host}{request_path}",
        )
        return 1

    # username and password are valid
    print(
        f"{username} successfully passed first factor from {ip_address} for {request_host}{request_path}",
    )

    # if they are logging in for the first time then we're good here
    if context == "login":
        return 0

    # if the context is NOT "login" then they are NOT logging in for
    # the first time so we need to check to see if they have passed
    # through duo.
    cookie = get_cookie(cookies, configuration["session"]["name"])
    if cookie is None:
        return 1  # no cookie, no login

    # connect to redis
    prefix = configuration["cache"].pop("prefix", "")
    redis = Redis(**configuration["cache"])
    key = f"{prefix}{cookie}"

    if redis.exists(key):
        # found the key in redis, the user already went through duo
        print(
            f"{username} successfully passed cookie check from {ip_address} for {request_host}{request_path}",
        )
        return 0

    # send the user to duo and if they succeed then save it but
    # with an expiration so that they have to reauthenticate after
    # some configurable period of time.
    duo_success = check_duo(username, ip_address, configuration["duo"])
    if duo_success:
        print(
            f"{username} successfully passed second factor from {ip_address} for {request_host}{request_path}",
        )
        redis.set(
            key,
            json.dumps(
                {
                    "username": username,
                    "timestamp": str(datetime.utcnow()),
                },
            ),
        )
        redis.expire(key, configuration["session"]["expiry"])
        return 0

    print(f"second factor failed from {ip_address} for {request_host}{request_path}")
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="check-duo")
    parser.add_argument(
        "--configuration-file",
        "-c",
        required=True,
        action="store",
        metavar="FILE",
        help="the path to the authentication configuration",
    )
    args = parser.parse_args()

    try:
        sys.exit(main(**vars(args)))
    except Exception as exc:  # noqa W703
        print(f"could not authenticate user: {exc}")
        sys.exit(1)

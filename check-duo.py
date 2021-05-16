#!/usr/bin/python3

import argparse
import hashlib
import hmac
import json
import os
import sys
import urllib.parse
from datetime import datetime
from http.cookies import SimpleCookie
from typing import Union

import requests
from redis import Redis
from schema import And, Optional, Schema, SchemaError, Use


class ConfigurationError(Exception):
    pass


def load_configuration(configuration_file: str) -> dict:
    try:
        with open(configuration_file, "rt") as f:
            configuration = json.load(f)
    except (IOError, ValueError) as e:
        raise ConfigurationError("could not load configuration file from {}: {}".format(configuration_file, e))

    schema = Schema({
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
    })

    try:
        return schema.validate(configuration)
    except SchemaError:
        raise ConfigurationError


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


def check_duo(username: str, configuration: dict) -> bool:
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


def get_cookie(cookies: str, cookie_name: dict) -> Union[str, None]:
    parsed_cookies = SimpleCookie(cookies)
    if cookie_name not in parsed_cookies:
        print("no cookie named {} found in cookies".format(cookie_name))
        return

    # see if this key is in redis. if it is then the session is valid and the
    # user is authorized and can continue without doing 2FA again.
    return parsed_cookies[cookie_name].value


def main(configuration_file: str) -> int:
    try:
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
            print("user provided no username from {} for {}{}".format(ip_address, request_host, request_path))
            return 1
        if password == "":  # noqa S105
            print("user provided no password from {} for {}{}".format(ip_address, request_host, request_path))
            return 1

        if username == configuration["username"] and password == configuration["password"]:
            print("{} successfully passed first factor from {} for {}{}".format(username, ip_address, request_host, request_path))

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
            key = "{}{}".format(prefix, cookie)

            if redis.exists(key):
                # found the key in redis, the user already went through duo
                print("{} successfully passed cookie check from {} for {}{}".format(username, ip_address, request_host, request_path))
                return 0
            else:
                # send the user to duo and if they succeed then save it but
                # with an expiration so that they have to reauthenticate after
                # some configurable period of time.
                duo_success = check_duo(username, configuration["duo"])
                if duo_success:
                    print("{} successfully passed second factor from {} for {}{}".format(username, ip_address, request_host, request_path))
                    redis.set(key, json.dumps({
                        "username": username,
                        "timestamp": str(datetime.utcnow()),
                    }))
                    redis.expire(key, configuration["session"]["expiry"])
                    return 0
                else:
                    print("second factor failed from {} for {}{}".format(ip_address, request_host, request_path))
        else:
            print("username or password did not match from {} for {}{}".format(ip_address, request_host, request_path))

        return 1
    except Exception as e:
        print("could not authenticate user: {}".format(e))
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="check-duo")
    parser.add_argument(
        "--configuration-file",
        required=True,
        action="store",
        metavar="FILE",
        help="the path to the authentication configuration",
    )
    args = parser.parse_args()
    sys.exit(main(**vars(args)))

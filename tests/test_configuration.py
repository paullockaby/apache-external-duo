import os
import tempfile

import pytest

from checkduo import checkduo


def test_configuration() -> None:
    with tempfile.TemporaryDirectory() as t:
        configuration_path = os.path.join(t, "configuration.json")

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            " foobar ": " bazbat "
                        },
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": "  fdsa  ",
                            "host": " api-1234.example.com "
                        },
                        "cache": {
                            "host": "foo.local"
                        },
                        "session": {
                            "name": "foobar",
                            "expiry": "10"
                        }
                    }
                """,
            )

        configuration = checkduo.load_configuration(configuration_path)
        assert configuration == {
            "usernames": {
                "foobar": "bazbat",
            },
            "duo": {
                "ikey": "asdf",
                "skey": "fdsa",
                "host": "api-1234.example.com",
            },
            "cache": {
                "host": "foo.local",
            },
            "session": {
                "name": "foobar",
                "expiry": 10,
            },
        }


def test_missing_configuration() -> None:
    with tempfile.TemporaryDirectory() as t:
        configuration_path = os.path.join(t, "configuration.json")
        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)


def test_invalid_configuration() -> None:
    with tempfile.TemporaryDirectory() as t:
        configuration_path = os.path.join(t, "configuration.json")

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            " foobar ": " bazbat "
                        },
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": "  fdsa  ",
                            "host": " api-1234.example.com ",
                        }
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)


def test_missing_usernames() -> None:
    with tempfile.TemporaryDirectory() as t:
        configuration_path = os.path.join(t, "configuration.json")

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": "  fdsa  ",
                            "host": " api-1234.example.com "
                        },
                        "cache": {
                            "host": "foo.local"
                        },
                        "session": {
                            "name": "foobar",
                            "expiry": "10"
                        }
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)


def test_empty_usernames() -> None:
    with tempfile.TemporaryDirectory() as t:
        configuration_path = os.path.join(t, "configuration.json")

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {},
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": "  fdsa  ",
                            "host": " api-1234.example.com "
                        },
                        "cache": {
                            "host": "foo.local"
                        },
                        "session": {
                            "name": "foobar",
                            "expiry": "10"
                        }
                    }
                """,
            )

        configuration = checkduo.load_configuration(configuration_path)
        assert configuration == {
            "usernames": {},
            "duo": {
                "ikey": "asdf",
                "skey": "fdsa",
                "host": "api-1234.example.com",
            },
            "cache": {
                "host": "foo.local",
            },
            "session": {
                "name": "foobar",
                "expiry": 10,
            },
        }


def test_missing_username() -> None:
    with tempfile.TemporaryDirectory() as t:
        configuration_path = os.path.join(t, "configuration.json")

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            null: " bazbat "
                        },
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": "  fdsa  ",
                            "host": " api-1234.example.com "
                        },
                        "cache": {
                            "host": "foo.local"
                        },
                        "session": {
                            "name": "foobar",
                            "expiry": "10"
                        }
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "": " bazbat "
                        },
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": "  fdsa  ",
                            "host": " api-1234.example.com "
                        },
                        "cache": {
                            "host": "foo.local"
                        },
                        "session": {
                            "name": "foobar",
                            "expiry": "10"
                        }
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)


def test_missing_password() -> None:
    with tempfile.TemporaryDirectory() as t:
        configuration_path = os.path.join(t, "configuration.json")

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "foobar": null
                        },
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": "  fdsa  ",
                            "host": " api-1234.example.com "
                        },
                        "cache": {
                            "host": "foo.local"
                        },
                        "session": {
                            "name": "foobar",
                            "expiry": "10"
                        }
                    }
                """,
            )

        configuration = checkduo.load_configuration(configuration_path)
        assert configuration == {
            "usernames": {
                "foobar": None,
            },
            "duo": {
                "ikey": "asdf",
                "skey": "fdsa",
                "host": "api-1234.example.com",
            },
            "cache": {
                "host": "foo.local",
            },
            "session": {
                "name": "foobar",
                "expiry": 10,
            },
        }

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "foobar": ""
                        },
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": "  fdsa  ",
                            "host": " api-1234.example.com "
                        },
                        "cache": {
                            "host": "foo.local"
                        },
                        "session": {
                            "name": "foobar",
                            "expiry": "10"
                        }
                    }
                """,
            )

        configuration = checkduo.load_configuration(configuration_path)
        assert configuration == {
            "usernames": {
                "foobar": "",
            },
            "duo": {
                "ikey": "asdf",
                "skey": "fdsa",
                "host": "api-1234.example.com",
            },
            "cache": {
                "host": "foo.local",
            },
            "session": {
                "name": "foobar",
                "expiry": 10,
            },
        }


def test_missing_duo() -> None:
    with tempfile.TemporaryDirectory() as t:
        configuration_path = os.path.join(t, "configuration.json")

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    "usernames": {
                        "foobar": "bazbat"
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "foobar": "bazbat"
                        }
                        "duo": null
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "foobar": "bazbat"
                        }
                        "duo": {}
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "foobar": "bazbat"
                        }
                        "duo": ""
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)


def test_missing_ikey() -> None:
    with tempfile.TemporaryDirectory() as t:
        configuration_path = os.path.join(t, "configuration.json")

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "foobar": "bazbat"
                        }
                        "duo": {
                            "skey": "  fdsa  ",
                            "host": " api-1234.example.com "
                        }
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "foobar": "bazbat"
                        }
                        "duo": {
                            "ikey": null,
                            "skey": "  fdsa  ",
                            "host": " api-1234.example.com "
                        }
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "foobar": "bazbat"
                        }
                        "duo": {
                            "ikey": "",
                            "skey": "  fdsa  ",
                            "host": " api-1234.example.com "
                        }
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)


def test_missing_skey() -> None:
    with tempfile.TemporaryDirectory() as t:
        configuration_path = os.path.join(t, "configuration.json")

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "foobar": "bazbat"
                        }
                        "duo": {
                            "ikey": "asdf  ",
                            "host": " api-1234.example.com "
                        }
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "foobar": "bazbat"
                        }
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": null,
                            "host": " api-1234.example.com "
                        }
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "foobar": "bazbat"
                        }
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": "",
                            "host": " api-1234.example.com "
                        }
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)


def test_missing_host() -> None:
    with tempfile.TemporaryDirectory() as t:
        configuration_path = os.path.join(t, "configuration.json")

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "foobar": "bazbat"
                        }
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": "  fdsa  "
                        }
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "foobar": "bazbat"
                        }
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": "  fdsa  ",
                            "host": null
                        }
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "usernames": {
                            "foobar": "bazbat"
                        }
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": "  fdsa  ",
                            "host": ""
                        }
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)


def test_is_valid_password() -> None:
    # no username provided
    assert (
        checkduo.is_valid_password(
            {"foo": "$2y$05$4GIpGUOxzIK61gmshbAprOGNJKSOGmEtVaJZYoX6M5o3CBTXUdSy."},
            "",
            "",
            "127.0.0.1",
            "localhost:8080/login/submit",
        )
        is False
    )

    # no password provided
    assert (
        checkduo.is_valid_password(
            {"foo": "$2y$05$4GIpGUOxzIK61gmshbAprOGNJKSOGmEtVaJZYoX6M5o3CBTXUdSy."},
            "foo",
            "",
            "127.0.0.1",
            "localhost:8080/login/submit",
        )
        is False
    )

    # missing a password list
    assert (
        checkduo.is_valid_password(
            {},
            "foo",
            "password",
            "127.0.0.1",
            "localhost:8080/login/submit",
        )
        is False
    )

    # password is empty
    assert (
        checkduo.is_valid_password(
            {"foo": ""},
            "foo",
            "password",
            "127.0.0.1",
            "localhost:8080/login/submit",
        )
        is False
    )

    # password is missing
    assert (
        checkduo.is_valid_password(
            {"foo": None},
            "foo",
            "password",
            "127.0.0.1",
            "localhost:8080/login/submit",
        )
        is False
    )

    # user not in username list
    assert (
        checkduo.is_valid_password(
            {"foo": "$2y$05$4GIpGUOxzIK61gmshbAprOGNJKSOGmEtVaJZYoX6M5o3CBTXUdSy."},
            "bar",
            "password",
            "127.0.0.1",
            "localhost:8080/login/submit",
        )
        is False
    )

    # password is invalid
    assert (
        checkduo.is_valid_password(
            {"foo": "$2y$05$4GIpGUOxzIK61gmshbAprOGNJKSOGmEtVaJZYoX6M5o3CBTXUdSy."},
            "foo",
            "asdf",
            "127.0.0.1",
            "localhost:8080/login/submit",
        )
        is False
    )

    # password is valid
    assert (
        checkduo.is_valid_password(
            {"foo": "$2y$05$4GIpGUOxzIK61gmshbAprOGNJKSOGmEtVaJZYoX6M5o3CBTXUdSy."},
            "foo",
            "password",
            "127.0.0.1",
            "localhost:8080/login/submit",
        )
        is True
    )


@pytest.mark.skip("not running tests against the duo api")
def test_duo_push() -> None:
    assert checkduo.check_duo(
        username="paul",
        ip_address="127.0.0.1",
        configuration={
            "ikey": "asdf",
            "skey": "fdsa",
            "host": "api-abc123.duosecurity.com",
        },
    )

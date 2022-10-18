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
                        "username": " foobar ",
                        "password": " bazbat ",
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
            "username": "foobar",
            "password": "bazbat",
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
                        "username": " foobar ",
                        "password": " bazbat ",
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


def test_missing_username() -> None:
    with tempfile.TemporaryDirectory() as t:
        configuration_path = os.path.join(t, "configuration.json")

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "password": " bazbat ",
                        "duo": {
                            "ikey": "asdf  ",
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
                        "username": null,
                        "password": " bazbat ",
                        "duo": {
                            "ikey": "asdf  ",
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
                        "username": "",
                        "password": " bazbat ",
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": "  fdsa  ",
                            "host": " api-1234.example.com "
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
                        "username": " foobar ",
                        "duo": {
                            "ikey": "asdf  ",
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
                        "username": " foobar ",
                        "password": null,
                        "duo": {
                            "ikey": "asdf  ",
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
                        "username": " foobar ",
                        "password": "",
                        "duo": {
                            "ikey": "asdf  ",
                            "skey": "  fdsa  ",
                            "host": " api-1234.example.com "
                        }
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)


def test_missing_duo() -> None:
    with tempfile.TemporaryDirectory() as t:
        configuration_path = os.path.join(t, "configuration.json")

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "username": " foobar ",
                        "password": " bazbat ",
                    }
                """,
            )

        with pytest.raises(checkduo.ConfigurationError):
            checkduo.load_configuration(configuration_path)

        with open(configuration_path, "wt", encoding="utf8") as f:
            f.write(
                """
                    {
                        "username": " foobar ",
                        "password": " bazbat ",
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
                        "username": " foobar ",
                        "password": " bazbat ",
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
                        "username": " foobar ",
                        "password": " bazbat ",
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
                        "username": " foobar ",
                        "password": " fdskal ",
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
                        "username": " foobar ",
                        "password": " fdskal ",
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
                        "username": " foobar ",
                        "password": " fdskal ",
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
                        "username": " foobar ",
                        "password": " fdskal ",
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
                        "username": " foobar ",
                        "password": " fdskal ",
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
                        "username": " foobar ",
                        "password": " fdskal ",
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
                        "username": " foobar ",
                        "password": " fdskal ",
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
                        "username": " foobar ",
                        "password": " fdskal ",
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
                        "username": " foobar ",
                        "password": " fdskal ",
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

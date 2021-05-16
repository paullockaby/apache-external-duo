import importlib
import os
import tempfile
import unittest


class TestExternalCheck(unittest.TestCase):
    def setUp(self) -> None:
        self.checker = importlib.import_module("check-duo")
        self.load_configuration = self.checker.load_configuration

    def test_configuration(self):
        with tempfile.TemporaryDirectory() as t:
            configuration_path = os.path.join(t, "configuration.json")

            with open(configuration_path, "wt") as f:
                f.write("""{
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
                }""")

            configuration = self.load_configuration(configuration_path)
            self.assertEqual(configuration, {
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
            })

    def test_missing_configuration(self):
        with tempfile.TemporaryDirectory() as t:
            configuration_path = os.path.join(t, "configuration.json")
            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

    def test_invalid_configuration(self):
        with tempfile.TemporaryDirectory() as t:
            configuration_path = os.path.join(t, "configuration.json")

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": " bazbat ",
                    "duo": {
                        "ikey": "asdf  ",
                        "skey": "  fdsa  ",
                        "host": " api-1234.example.com ",
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

    def test_missing_username(self):
        with tempfile.TemporaryDirectory() as t:
            configuration_path = os.path.join(t, "configuration.json")

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "password": " bazbat ",
                    "duo": {
                        "ikey": "asdf  ",
                        "skey": "  fdsa  ",
                        "host": " api-1234.example.com "
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": null,
                    "password": " bazbat ",
                    "duo": {
                        "ikey": "asdf  ",
                        "skey": "  fdsa  ",
                        "host": " api-1234.example.com "
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": "",
                    "password": " bazbat ",
                    "duo": {
                        "ikey": "asdf  ",
                        "skey": "  fdsa  ",
                        "host": " api-1234.example.com "
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

    def test_missing_password(self):
        with tempfile.TemporaryDirectory() as t:
            configuration_path = os.path.join(t, "configuration.json")

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "duo": {
                        "ikey": "asdf  ",
                        "skey": "  fdsa  ",
                        "host": " api-1234.example.com "
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": null,
                    "duo": {
                        "ikey": "asdf  ",
                        "skey": "  fdsa  ",
                        "host": " api-1234.example.com "
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": "",
                    "duo": {
                        "ikey": "asdf  ",
                        "skey": "  fdsa  ",
                        "host": " api-1234.example.com "
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

    def test_missing_duo(self):
        with tempfile.TemporaryDirectory() as t:
            configuration_path = os.path.join(t, "configuration.json")

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": " bazbat ",
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": " bazbat ",
                    "duo": null
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": " bazbat ",
                    "duo": {}
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": " bazbat ",
                    "duo": ""
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

    def test_missing_ikey(self):
        with tempfile.TemporaryDirectory() as t:
            configuration_path = os.path.join(t, "configuration.json")

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": " fdskal ",
                    "duo": {
                        "skey": "  fdsa  ",
                        "host": " api-1234.example.com "
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": " fdskal ",
                    "duo": {
                        "ikey": null,
                        "skey": "  fdsa  ",
                        "host": " api-1234.example.com "
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": " fdskal ",
                    "duo": {
                        "ikey": "",
                        "skey": "  fdsa  ",
                        "host": " api-1234.example.com "
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

    def test_missing_skey(self):
        with tempfile.TemporaryDirectory() as t:
            configuration_path = os.path.join(t, "configuration.json")

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": " fdskal ",
                    "duo": {
                        "ikey": "asdf  ",
                        "host": " api-1234.example.com "
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": " fdskal ",
                    "duo": {
                        "ikey": "asdf  ",
                        "skey": null,
                        "host": " api-1234.example.com "
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": " fdskal ",
                    "duo": {
                        "ikey": "asdf  ",
                        "skey": "",
                        "host": " api-1234.example.com "
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

    def test_missing_host(self):
        with tempfile.TemporaryDirectory() as t:
            configuration_path = os.path.join(t, "configuration.json")

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": " fdskal ",
                    "duo": {
                        "ikey": "asdf  ",
                        "skey": "  fdsa  "
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": " fdskal ",
                    "duo": {
                        "ikey": "asdf  ",
                        "skey": "  fdsa  ",
                        "host": null
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

            with open(configuration_path, "wt") as f:
                f.write("""{
                    "username": " foobar ",
                    "password": " fdskal ",
                    "duo": {
                        "ikey": "asdf  ",
                        "skey": "  fdsa  ",
                        "host": ""
                    }
                }""")

            with self.assertRaises(self.checker.ConfigurationError):
                self.load_configuration(configuration_path)

    @unittest.skip
    def test_duo_push(self):
        self.assertTrue(self.checker.call_duo(
            username="paul",
            configuration={
                "ikey": "asdf",
                "skey": "fdsa",
                "host": "api-abc123.duosecurity.com",
            },
        ))


if __name__ == '__main__':
    unittest.main()

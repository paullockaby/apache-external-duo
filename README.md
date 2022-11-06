# apache-external-duo
This is a program for setting up Apache with Duo for 2FA so that you do not have to build it into your programs. This tool utilizes these components:

* [mod_auth_form](https://httpd.apache.org/docs/2.4/mod/mod_auth_form.html)
* [mod_auth_external](https://github.com/phokz/mod-auth-external)
* [mod_session](https://httpd.apache.org/docs/2.4/mod/mod_session.html)
* [mod_session_cookie](https://httpd.apache.org/docs/2.4/mod/mod_session_cookie.html)
* [mod_session_crypto](https://httpd.apache.org/docs/2.4/mod/mod_session_crypto.html)
* [redis](https://redis.io)
* [python](https://www.python.org)

Because of implementation details -- specifically that we need a session cookie to keep from making requests to Duo too often -- this only works with Apache's form based authentication system using session cookies and not Apache's regular "basic" authentication system. Finally, you will need to be using a more recent version of Apache. Apache 2.4 on Buster does not work but Apache 2.4 on Bullseye does work.

## Configuring Duo

Before you can use this you must have a Duo account. You should create an application using what is currently called "Partner Auth API". That will give you an `ikey`, `skey`, and a hostname. You need all three of those pieces.

Additionally, you will need to create users in Duo with the same usernames that you're going to use for your authentication system. That is, if you will enter "joe" into the form, you should create a user called "joe" on the Duo control panel.

## Creating The Configuration Files

There are two configuration files that will contain secret information. You should create these files and put them in a location on your server that is relatively protected and ensure that they are owned by root and readable only by root. **DO NOT PUT THESE FILES INTO A CONTAINER.** Mount them into the container. These file contain the keys to the kingdom.

The first configuration file should be called `auth-configuration.json` and look like this:

```json
{
  "usernames": {
    "joe": "$2y$05$6USL7IGYNtGtQrENZ18bEuuNINXSsM6vRnsKME4UCn0Nm4y0lJyZ."
  },
  "duo": {
    "ikey": "Your Application Integration Key",
    "skey": "Your Application Secret Key",
    "host": "api-1234.duosecurity.com"
  },
  "cache": {
    "host": "redis",
    "port": "6379"
  },
  "session": {
    "name": "formsession",
    "expiry": 14400
  }
}
```

The above configuration does a few things:

* Configures a single username "joe" with a password. The password must be hashed with `bcrypt`. You can generate a hashed password using the `htpasswd` tool, like this: `htpasswd -n -B joe`
* Configures the Duo application credentials.
* Configures the Redis credentials. These are passed directly to the Python [redis](https://pypi.org/project/redis/) library so put whatever works with that in here.
* Configures some session details. The `name` must match the cookie that your session uses which is configured in your Apache. The `expiry` is how often, in seconds, you must reauthenticate with Duo.

The second file should contain random text and you can fill it by running something like this:

```
openssl rand -base64 42 > session-secret.txt
```

Again, place these files somewhere on your server and ensure that they are owned by root and readable only by root.

## Running The Example

There is a directory called `example` that contains a working Docker container that starts Apache and protects a directory with Duo 2FA. Important files to review are:

* `example/conf/etc/apache2/sites-enabled/000-default.conf` - configure your web server with the correct values.
* `example/conf/etc/apache2/sites-enabled/100-login.conf` - set the path to the `auth-configuration.json` and `session-secret.txt` files and also configure paths to protect.
* `example/conf/var/www/html/login/index.html` - make your login form look pretty.

Note that this container example **DOES NOT** have SSL configured. It is figured that you will put an SSL terminator in front of your web server and that it will encrypt everything. This example _will_ send your password in cleartext.

You can use the example like this:

0. Change into the example directory: `cd examples`
1. Create a place for all of your secrets: `mkdir private`
2. Create a session secret file: `openssl rand -base64 42 > private/session-secret.txt`
3. Create a configuration file from the example above: `vi private/auth-configuration.json`
4. Build the example container: `docker-compose build`
5. Start up the container: `docker-compose up`
6. Visit [http://localhost:8080/private](http://localhost:8080/private) and log in!

## How Does It Work?

It works like this:

* You try to go to a path that is protected and Apache intercepts that request and sends you to the form you designated for `mod_auth_form`.
* You enter your password and it gets submitted to the submission handler for `mod_auth_form`. The handler uses the external script to verify your username and password. If it matches (i.e. if the external script returns a "0") then you are now logged in. Apache will now create a session using `mod_session` and `mod_session_cookie`. The session cookie contains your username and password. Every time you browse to a protected page Apache read the session cookie and run your username and password through the external script.
* When you navigate to the first page that is _not_ the submission handler a cookie will now exist in your request. This cookie is sent to Redis to see if it is a new session. If the cookie does not exist in Redis then it is a new session and Duo will be pinged. After a successful Duo acknowledgement the session cookie will be stored in Redis with an expiry. When the session cookie expires from Redis then Duo will be pinged again. And repeat.

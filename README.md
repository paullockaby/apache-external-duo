# apache-external-duo
This is a program for setting up Apache with Duo for 2FA so that you do not
have to build it into your programs. This tool utilizes these components:

* [mod_auth_form](https://httpd.apache.org/docs/2.4/mod/mod_auth_form.html)
* [mod_auth_external](https://github.com/phokz/mod-auth-external)
* [mod_session](https://httpd.apache.org/docs/2.4/mod/mod_session.html)
* [mod_session_cookie](https://httpd.apache.org/docs/2.4/mod/mod_session_cookie.html)
* [mod_session_crypto](https://httpd.apache.org/docs/2.4/mod/mod_session_crypto.html)
* [redis](https://redis.io)
* [python](https://www.python.org)

This tool also only works for one user. If you have more than one user you can
start with this tool but you'll need to add your own code to support multiple
users. Read on for how to get this thing going.

## Configuring Duo

Before you can use this you must have a Duo account. You should create an
application using what is currently called "Partner Auth API". That will give
you an `ikey`, `skey`, and a hostname. You need all three of those pieces.

Additionally, you will need to create a user in Duo with the same username that
you're going to use for your authentication system. That is, if you will enter
"joe" into the form, you should create a user called "joe" on the Duo control
panel.

## Creating The Configuration Files

There are two configuration files that will contain secret information. You
should create these and put them somewhere on your server that is relatively
protected and ensure that they are owned by root and readable only by root.
**DO NOT PUT THESE INTO A CONTAINER.** Mount these into the container. These
files are the keys to the kingdom.

The first configuration file should be called `auth-configuration.json` and
look like this:

```json
{
    "username": "joe",
    "password": "s00p3rSekrit!",
    "duo": {
        "ikey": "Your Application Integration Key",
        "skey": "Your Application Secret Key",
        "host": "api-1234.duosecurity.com"
    },
    "cache": {
        "host": "redis.default.svc.cluster.local",
        "port": "6379"
    },
    "session": {
        "name": "formsession",
        "expiry": 14400
    }
}
```

The above configuration does a few things:

* Configures the username "joe" with a password.
* Configures the Duo application credentials.
* Configures the Redis credentials. These are passed directly to the Python
  [redis](https://pypi.org/project/redis/) library so put whatever works with
  that in here.
* Configures some session details. The `name` must match the cookie that your
  session uses which is configured in your Apache. The `expiry` is how often,
  in seconds, you must reauthenticate with Duo.

The second configuration file should be called `session-secret.txt` and contain
some random text. This file is used by Apache to encrypt the session data and
thus encrypt the cookie that gets sent to your browser. If you do not do this
then your session cookie will contain your password in clear text.

Generate this random text by running something like this:

```
openssl rand -base64 42 > session-secret.txt
```

Again, place both of these files somewhere on your server and ensure that they
are owned by root and readable only by root.

## Running The Example

There is a directory called `example` that contains a working Docker container
that starts Apache and protects a directory with Duo 2FA. Important files to
review are:

* `example/conf/etc/apache2/sites-enabled/000-default.conf` - configure your
  web server wtih the correct values.
* `example/conf/etc/apache2/sites-enabled/100-login.conf` - set the path to
  the `auth-configuration.json` and `session-secret.txt` files and also
  configure paths to protect.
* `example/conf/var/www/html/login/index.html` - make your login form look oh
  so pretty.

Note that this container example **DOES NOT** have SSL configured. It is
figured that you will put an SSL terminator in front of your web server and it
will encrypt everything. This example _will_ send your password in cleartext.

## How Does It Work?

It works like this:

* You try to go to a path that is protected and Apache intercepts that request
  and sends you to the form you designated for `mod_auth_form`.
* You enter your password and it gets submitted to the submission handler for
  `mod_auth_form`. The handler uses the external script to verify your username
  and password. If it matches (i.e. if the external script returns a "0") then
  you are now logged in. Apache will now create an encrypted session using
  `mod_session` and `mod_session_cookie` and `mod_session_crypto`. The session
  cookie contains an encrypted form or your username and password. Every time
  you browse to a protected page Apache will decrypt the session cookie and run
  your username and password through the external script.
* When you navigate to the first page that is _not_ the submission handler a
  cookie will now exist in your request. This cookie is sent to Redis to see if
  it is a new session. If the cookie does not exist in Redis then it is a new
  session and Duo will be pinged. After a successful Duo acknowledgement the
  session cookie will be stored in Redis with an expiry. When the session
  cookie expires from Redis then Duo will be pinged again. And repeat.

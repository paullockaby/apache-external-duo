FROM debian:bullseye-slim@sha256:b0d53c872fd640c2af2608ba1e693cfc7dedea30abcd8f584b23d583ec6dadc7 AS base

# first install apache
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      apache2 apache2-utils \
      libapache2-mod-authnz-external python3 python3-requests python3-redis python3-schema sudo \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# then set up the configuration
RUN a2dismod autoindex access_compat status -f \
 && a2disconf security serve-cgi-bin other-vhosts-access-log -f \
 && a2enmod \
      remoteip headers rewrite deflate authnz_external \
      auth_form session session_cookie session_crypto request \
 && sed -i '/^ErrorLog/d' /etc/apache2/apache2.conf \
 && rm -rf /var/www/html

COPY /conf /

EXPOSE 80/tcp
ENTRYPOINT ["/entrypoint"]

FROM python:2.7-onbuild

# Update the package repository
RUN set -x; \
        apt-get update \
        && apt-get install -y --no-install-recommends \
            locales

# Configure timezone and locale
RUN echo "America/Sao_Paulo" > /etc/timezone; dpkg-reconfigure -f noninteractive tzdata
RUN echo 'pt_BR.UTF-8 UTF-8' >> /etc/locale.gen && locale-gen && DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales


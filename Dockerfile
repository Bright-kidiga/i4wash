# Base image
FROM python:3.11-slim

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PIP_NO_CACHE_DIR=1
ENV FRAPPE_USER=frappe
ENV FRAPPE_HOME=/home/$FRAPPE_USER
#ENV SITE_NAME=
ENV DB_HOST=
#ENV DB_NAME=
#ENV DB_USER=
#ENV DB_PASSWORD=
#ENV ADMIN_PASSWORD=
ENV DB_SSLMODE=disable
ENV DB_ALLOW_PUBLIC_KEY_RETRIEVAL=1

ENV SITE_NAME=web.apps.i4wash.com
ENV DB_ROOT_PASSWORD=example_root_password
ENV ADMIN_PASSWORD=admin123

# Install system dependencies (as root)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl wget vim libffi-dev libssl-dev python3-dev python3-setuptools \
    redis-server redis-tools supervisor unzip gnupg cron \
    && wget https://dev.mysql.com/get/mysql-apt-config_0.8.25-1_all.deb \
    && DEBIAN_FRONTEND=noninteractive dpkg -i mysql-apt-config_0.8.25-1_all.deb \
    && apt-get update && apt-get install -y mysql-client \
    && apt-get clean && rm -rf /var/lib/apt/lists/*



# Install Node.js 20.x
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Install Yarn via npm
RUN npm install -g yarn

# Create frappe user and switch
RUN useradd -ms /bin/bash $FRAPPE_USER
WORKDIR $FRAPPE_HOME
USER $FRAPPE_USER

# Install Bench
RUN pip install --upgrade pip
RUN pip install frappe-bench

# Add bench to PATH
ENV PATH=$FRAPPE_HOME/.local/bin:$PATH

# Initialize bench (without creating a site)
RUN bench init frappe-bench --frappe-branch version-15 --python python3
WORKDIR $FRAPPE_HOME/frappe-bench

# Copy entrypoint
COPY --chown=frappe:frappe entrypoint.sh /home/frappe/entrypoint.sh
RUN chmod +x /home/frappe/entrypoint.sh

# Expose ports
EXPOSE 8000 9000
ENTRYPOINT ["/home/frappe/entrypoint.sh"]

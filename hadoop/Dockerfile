FROM debian:bullseye-slim

ENV DEBIAN_FRONTEND=noninteractive

# bullseye ya está archivado: apuntamos apt al archivo de Debian
RUN sed -i 's|deb.debian.org|archive.debian.org|g; s|security.debian.org|archive.debian.org|g' /etc/apt/sources.list \
    && echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99archive

# Java, Python 3 y utilidades
RUN apt-get update && apt-get install -y --no-install-recommends \
        openjdk-11-jdk-headless \
        python3 \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Ruta estable de Java
RUN ln -s "$(dirname "$(dirname "$(readlink -f "$(which java)")")")" /opt/java

# Descargar e instalar Hadoop
ARG HADOOP_VERSION=3.3.6
RUN curl -fsSL https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
    | tar -xz -C /opt \
    && mv /opt/hadoop-${HADOOP_VERSION} /opt/hadoop

# Variables de entorno
ENV JAVA_HOME=/opt/java
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Hadoop necesita saber dónde está Java
RUN echo "export JAVA_HOME=${JAVA_HOME}" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh

# Carpetas de trabajo
RUN mkdir -p /data/input /data/output /app
WORKDIR /app

# ---------- SSH (Parte B) ----------
RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server openssh-client \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd

# Usuario sin contraseña: el '*' bloquea el login por password, solo entra con llave
RUN useradd -m -s /bin/bash hduser \
    && usermod -p '*' hduser \
    && chown -R hduser:hduser /data /app

# Endurecer sshd: solo llaves, sin root
RUN echo "PasswordAuthentication no" >> /etc/ssh/sshd_config \
    && echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config \
    && echo "PermitRootLogin no" >> /etc/ssh/sshd_config

# Cliente SSH: no preguntar por "yes/no" al conectar a hosts nuevos
RUN mkdir -p /home/hduser/.ssh \
    && printf 'Host *\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null\n  LogLevel ERROR\n' > /home/hduser/.ssh/config \
    && chown -R hduser:hduser /home/hduser/.ssh \
    && chmod 700 /home/hduser/.ssh \
    && chmod 600 /home/hduser/.ssh/config

COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
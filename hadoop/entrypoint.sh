#!/bin/bash
set -e

SSH_DIR=/home/hduser/.ssh

# Llaves de host del servidor SSH
ssh-keygen -A

# Par de llaves de hduser (sin passphrase), solo si aún no existen
if [ ! -f "$SSH_DIR/id_ed25519" ]; then
    ssh-keygen -t ed25519 -N "" -q -f "$SSH_DIR/id_ed25519"
    cat "$SSH_DIR/id_ed25519.pub" >> "$SSH_DIR/authorized_keys"
fi
chmod 600 "$SSH_DIR/authorized_keys"
chown -R hduser:hduser "$SSH_DIR"

# Si existe el volumen compartido, publica la llave privada (la usará el contenedor api)
if [ -d /shared-keys ]; then
    cp "$SSH_DIR/id_ed25519" /shared-keys/id_ed25519
    chmod 600 /shared-keys/id_ed25519
fi

# Deja sshd en primer plano para que el contenedor siga vivo
exec /usr/sbin/sshd -D -e
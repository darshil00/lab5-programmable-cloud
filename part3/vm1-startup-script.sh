#!/bin/bash
set -e

mkdir -p /srv
cd /srv

curl http://metadata/computeMetadata/v1/instance/attributes/vm2-startup-script \
  -H "Metadata-Flavor: Google" \
  > /srv/vm2-startup-script.sh

curl http://metadata/computeMetadata/v1/instance/attributes/vm1-launch-vm2-code \
  -H "Metadata-Flavor: Google" \
  > /srv/vm1-launch-vm2.py

curl http://metadata/computeMetadata/v1/instance/attributes/service-credentials \
  -H "Metadata-Flavor: Google" \
  > /srv/service-credentials.json

curl http://metadata/computeMetadata/v1/instance/attributes/project \
  -H "Metadata-Flavor: Google" \
  > /srv/project

export GOOGLE_CLOUD_PROJECT=$(cat /srv/project)
export GOOGLE_APPLICATION_CREDENTIALS=/srv/service-credentials.json

apt-get update
apt-get install -y python3-pip

pip3 install \
  google-api-python-client \
  google-auth \
  google-auth-httplib2

python3 /srv/vm1-launch-vm2.py \
  > /var/log/vm1-launch-vm2.log 2>&1

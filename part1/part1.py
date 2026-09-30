#!/usr/bin/env python3

import time

import google.auth
import googleapiclient.discovery


credentials, project = google.auth.default()

compute = googleapiclient.discovery.build(
    "compute",
    "v1",
    credentials=credentials
)


ZONE = "us-central1-a"
INSTANCE_NAME = "lab5-part1"
MACHINE_TYPE = "f1-micro"

FIREWALL_NAME = "allow-5000"
NETWORK_TAG = "allow-5000"


def wait_for_zone_operation(compute, project, zone, operation_name):
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation_name
        ).execute()

        if result["status"] == "DONE":
            if "error" in result:
                raise Exception(result["error"])
            return result

        time.sleep(1)


def wait_for_global_operation(compute, project, operation_name):
    while True:
        result = compute.globalOperations().get(
            project=project,
            operation=operation_name
        ).execute()

        if result["status"] == "DONE":
            if "error" in result:
                raise Exception(result["error"])
            return result

        time.sleep(1)


def firewall_exists(compute, project, firewall_name):
    result = compute.firewalls().list(
        project=project
    ).execute()

    for firewall in result.get("items", []):
        if firewall["name"] == firewall_name:
            return True

    return False


def create_firewall(compute, project):
    if firewall_exists(compute, project, FIREWALL_NAME):
        print(f"Firewall rule '{FIREWALL_NAME}' already exists.")
        return

    firewall_config = {
        "name": FIREWALL_NAME,
        "network": "global/networks/default",
        "direction": "INGRESS",
        "priority": 1000,
        "sourceRanges": ["0.0.0.0/0"],
        "targetTags": [NETWORK_TAG],
        "allowed": [
            {
                "IPProtocol": "tcp",
                "ports": ["5000"]
            }
        ]
    }

    print(f"Creating firewall rule '{FIREWALL_NAME}'...")

    operation = compute.firewalls().insert(
        project=project,
        body=firewall_config
    ).execute()

    wait_for_global_operation(
        compute,
        project,
        operation["name"]
    )

    print("Firewall rule created.")


def create_instance(compute, project, zone, name):
    image_response = compute.images().getFromFamily(
        project="ubuntu-os-cloud",
        family="ubuntu-2204-lts"
    ).execute()

    source_image = image_response["selfLink"]

    startup_script = """#!/bin/bash
set -e

mkdir -p /opt/lab5
cd /opt/lab5

sudo apt-get update
sudo apt-get install -y python3 python3-pip git

git clone https://github.com/cu-csci-4253-datacenter/flask-tutorial

cd flask-tutorial

sudo python3 setup.py install
sudo pip3 install -e .

export FLASK_APP=flaskr
flask init-db

nohup flask run -h 0.0.0.0 > /var/log/flask.log 2>&1 &
"""

    machine_type = f"zones/{zone}/machineTypes/{MACHINE_TYPE}"

    config = {
        "name": name,

        "machineType": machine_type,

        "disks": [
            {
                "boot": True,
                "autoDelete": True,
                "initializeParams": {
                    "sourceImage": source_image
                }
            }
        ],

        "networkInterfaces": [
            {
                "network": "global/networks/default",
                "accessConfigs": [
                    {
                        "type": "ONE_TO_ONE_NAT",
                        "name": "External NAT"
                    }
                ]
            }
        ],

        "metadata": {
            "items": [
                {
                    "key": "startup-script",
                    "value": startup_script
                }
            ]
        }
    }

    print(f"Creating VM '{name}'...")

    operation = compute.instances().insert(
        project=project,
        zone=zone,
        body=config
    ).execute()

    wait_for_zone_operation(
        compute,
        project,
        zone,
        operation["name"]
    )

    print("VM creation completed.")


def add_network_tag(compute, project, zone, instance_name):
    instance = compute.instances().get(
        project=project,
        zone=zone,
        instance=instance_name
    ).execute()

    fingerprint = instance["tags"]["fingerprint"]

    body = {
        "items": [NETWORK_TAG],
        "fingerprint": fingerprint
    }

    print(f"Applying network tag '{NETWORK_TAG}'...")

    operation = compute.instances().setTags(
        project=project,
        zone=zone,
        instance=instance_name,
        body=body
    ).execute()

    wait_for_zone_operation(
        compute,
        project,
        zone,
        operation["name"]
    )

    print("Network tag applied.")


def get_external_ip(compute, project, zone, instance_name):
    instance = compute.instances().get(
        project=project,
        zone=zone,
        instance=instance_name
    ).execute()

    for interface in instance.get("networkInterfaces", []):
        for access_config in interface.get("accessConfigs", []):
            if "natIP" in access_config:
                return access_config["natIP"]

    return None


def main():
    print(f"Project: {project}")
    print(f"Zone: {ZONE}")

    create_firewall(
        compute,
        project
    )

    create_instance(
        compute,
        project,
        ZONE,
        INSTANCE_NAME
    )

    add_network_tag(
        compute,
        project,
        ZONE,
        INSTANCE_NAME
    )

    time.sleep(5)

    external_ip = get_external_ip(
        compute,
        project,
        ZONE,
        INSTANCE_NAME
    )

    if external_ip:
        print()
        print("VM created successfully.")
        print(f"Instance: {INSTANCE_NAME}")
        print(f"External IP: {external_ip}")
        print()
        print("The Flask application should be available at:")
        print(f"http://{external_ip}:5000")
    else:
        print("VM created, but no external IP was found.")


if __name__ == "__main__":
    main()

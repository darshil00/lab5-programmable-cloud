#!/usr/bin/env python3

import os
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
INSTANCE_NAME = "lab5-part3-vm2"


def wait_for_operation(compute, project, zone, operation_name):
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


def create_vm2():
    with open("/srv/vm2-startup-script.sh", "r") as f:
        startup_script = f.read()

    image_response = compute.images().getFromFamily(
        project="ubuntu-os-cloud",
        family="ubuntu-2204-lts"
    ).execute()

    source_image = image_response["selfLink"]

    config = {
        "name": INSTANCE_NAME,

        "machineType": f"zones/{ZONE}/machineTypes/f1-micro",

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
        },

        "tags": {
            "items": ["allow-5000"]
        }
    }

    print(f"Creating {INSTANCE_NAME}...")

    operation = compute.instances().insert(
        project=project,
        zone=ZONE,
        body=config
    ).execute()

    wait_for_operation(
        compute,
        project,
        ZONE,
        operation["name"]
    )

    print(f"{INSTANCE_NAME} created.")


if __name__ == "__main__":
    create_vm2()

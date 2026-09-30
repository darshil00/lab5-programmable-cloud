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
MACHINE_TYPE = "f1-micro"
SNAPSHOT_NAME = "base-snapshot-lab5-part1"

INSTANCE_NAMES = [
    "lab5-part2-1",
    "lab5-part2-2",
    "lab5-part2-3"
]


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


def create_instance_from_snapshot(
    compute,
    project,
    zone,
    instance_name,
    snapshot_name
):

    machine_type = (
        f"zones/{zone}/machineTypes/{MACHINE_TYPE}"
    )

    snapshot = (
        f"projects/{project}/global/snapshots/{snapshot_name}"
    )

    config = {
        "name": instance_name,

        "machineType": machine_type,

        "disks": [
            {
                "boot": True,
                "autoDelete": True,

                "initializeParams": {
                    "sourceSnapshot": snapshot
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

        "tags": {
            "items": ["allow-5000"]
        }
    }

    start_time = time.time()

    operation = compute.instances().insert(
        project=project,
        zone=zone,
        body=config
    ).execute()

    wait_for_operation(
        compute,
        project,
        zone,
        operation["name"]
    )

    end_time = time.time()

    return end_time - start_time


def main():

    print(f"Project: {project}")
    print(f"Zone: {ZONE}")
    print(f"Snapshot: {SNAPSHOT_NAME}")
    print()

    timings = []

    for instance_name in INSTANCE_NAMES:

        print(f"Creating {instance_name}...")

        elapsed = create_instance_from_snapshot(
            compute,
            project,
            ZONE,
            instance_name,
            SNAPSHOT_NAME
        )

        timings.append(
            (instance_name, elapsed)
        )

        print(
            f"{instance_name} created in "
            f"{elapsed:.2f} seconds"
        )

        print()

    print("Final timing results:")

    for instance_name, elapsed in timings:
        print(
            f"{instance_name}: "
            f"{elapsed:.2f} seconds"
        )


if __name__ == "__main__":
    main()

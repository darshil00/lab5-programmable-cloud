# Part 2 VM Creation Timing

The three VM instances were created from the `base-snapshot-lab5-part1` snapshot.

| Instance | Creation Time |
|---|---:|
| lab5-part2-1 | 28.01 seconds |
| lab5-part2-2 | 50.80 seconds |
| lab5-part2-3 | 24.82 seconds |

## Note

The assignment specified the use of region `us-west1-b`. However, Google Cloud repeatedly returned `ZONE_RESOURCE_POOL_EXHAUSTED` when attempting to provision the required VMs in that zone. The experiment was therefore performed in the `us-central1-a` zone.

## Case ID: SF-12345
## Title: topology-merge times out under load
## Service: topology-merge
## Symptoms:
- Error: "Timeout waiting for merge lock"
- Logs: `WARN  c.i.t.m.LockManager - Lock wait > 30s`
- Env: OpenShift, 5-node Cassandra

## Root Cause:
Cassandra P99 latency > 1s due to tombstone overload from old topology records.

## Fix:
Ran `nodetool compact topology_keyspace merge_lock_table` and increased compaction throughput.

## Links:
- [Slack Thread](https://slack.com/...)
- [Internal Doc](https://w3.ibm.com/...)
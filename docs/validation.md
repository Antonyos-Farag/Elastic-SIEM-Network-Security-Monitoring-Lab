# Validation & troubleshooting runbook

[← Project overview](../README.md)

**Status:** proposed acceptance tests, not completed results. Run only within the authorized lab. Establish a baseline and a rollback plan before disconnecting anything.

## Baseline checklist

| Check | Pass criterion | Evidence to retain |
| --- | --- | --- |
| Platform health | Elasticsearch, Kibana, Logstash respond as expected | Sanitized service/API output and UTC time |
| Fleet management | Fleet Server and each intended endpoint healthy | Hostname, policy, last check-in; no tokens |
| Endpoint event generation | Test event exists in the local selected channel | Host, record ID, channel, source timestamp |
| Endpoint delivery | Same event found in Elasticsearch | Index, document ID, host, timestamp and ingest time |
| Firewall delivery | Unique benign firewall event indexed | Source event/session identifier and parsed document |
| Field/time quality | Source identity and full timezone-aware time correct | Original vs parsed values |
| Detection | Expected rule fires for the controlled event pattern | Rule ID/version, window, source docs, alert ID |

For any failed check, stop and resolve the ingestion path before interpreting an absent alert.

## Troubleshoot in order

1. **Source:** does the event exist locally? Is the audit/Sysmon configuration enabled?
2. **Shipper:** is the service healthy? Check config/output tests and error logs.
3. **Transport:** confirm route, DNS, TCP/UDP, port, firewall policy, and TLS trust. A successful ping is insufficient.
4. **Listener:** confirm the bound interface and protocol. Beats/TCP cannot use a raw UDP input.
5. **Pipeline:** inspect parsing errors, queue/backpressure, output authorization, and certificate errors.
6. **Index:** inspect the correct index/data stream, document count, source host, and ingest time.
7. **UI/rule:** check data view, time range/timezone, field types, rule schedule, exclusions, and permissions.

For syslog, resolve UDP/514 versus UDP/5514 before treating an empty packet capture as a source failure. For Windows 10, reproduce and resolve the documented TCP/5044 failure.

## Outage tests

For every test: record a test ID, UTC start/end, expected path, baseline event count, and rollback. Emit uniquely identifiable benign events before, during, and after the outage. Restore one component at a time; compare source records with indexed records after recovery.

| Scenario | Action inside isolated lab | Acceptance / limitation |
| --- | --- | --- |
| Firewall outage | Temporarily disable the relevant FortiGate path | Endpoint logs continue only if an independent route exists; prove it with route and event evidence |
| Elastic outage | Stop the relevant central service | Show firewall inspection/local retention separately; central monitoring is expected to be unavailable |
| Logstash outage | Stop collector, continue safe test events, restore | Measure replay, loss, queue/disk use, and duplicates; UDP loss may be unrecoverable |
| Endpoint link loss | Remove Windows 10's primary telemetry path | Show actual alternate route or relay and received events; otherwise mark failover unsupported |
| Time skew | Compare synchronized clocks before testing | Do not deliberately skew production/DC clocks; document any timestamp discrepancy |

### Measure, do not infer

- Count expected unique source events, received unique events, missing events, and duplicates.
- Measure delivery/replay latency using synchronized source and ingest timestamps.
- Record the longest outage tested and queue/local-retention limits.
- Note whether FortiGate local storage survives a reboot and whether missed syslog is replayed.
- Record residual gaps even if services recover successfully.

A healthy service after restart is not proof of zero event loss. This single-host Elastic design does not provide storage or service high availability.

## Exit criteria

A claim is ready to publish only when its scope, test conditions, expected behavior, actual result, and sanitized supporting evidence are recorded. Use [the evidence record](../examples/evidence-record.md) and update [the evidence register](evidence.md).

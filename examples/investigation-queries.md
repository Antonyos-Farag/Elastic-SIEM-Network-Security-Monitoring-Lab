# Investigation query starters

[← Project overview](../README.md)

**Illustrative KQL for Kibana Discover—not exported detection rules or verified lab results.** Select an appropriate data view and a narrow UTC time range. Confirm field names and types in a sample document first. Raw FortiGate/Logstash records may not be ECS-normalized, and unparsed messages will require different queries.

## Windows failed logons

For ECS/Winlogbeat-style mappings where `event.code` is a keyword:

```text
event.code: "4625"
```

Scope to one host:

```text
event.code: "4625" and host.name: "YOUR_WINDOWS_HOST"
```

If your mapping uses `winlog.event_id`, inspect its type and use the corresponding field/value instead. A 4625 match is not automatically a brute-force alert. Compare account, source, status/substatus, and repetition in the bounded test window.

## Sysmon process telemetry

```text
winlog.channel: "Microsoft-Windows-Sysmon/Operational" and event.code: "1"
```

Inspect process, parent process, command line, user, and host. Process-creation events on the Windows target will not necessarily show the Nmap or Hydra process running on Kali.

## Known test source

After substituting your authorized test source address, for ECS-normalized records:

```text
source.ip: "192.0.2.10"
```

`192.0.2.10` is a documentation-only placeholder. Restrict the data view to the intended firewall or endpoint records; compare distinct destination ports and actions within the exercise window. KQL filters documents—it does not calculate a scan-rate threshold.

## FortiGate traffic records

For ECS-normalized fields only:

```text
event.module: "fortinet" and source.ip: "192.0.2.10"
```

A custom Logstash pipeline might not populate `event.module`. In that case select the `fortigate-*` data view and use the actual parsed source/action fields. Do not interpret a zero-result query as no attack until parsing and time range have been verified.

## From search to detection

1. Confirm a known test event matches the query.
2. Define the detection hypothesis, aggregation/grouping keys, threshold, window, and schedule.
3. Evaluate normal traffic and expected false positives.
4. Run the controlled test and capture the resulting alert plus its source events.
5. Document tuning and limitations before claiming a working detection.

No query here is a deployed or tested rule. The supplied report contains no detection-rule export.

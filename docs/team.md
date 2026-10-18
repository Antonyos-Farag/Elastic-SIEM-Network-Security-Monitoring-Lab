# Team responsibilities

[← Project overview](../README.md)

The supplied revised report organizes the work into three tracks. This describes responsibilities, not named contributor attribution.

| Track | Responsibilities | Handoff evidence |
| --- | --- | --- |
| **SOC Engineer** | Ubuntu Elastic platform, Kibana, Fleet Server, endpoint instrumentation, Windows Server roles, Windows environment configuration | Service health, endpoint policies, local events, per-host ingestion checks |
| **Network Security** | Windows connectivity, FortiGate policy/syslog, Logstash integration, addressing, VM networking, controlled reconnaissance and SMB exercises | As-built topology, protocol/port plan, sanitized policy/configuration, packet and index evidence |
| **SOC Analyst** | Detection rules, monitoring views, investigation and event correlation | Rule definitions, dashboards, matched alerts, investigation timelines and findings |

## Handoff checklist

- Engineer → Network Security: endpoint addresses, required ports, selected shipper, CA requirements, and known failures.
- Network Security → Analyst: source inventory, index/data-stream names, parsed field mappings, timezone, and controlled exercise windows.
- Analyst → Engineer/Network Security: missing channels, parsing issues, false positives, clock drift, and visibility gaps.

## Source limitations

The report explicitly states that NAS connectivity is not evidenced. It also states that analyst rule creation, monitoring dashboards, and investigation captures are absent. Those work items must not be marked complete based solely on platform installation or populated indices.

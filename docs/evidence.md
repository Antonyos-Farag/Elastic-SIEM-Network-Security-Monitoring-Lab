# Evidence & results

[← Project overview](../README.md)

## Sources and publication policy

This repository was prepared from:

1. The project author's narrative describing the end-to-end build, endpoint Elastic Agents, attack simulations, detection analysis, and resilience goals.
2. The supplied **SOC_Lab_Documentation_Revised_Task_Distribution.pdf**, a 34-page revised report with numbered figures and three responsibility tracks.

References below point to that supplied report. The PDF is not committed because its text and screenshots may expose passwords, service/enrollment tokens, setup codes, or internal details. No raw screenshots have been republished. If adding evidence, first redact it and follow [security guidance](../SECURITY.md).

**Evidence levels:** *Reported* means stated by the author; *documented* means described/shown in the supplied report; *proposed* means a future test or improvement. Neither documentation nor this repository constitutes a fresh execution of the lab.

## Evidence register

| Item | Source | What is supported | Boundary |
| --- | --- | --- | --- |
| Elasticsearch | pp. 3–5, Figs. 1–4 | Installation, active service, HTTPS node response | Package version labels are source claims, not independently verified |
| Kibana | pp. 5–10, Figs. 5–9 | Installation and successful configuration | No analyst dashboard demonstrated |
| Fleet Server | pp. 10–14, Figs. 10–14 | Successful install, connected state, healthy Ubuntu agent | Windows endpoint enrollments not shown |
| Windows Server roles | pp. 14–16, Figs. 15–20 | AD DS/DHCP/DNS role selection, forest/promotion settings | Completed promotion, DHCP setup, and client domain join not proven |
| Sysmon | pp. 16–18, Figs. 21, 23 | Server install and Windows 10 configuration update | Not proof every desired event type is enabled |
| Winlogbeat | pp. 18–19, Figs. 24–25 | Server service running; Windows 10 connectivity tested | Windows 10 TCP/5044 test failed |
| Windows connectivity | pp. 19–22, Figs. 26–27, 48 | Addressing and successful gateway pings | Does not demonstrate a Windows relay or failover route |
| FortiGate policy | p. 22, Fig. 42 | Allow policy with antivirus/web filtering | Not an attack-specific detection result |
| Syslog export | pp. 23–24, Figs. 28–30 | Sender configured; collector ping succeeds | Ping alone does not establish syslog delivery |
| Logstash & indices | pp. 24–27, Figs. 31–36 | Service/config checks and populated indices | Protocol/port inconsistencies remain unresolved |
| Nmap | pp. 27–28, Figs. 40–41 | Hosts/services enumerated in controlled scans | No corresponding SIEM alert capture supplied |
| Hydra / NetExec | pp. 29–30, Fig. 39 | Hydra error and SMB fingerprinting/authentication failures | No successful password discovery shown |
| Metasploit | pp. 28–29, Figs. 37–38 | Console/module setup and target configuration | No successful session shown |
| Analyst activities | p. 34, §§3.1–3.3 | Report explicitly states missing rule/dashboard/investigation captures | Author-reported detection verification remains uncorroborated here |
| Resilience | Author narrative | Alternative-path objective | No timed outage, relay, replay, or recovery evidence supplied |

## Known issues to resolve

### 1. Windows ingestion protocol mismatch

Figure 33 describes a Logstash UDP/5044 input. Winlogbeat's Logstash output uses Beats over TCP, requiring a compatible Beats listener. Figure 25 also shows a failed TCP/5044 check. Correct the listener and validate an actual Windows 10 event end to end.

### 2. Syslog port mismatch

FortiGate sender screenshots specify UDP/514; a later packet check uses UDP/5514. Document any redirect/forwarding or align the ports, then verify a unique event across sender, listener, and index.

### 3. Unsafe example settings in the source

The captured Elasticsearch outputs use the `elastic` superuser and disable TLS certificate verification. These are not recommended deployment defaults. Replace them with a least-privilege writer and verified TLS, using a keystore or equivalent secret storage.

### 4. Addressing and time consistency

Captures span several subnets and setup states; do not combine their IP addresses into an asserted final topology. A FortiGate time-sync warning also appears. Establish an as-built addressing plan and verify UTC correlation across sources.

### 5. Reachability is not failover

Gateway ping success and a shared subnet do not prove direct peer connectivity, log relaying, or recovery behavior. One Kali capture shows a reachable gateway, while another shows `Destination Host Unreachable`; treat these as separate observed states, not one stable baseline.

## Evidence still needed

- Sanitized final topology with interface, gateway, and routing details.
- Healthy endpoint enrollment and event receipt for each Windows host/channel.
- Compatible sender/listener configurations with secrets removed.
- Unique-event trace from FortiGate through Logstash into Elasticsearch.
- Rule exports and source-event-to-alert correlation for controlled attacks.
- Dashboard/investigation captures with timestamps, timezone, and query scope.
- Outage tests including event loss, duplicates, replay delay, and local retention limits.

Use the [evidence template](../examples/evidence-record.md) to record future results. Missing evidence should remain visibly missing—not be replaced with illustrative screenshots presented as real results.

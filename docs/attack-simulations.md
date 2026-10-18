# Controlled attack simulations

[← Project overview](../README.md)

> Run only against explicitly authorized lab targets. Use an isolated network, disposable test accounts, low attempt rates, snapshots, and a defined stop condition. Do not run attacks against public, shared, or production systems.

## Exercise workflow

1. Record authorization, target, source, test account, UTC window, and rollback.
2. Confirm baseline telemetry and clock synchronization.
3. Start one controlled activity at a time with a deliberately small scope.
4. Capture tool outcome separately from target events, firewall logs, and SIEM alerts.
5. Correlate the same source/target/time window across layers.
6. Stop, clean up, and record both observed results and missing evidence.

## 01 · Nmap reconnaissance

**Objective:** observe how connection attempts and service discovery appear in network and endpoint telemetry.

The supplied report shows a full-port service/script scan of one lab edge address and a service scan of an internal address (Figs. 40–41). The edge scan reports most ports filtered and HTTPS open; the internal scan identifies Windows-associated services and FortiGuard proxy/web-filter responses. Service banners are observations, not definitive proof of OS identity or exploitation.

For a new baseline, start with a narrow, authorized service-discovery scan rather than copying the source's broad full-port scan:

```bash
# Replace the placeholder only with a target you are authorized to test.
nmap -sV -p 443 --max-rate 10 <AUTHORIZED_LAB_TARGET>
```

**Look for:** source/destination addresses, connection bursts, allowed/denied actions, destination ports, and any enabled IPS signatures. Sysmon network events depend on configuration and do not necessarily expose every inbound scan.

**Evidence gap:** no source-event-to-alert linkage is supplied. A filtered-port result is not by itself a FortiGate detection alert.

## 02 · Hydra password-attack exercise

**Objective:** evaluate visibility into repeated authentication attempts using a disposable lab account and a small bounded credential set.

The author reports a Hydra password-attack exercise. Figure 39 documents an SMB attempt that returns **`invalid reply from target`**. It does not show a recovered password or successful authentication. Subsequent NetExec output identifies a Windows host/domain but returns **`STATUS_NO_LOGON_SERVERS`** for the captured credential attempts.

For a repeat test:

- Verify the target service, tool/protocol compatibility, and account lockout policy first.
- Limit concurrency and attempts; establish a stop condition before starting.
- Keep credential lists and passwords out of Git and screenshots.
- Verify whether the target actually generated authentication events. A tool error is not proof of a failed logon event.
- Distinguish wrong credentials from domain-controller reachability and protocol errors.

**Look for:** Security event 4625 where auditing applies, authentication context, account, source address, status/substatus, and firewall connection logs. Event location and fields vary by authentication protocol and domain role.

**Evidence gap:** the report supplies no corresponding Kibana investigation or rule-trigger screenshot.

## 03 · Supplementary Metasploit / SMB activity

The report shows a Samba module selected and configured (Figs. 37–38), but **no successful session**. Configuring an exploit module does not prove a Windows target is vulnerable to it. This repository does not present the module setup as a successful compromise.

## Correlation worksheet

| Layer | Capture | What it establishes |
| --- | --- | --- |
| Test source | Tool, bounded scope, start/end time, outcome | What was attempted—not necessarily what reached the target |
| Target | Local event ID, source/account, status | What the target actually recorded |
| FortiGate | Traffic/security event, policy, action, source/target | What traversed an inspected/logged path |
| Elastic | Indexed document IDs and parsed fields | What arrived and became searchable |
| Detection | Rule version, match window, alert ID | Whether a configured rule actually triggered |
| Analyst | Timeline and reasoned conclusion | Interpretation grounded in evidence |

Use [starter queries](../examples/investigation-queries.md) only after validating your field mappings. Record the exercise with [an evidence record](../examples/evidence-record.md).

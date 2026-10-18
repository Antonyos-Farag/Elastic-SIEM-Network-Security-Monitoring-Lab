# Build guide

[← Project overview](../README.md) · [Detailed device configuration](configuration.md) · [Backup-line designs](backup-lines.md) · [PDF screenshots](screenshots.md)

This is an operator workflow, not a tested automated installer. Commands below are diagnostic examples. Obtain packages and version-specific installation instructions from the relevant vendor, verify checksums, and select a mutually compatible, supported stack version. The supplied report labels its Elastic packages **9.4.4**; that label is preserved as source metadata, not independently verified release guidance.

## 1 · Plan and isolate

Prepare Ubuntu, Windows 10, Windows Server, FortiGate, and an authorized test VM. Size resources for the selected versions and log volume; source VM screenshots are not a sizing benchmark.

Record before installation:

- Hostnames, static/reserved addresses, subnets, gateways, DNS, and time sources.
- Which interfaces carry management, telemetry, and simulated attack traffic.
- Sender/listener protocol and port pairs, including any syslog port forwarding.
- Certificate names, CA distribution, service identities, and retention limits.
- Snapshot/backup and rollback procedures.

Use an isolated lab network. The report used VMware bridged adapters; bridging alone neither guarantees a shared subnet nor isolates attack traffic.

## 2 · Install Elasticsearch and Kibana

1. Install verified Elasticsearch packages on Ubuntu and retain the security auto-configuration.
2. Bind only the required interface; limit TCP/9200 to trusted peers.
3. Install compatible Kibana, complete its enrollment, and protect browser access with TLS.
4. Store passwords and enrollment material outside Git. Use the generated CA or your lab CA rather than disabling certificate checks.
5. Verify both services and an authenticated HTTPS API response.

```bash
sudo systemctl status elasticsearch kibana --no-pager
# Prompts for the password; use your real hostname, user, and CA path.
curl --cacert /path/to/http_ca.crt --user YOUR_READ_USER https://elastic.lab.example:9200/
```

The service check does not replace application-level authentication and index access testing.

## 3 · Configure Fleet and endpoint collection

1. Add Fleet Server in Kibana with a reachable HTTPS hostname and port.
2. Use the generated enrollment command securely on the designated Ubuntu host.
3. Confirm Fleet Server is healthy.
4. Enroll each Windows endpoint with the correct policy and trusted CA.
5. Capture each endpoint's hostname, policy, status, and last check-in without exposing tokens.

**Collection decision:** use Elastic Agent integrations or standalone Winlogbeat for each channel. Do not enable both against the same channel by accident. The source report demonstrates Fleet Server enrollment and Winlogbeat setup, but does not show both Windows endpoint Agent enrollments.

## 4 · Instrument Windows

Install Sysmon using a reviewed XML configuration appropriate for the lab. Confirm the Sysmon Operational channel contains events. Enable the Windows audit policies needed for the test, including failed logons where appropriate.

For a standalone Winlogbeat path:

1. Select Security, System, Application, and required Sysmon channels.
2. Configure `output.logstash` to the selected collector's **Beats/TCP** listener.
3. Distribute the CA and configure TLS on both ends.
4. Run Winlogbeat's configuration/output tests from its install directory.
5. Start the service and verify a new event in Elasticsearch for **each** host/channel.

```powershell
Get-Service Sysmon64, winlogbeat
Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' -MaxEvents 3
Test-NetConnection -ComputerName logstash.lab.example -Port 5044
.\winlogbeat.exe test config -c .\winlogbeat.yml
.\winlogbeat.exe test output -c .\winlogbeat.yml
```

Adjust service names if using a different Sysmon binary or Elastic Agent instead of Winlogbeat. `TcpTestSucceeded: True` is a transport check, not proof that events were indexed.

Windows Server AD DS, DNS, and DHCP roles are part of the source setup. Configure them only if required by your topology; role selection and promotion settings are not proof of a completed working domain join.

## 5 · Integrate FortiGate through Logstash

1. Create narrowly scoped lab traffic policies and enable the required traffic/security logging.
2. Configure syslog to the Ubuntu collector's reachable address and agreed protocol/port.
3. Configure a matching Logstash listener and parsing for the actual FortiOS event format.
4. Preserve original messages, parse full timestamps with timezone, and normalize fields where possible.
5. Use a dedicated Elasticsearch writer with trusted TLS and secret storage.
6. Generate a benign firewall event and prove it reaches a queryable index.

Do not copy the source's superuser output credentials or `ssl_verification_mode => "none"`. Do not treat UDP/514 and UDP/5514 as equivalent without a documented mapping. Privileged ports may require OS-level handling; do not run the entire collector as root just to bind UDP/514.

```bash
sudo systemctl status logstash --no-pager
sudo ss -lntup
# Substitute the syslog port actually selected for the lab.
sudo tcpdump -ni any udp port 5514 -c 10
```

Packet arrival proves only arrival—not successful parsing, indexing, or source attribution. Captures may contain sensitive payloads.

## 6 · Prove the baseline before attacks

Use the [validation runbook](validation.md). Require per-source ingestion, accurate timestamps, and a working search before running simulations. Investigate the source report's failed Windows TCP/5044 check rather than assuming later index screenshots resolve it.

## 7 · Add detection content and resilience tests

Start from [investigation queries](../examples/investigation-queries.md), verify field mappings, then build and test rules. Record rule definitions, thresholds, time windows, source events, and resulting alerts. Query matches alone are not a detection-rule deployment.

Only after baseline ingestion passes should you test disconnections, queue exhaustion, and recovery. Keep all disruptive changes inside the authorized lab and record rollback steps.

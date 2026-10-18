# Device-by-device configuration

[← Overview](../README.md) · [Backup lines](backup-lines.md) · [PDF screenshots](screenshots.md)

This guide separates **captured settings** from **recommended rebuild steps**. Examples are configuration templates, not files recovered from the machines and not tested deployments. Use vendor instructions for the installed version. Take snapshots and keep console access before changing addresses, routes, certificates, or domain roles.

## 1. Establish one consistent network plan

The PDF contains different addresses at different stages. The following observations are useful for understanding the screenshots, but are **not a proven final topology**:

| Device / service | Address visible in report | Evidence / qualification |
| --- | --- | --- |
| Windows 10 | `10.150.0.177/16`, gateway `10.150.0.1` | Fig. 26/48; gateway `10.10.10.1` also pinged |
| Windows Server | `10.150.0.175`, gateway `10.150.0.1` | Fig. 27; report describes common `/16` segment |
| Logstash destination | `10.150.0.185:5044` | Windows test; TCP failed |
| FortiGate management | `10.150.0.184` | Fig. 42 policy view |
| FortiGate reachable interface | `10.10.10.1` | Windows ping tests; exact interface mapping not supplied |
| FortiGate syslog destination | `192.168.111.45:514/UDP` | Figs. 28–30; later capture checks UDP/5514 |
| Elasticsearch | `192.168.100.30:9200/HTTPS` | Fig. 4; another setup stage |
| Fleet Server | `192.168.119.128:8220` | Fig. 11; another setup stage |

For a rebuild, choose **one** address plan. Fill in hostnames, IP/prefix, gateway, DNS, interface/VMnet, and permitted peers for every device. Do not assign all observed Ubuntu addresses to one host without confirming its actual NICs and routes.

### Example connectivity contract

| Initiator | Destination | Required service | Why |
| --- | --- | --- | --- |
| Windows endpoints | Domain controller | AD DNS, Kerberos, LDAP, SMB and required RPC | Domain operations; use Microsoft's role-specific port guidance |
| Windows Winlogbeat | Logstash | TCP/5044 with TLS | Endpoint event transport |
| Windows Elastic Agent | Fleet Server | HTTPS/TCP/8220 | Enrollment and policy management |
| Windows Elastic Agent | Its configured output | HTTPS/9200 or configured Logstash endpoint | Actual event delivery; separate from Fleet management |
| FortiGate | Logstash | Chosen syslog transport/port | Firewall log export |
| Logstash | Elasticsearch | HTTPS/TCP/9200 | Index events |
| Kibana | Elasticsearch | HTTPS/TCP/9200 | Search and application data |
| Analyst workstation | Kibana | HTTPS service; default application port 5601 | Analyst access |

Restrict by source/destination, not broad `ANY` rules. A connection's return traffic must also have a valid route. Shared subnets communicate directly through Layer 2; routed destinations require gateways and return routes.

## 2. Windows 10 configuration

### What the report actually shows

- Address `10.150.0.177`, mask `255.255.0.0`, gateway `10.150.0.1`.
- Successful ping to `10.10.10.1`.
- Sysmon already installed; XML configuration validated and updated (Fig. 23).
- Ping to collector succeeds but **TCP/5044 fails** (Fig. 25).
- Endpoint Elastic Agent enrollment is author-reported, not shown in the supplied captures.

![Windows 10 collector connectivity test from PDF Figure 25](../assets/evidence/windows10-connectivity.png)

*Historical test, not a success screenshot: IP reachability worked, but the TCP listener was not reachable.*

### Rebuild procedure

1. Attach the VM NIC to the intended isolated Windows network. Give the NIC a meaningful name; record its MAC and VMnet/switch.
2. In `ncpa.cpl` → adapter Properties → IPv4, configure the planned address, prefix, gateway, and DNS. Use either a static address or a controlled DHCP reservation, not a conflicting mixture.
3. If joining a domain, point DNS to the lab domain controller, not a public resolver. Confirm the domain's DNS records resolve before joining. Join through System Properties and reboot when requested.
4. Synchronize time with the domain hierarchy. Authentication and event correlation are sensitive to clock errors.
5. Install Sysmon with a reviewed XML config. Check existing installation before reinstalling:

```powershell
# Run elevated, from the reviewed Sysmon package directory.
Get-Service Sysmon64 -ErrorAction SilentlyContinue
# New install only:
.\Sysmon64.exe -i .\sysmonconfig.xml -accepteula
# Existing install: use this instead of reinstalling.
.\Sysmon64.exe -c .\sysmonconfig.xml
Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' -MaxEvents 5
```

6. Enable the audit categories required by your exercises. Inspect effective policy with `auditpol /get /category:*`; do not assume Sysmon substitutes for Security logon auditing.
7. Choose Elastic Agent integrations **or** standalone Winlogbeat for each channel. If using Fleet, enroll using the private generated command and a trusted CA; verify the Windows host policy and data output, not only Fleet Server status.
8. For standalone Winlogbeat, use a template like the following, adjusted to actual names and paths:

```yaml
# Illustrative winlogbeat.yml fragment; not a recovered lab config.
winlogbeat.event_logs:
  - name: Application
  - name: System
  - name: Security
  - name: Microsoft-Windows-Sysmon/Operational
output.logstash:
  hosts: ["logstash.lab.example:5044"]
  ssl.certificate_authorities: ['C:\Lab\certs\lab-ca.crt']
```

Disable any conflicting active output. The CA must trust the Logstash server certificate; its DNS name must match the configured host. Add client certificate/key settings only if the collector requires mutual TLS. Secure keys and configuration permissions.

9. Install the Winlogbeat service with the package's elevated installation script, then validate:

```powershell
.\winlogbeat.exe test config -c .\winlogbeat.yml
.\winlogbeat.exe test output -c .\winlogbeat.yml
Start-Service winlogbeat
Get-Service winlogbeat
Test-NetConnection logstash.lab.example -Port 5044
```

10. Find a newly generated event in Elasticsearch and match host, channel, source record ID, and timestamp. A running service or successful TCP check alone is insufficient.

## 3. Windows Server configuration

### What the report actually shows

Windows Server 2016 role selection includes **AD DS, DNS, DHCP**, management tools, and new-forest settings for `server.local` / NetBIOS `SERVER`. Later captures show Sysmon installation, Winlogbeat running, address `10.150.0.175`, and successful gateway pings. The report does **not** prove completed promotion, working DHCP scopes, or Windows 10 domain join. Another attack capture references `Team1.local`; do not silently assume it is the same configured domain.

![Windows Server addressing and gateway checks from PDF Figure 27](../assets/evidence/windows-server-connectivity.png)

### Rebuild procedure

1. Configure a stable IP on the planned Windows network and set a unique hostname before domain promotion. Ensure no competing DHCP server exists on that isolated network.
2. In Server Manager → Add Roles and Features, install AD DS, DNS, and DHCP only if they are part of the intended design.
3. Promote the server using the intended new forest/domain or existing-domain workflow. Set a private DSRM password, select supported functional levels, and review prerequisites before rebooting.
4. Verify DNS zones and AD SRV records. Configure clients to use this server for domain DNS; configure appropriate upstream DNS forwarding separately.
5. Complete DHCP authorization where required. Create an appropriate scope, exclude infrastructure addresses, reserve important hosts, and set router/DNS/domain options to the actual lab values.
6. Verify AD/DNS/DHCP services and inspect health from an elevated shell with the corresponding management tools installed:

```powershell
Get-Service NTDS,DNS,DHCPServer
Get-ADDomain
Get-DnsServerZone
Get-DhcpServerv4Scope
Resolve-DnsName -Type SRV _ldap._tcp.dc._msdcs.YOUR_DOMAIN
```

Replace `YOUR_DOMAIN` before use. A service result is only one part of the test; verify a client lease and authenticated domain operation as applicable.

7. Install/update Sysmon and configure the selected shipper as on Windows 10. Monitor DC-specific channels/audit categories only where enabled and appropriate. Verify events under the **server's** hostname independently.
8. Keep Windows Defender Firewall enabled. Permit necessary AD/management services using scoped built-in role rules and narrow custom rules. Do not open all ports to make a ping work.

**Important:** a domain controller is not automatically a router or a log relay. Prefer a separate member server for any relay role; adding routing or collectors to a DC increases attack surface.

## 4. Ubuntu / Elastic configuration

### Captured baseline

The source shows authenticated/TLS-enabled Elasticsearch, Kibana connected, Fleet Server healthy, Logstash active, and populated indices. Its output examples use superuser credentials and disabled certificate verification; do **not** copy those insecure settings.

![Logstash active service from PDF Figure 34](../assets/evidence/elastic-logstash-service.png)

### Host and Elasticsearch

1. Assign a stable lab address and DNS name. Confirm `ip -br addr`, `ip route`, DNS, time sync, disk capacity, and source reachability.
2. Install a supported, mutually compatible Elastic stack using verified packages. Preserve security auto-configuration or explicitly configure authentication and TLS.
3. In `/etc/elasticsearch/elasticsearch.yml`, choose the appropriate cluster/node names and network bind. The following is a **non-complete fragment** for a dedicated single-node lab:

```yaml
cluster.name: soc-lab
node.name: ubuntu-siem
network.host: YOUR_COLLECTOR_IP
http.port: 9200
# Retain the package's security/TLS settings; do not replace the whole file.
```

`YOUR_COLLECTOR_IP` must be replaced. Configure discovery according to the chosen supported deployment mode and existing bootstrap state; do not add single-node discovery blindly to an already bootstrapped cluster.

4. Restrict network exposure using the host firewall and network policy. Use the CA and a valid hostname for HTTPS checks. Set retention and disk watermarks appropriate to capacity.
5. Create least-privilege identities for ingestion and investigation, and keep credentials in protected secret storage. Bootstrap administrative credentials are not pipeline identities.

### Kibana and Fleet

1. Configure `/etc/kibana/kibana.yml` using the supported enrollment/service identity flow. Set `server.host` to the selected bind address, port as planned, and Elasticsearch hosts to the trusted HTTPS endpoint.
2. Configure browser-facing TLS (or a trusted reverse proxy) and persistent encryption keys as required by the installed version. Keep keys out of Git.
3. In Fleet settings, set the HTTPS Fleet Server URL and trusted CA. Enroll the Ubuntu Fleet Server using the private generated command, then enroll the Windows endpoints with their policies.
4. Set the policy's event output deliberately. Agent → Fleet/8220 is management; Agent → Elasticsearch or Logstash is data. Test both paths separately.

### Logstash listeners and output

Use the actual selected protocol. The Windows source's `udp { port => 5044 }` is incompatible with Winlogbeat's Beats output. An illustrative corrected listener is:

```text
input {
  beats {
    id => "windows_beats_tls"
    port => 5044
    ssl_enabled => true
    ssl_certificate => "/etc/logstash/certs/logstash.crt"
    ssl_key => "/etc/logstash/certs/logstash.pkcs8.key"
  }
}
```

Verify plugin settings and private-key format for your installed version. This enables server TLS; configure and test client authentication separately if required. Do not deploy this fragment without a compatible filter/output.

For FortiGate, choose a matching syslog listener, for example `udp { port => 5514 }` **only if the firewall sends to 5514** or an explicitly documented redirect exists. A raw UDP listener does not automatically parse fields or create ECS mappings. Preserve the message and parse full event time/timezone, source/destination, policy, action, device, and event type using the integration/parser appropriate to the actual format.

Configure the Elasticsearch output with a least-privilege writer, HTTPS and full CA verification. Place its password/API key in the Logstash keystore rather than a tracked config. Use separate pipelines/conditions for Windows and firewall events so they are not inadvertently written to both indices.

```bash
# Run using the packaged service identity/permissions appropriate to your install.
sudo /usr/share/logstash/bin/logstash --path.settings /etc/logstash --config.test_and_exit
sudo systemctl restart logstash
sudo systemctl status elasticsearch kibana logstash --no-pager
sudo ss -lntup
```

Ensure certificates/keys are readable only by the required service identity. Validate fresh per-source documents after changes. Index existence does not prove parsing or every host's delivery.

## 5. FortiGate configuration

### Captured baseline

Figure 42 shows FortiOS 7.2.0 policy `windows10toFTG` (ID 6): incoming `port2`, outgoing `port3`, source `WINDOWS_10`, destination `all`, service `ALL`, ACCEPT, flow-based inspection, NAT off, and default antivirus/web-filter profiles. These historical broad settings are **not** a recommended least-privilege policy.

![FortiGate policy from PDF Figure 42](../assets/evidence/fortigate-policy.png)

### Rebuild procedure

1. Label each interface by role: management, Windows segment, collector/transit, and any alternate uplink. Record IP/prefix, switch/VMnet, zone, gateway, and trusted management sources. Do not infer port-to-subnet assignments from policy names alone.
2. Add connected/static routes for nonlocal destinations and valid return routes on peers. For a collector on the same subnet, traffic may not pass through the FortiGate at all.
3. Define address objects for each endpoint, server, collector, and analyst network. Use exact hosts/subnets from the as-built plan.
4. Create narrow interface-to-interface policies for intended services. Allow endpoint ingestion, domain services, and management only where needed; use separate policies if paths differ.
5. Choose NAT based on the routing design. Internal routed lab paths generally preserve source addresses; NAT may be required for other paths but must not be used as a substitute for an understood topology.
6. Enable traffic logging on relevant policies and required security profiles. Verify profile/license functionality before claiming IPS/AV/web-filter detection.
7. Synchronize NTP and timezone, then configure syslog. This example intentionally chooses **UDP/5514** to match an unprivileged collector listener; it is **not** the exact original UDP/514 configuration:

```text
config log syslogd setting
    set status enable
    set server "YOUR_COLLECTOR_IP"
    set mode udp
    set port 5514
    set facility local7
    set format default
end
```

Replace the placeholder; confirm CLI support and logging filters in your FortiOS version. If selecting TCP/TLS instead, verify support at both ends and configure the matching listener and certificates. UDP lacks acknowledgment/replay.

8. Verify interface/route/policy selection and generate a benign logged connection. Compare FortiGate event/session details, collector packets, and the indexed document. Do not equate ping with syslog success.

```text
get system interface physical
get router info routing-table all
show log syslogd setting
execute ping YOUR_COLLECTOR_IP
```

Do not export a full configuration publicly: it can contain sensitive encrypted secrets, addressing, and management data.

## 6. How the devices connect

- **Windows 10 ↔ Windows Server:** shared Layer-2 segment allows direct IP communication if addressing and host firewalls permit it. DNS/AD connectivity needs actual domain service configuration, not simply ping.
- **Windows → Elastic:** Winlogbeat connects to Beats/TCP on Logstash; Elastic Agent uses its configured data output. Both need routes, allowed ports, and trusted certificates.
- **FortiGate → Elastic:** FortiGate sends syslog to Logstash, which parses and authenticates to Elasticsearch. FortiGate does not need unrestricted access to the Elasticsearch API.
- **Analyst → Kibana:** browser access is separate from event ingestion and can fail independently.
- **Windows 10 → Server → Elastic:** this is only a **proposed** backup path until routing or event forwarding is explicitly configured. See [backup lines](backup-lines.md) for the two different designs and their limitations.

Use the [validation runbook](validation.md) and [evidence record](../examples/evidence-record.md) for every link. Never mark a complete path healthy based only on its first hop.

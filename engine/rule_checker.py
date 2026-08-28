# -------------------------------------------------
# NETSAGE AI - NETWORK RULE CHECKER
# -------------------------------------------------


def check_interface_down(show_output):

    findings = []

    evidence = show_output.lower()

    if "administratively down" in evidence:

        findings.append({
            "issue": "Interface Administratively Down",
            "severity": "High",
            "evidence": (
                "The command output indicates that an interface "
                "is administratively down."
            ),
            "recommendation": (
                "Check the affected interface and use 'no shutdown' "
                "if appropriate."
            )
        })

    return findings


# -------------------------------------------------
# VLAN MISMATCH CHECK
# -------------------------------------------------

def check_vlan_mismatch(show_output):

    findings = []

    evidence = show_output.lower()

    if (
        "access mode vlan: 10" in evidence
        and "20 active" in evidence
    ):

        findings.append({
            "issue": "Possible VLAN Mismatch",
            "severity": "Medium",
            "evidence": (
                "The network evidence indicates interfaces "
                "associated with different VLANs."
            ),
            "recommendation": (
                "Verify VLAN assignments on the affected interfaces "
                "and trunk configuration."
            )
        })

    return findings


# -------------------------------------------------
# DHCP POOL EXHAUSTION CHECK
# -------------------------------------------------

def check_dhcp_pool_exhaustion(show_output):

    findings = []

    evidence = show_output.lower()

    if (
        "available addresses: 0" in evidence
        or "available addresses : 0" in evidence
    ):

        findings.append({
            "issue": "DHCP Pool Exhausted",
            "severity": "High",
            "evidence": (
                "The DHCP pool has zero available addresses."
            ),
            "recommendation": (
                "Expand the DHCP pool or release unused leases, then "
                "verify DHCP availability."
            )
        })

    return findings


# -------------------------------------------------
# DNS FAILURE CHECK
# -------------------------------------------------

def check_dns_failure(show_output):

    findings = []

    evidence = show_output.lower()

    dns_patterns = [
        "unknown host",
        "could not resolve",
        "dns request timed out",
        "server can't find",
        "name or service not known"
    ]

    for pattern in dns_patterns:

        if pattern in evidence:

            findings.append({
                "issue": "DNS Resolution Failure",
                "severity": "Medium",
                "evidence": (
                    "The network evidence indicates a DNS "
                    "name resolution failure."
                ),
                "recommendation": (
                    "Verify the configured DNS server and test hostname "
                    "resolution using nslookup."
                )
            })

            break

    return findings


# -------------------------------------------------
# ROUTING FAILURE CHECK
# -------------------------------------------------

def check_routing_failure(show_output):

    findings = []

    evidence = show_output.lower()

    routing_patterns = [
        "network is unreachable",
        "destination unreachable",
        "no route to host",
        "route not found"
    ]

    for pattern in routing_patterns:

        if pattern in evidence:

            findings.append({
                "issue": "Routing Failure",
                "severity": "High",
                "evidence": (
                    "The network evidence indicates that a valid "
                    "route to the destination could not be found."
                ),
                "recommendation": (
                    "Check the routing table, next-hop reachability, and "
                    "route advertisements."
                )
            })

            break

    return findings


# -------------------------------------------------
# DUPLICATE IP ADDRESS CHECK
# -------------------------------------------------

def check_duplicate_ip(show_output):

    findings = []

    evidence = show_output.lower()

    duplicate_patterns = [
        "duplicate ip address",
        "ip address conflict",
        "duplicate address detected",
        "arp conflict"
    ]

    for pattern in duplicate_patterns:

        if pattern in evidence:

            findings.append({
                "issue": "Possible Duplicate IP Address",
                "severity": "High",
                "evidence": (
                    "The network evidence indicates an IP "
                    "address conflict."
                ),
                "recommendation": (
                    "Identify the duplicate host and assign unique IP "
                    "addresses, then verify ARP entries."
                )
            })

            break

    return findings


# -------------------------------------------------
# RUN ALL NETWORK CHECKS
# -------------------------------------------------

def run_all_checks(show_output):

    if not show_output:
        return []

    all_findings = []

    all_findings.extend(
        check_interface_down(show_output)
    )

    all_findings.extend(
        check_vlan_mismatch(show_output)
    )

    all_findings.extend(
        check_dhcp_pool_exhaustion(show_output)
    )

    all_findings.extend(
        check_dns_failure(show_output)
    )

    all_findings.extend(
        check_routing_failure(show_output)
    )

    all_findings.extend(
        check_duplicate_ip(show_output)
    )

    return all_findings
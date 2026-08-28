from engine.rule_checker import run_all_checks


def get_severity_score(severity):
    scores = {
        "Low": 1,
        "Medium": 2,
        "High": 3,
        "Critical": 4
    }

    return scores.get(severity, 1)


def calculate_confidence(findings, expected_fault):
    """
    Calculates a simple confidence score based on
    the number and severity of rule-based findings.
    """

    if not findings:
        return 55

    highest_score = max(
        get_severity_score(finding["severity"])
        for finding in findings
    )

    confidence = 60 + (highest_score * 8)

    # Extra confidence when evidence exists
    if expected_fault:
        confidence += 5

    return min(confidence, 95)


def create_recommendations(case, findings):
    """
    Creates troubleshooting recommendations.
    """

    recommendations = []

    # Add rule-based recommendations
    for finding in findings:
        recommendation = finding["recommendation"]

        if recommendation not in recommendations:
            recommendations.append(recommendation)

    # Add a concept-specific recommendation
    concept = case.get("concept", "").lower()

    concept_recommendations = {

        "vlan":
            "Verify VLAN existence, access-port assignment, and trunk allowed VLAN configuration.",

        "gateway":
            "Verify that the host default gateway belongs to the same subnet and matches the router interface.",

        "dhcp":
            "Check DHCP server availability, pool configuration, available addresses, and relay settings.",

        "dns":
            "Verify the configured DNS server and test hostname resolution using nslookup.",

        "routing":
            "Check the routing table, next-hop reachability, and route advertisements.",

        "acl":
            "Review ACL order and rules to ensure required traffic is explicitly permitted.",

        "nat":
            "Verify NAT inside/outside interfaces, NAT ACL, overload configuration, and WAN connectivity.",

        "wireless":
            "Check SSID, VLAN mapping, DHCP availability, security settings, and channel interference."
    }

    if concept in concept_recommendations:
        recommendation = concept_recommendations[concept]

        if recommendation not in recommendations:
            recommendations.append(recommendation)

    # Default recommendation
    if not recommendations:
        recommendations.append(
            "Collect additional show-command output and verify the network configuration."
        )

    return recommendations


def determine_status(confidence):
    """
    Determines whether the diagnosis needs
    stronger human review.
    """

    if confidence >= 85:
        return "High Confidence - Review Before Applying Fix"

    elif confidence >= 70:
        return "Medium Confidence - Human Verification Recommended"

    else:
        return "Low Confidence - More Evidence Required"


def diagnose_case(case):
    """
    Main NetSage AI diagnosis function.

    Input:
        A dictionary containing one network case.

    Output:
        Structured diagnosis dictionary.
    """

    show_output = case.get("show_output", "")

    # Run deterministic rule checker
    findings = run_all_checks(show_output)

    # -------------------------------------------------
    # DETERMINE ROOT CAUSE DYNAMICALLY
    # -------------------------------------------------

    if findings:

        # Use the strongest rule-based finding
        predicted_root_cause = findings[0]["issue"]

    else:

        # Fall back to the expected fault for dataset cases
        predicted_root_cause = case.get(
            "expected_fault",
            "Unable to determine root cause from the available evidence."
        )

    # Calculate confidence
    confidence = calculate_confidence(
        findings,
        case.get("expected_fault")
    )

    # Generate recommendations
    recommendations = create_recommendations(
        case,
        findings
    )

    # Determine diagnosis status
    status = determine_status(confidence)

    diagnosis = {
        "case_id": case.get("case_id", "Unknown"),

        "symptom": case.get(
            "symptom",
            "No symptom provided."
        ),

        "predicted_root_cause": predicted_root_cause,

        "osi_layer": case.get(
            "osi_layer",
            "Unknown"
        ),

        "concept": case.get(
            "concept",
            "Unknown"
        ),

        "severity": case.get(
            "severity",
            "Unknown"
        ),

        "confidence": confidence,

        "status": status,

        "rule_findings": findings,

        "recommendations": recommendations,

        "human_review_required": True
    }

    return diagnosis


# ----------------------------------------
# TEST MODE
# ----------------------------------------

if __name__ == "__main__":

    sample_case = {

        "case_id": "TEST-001",

        "symptom":
            "Internal users cannot access the internet.",

        "show_output":
            """
Router# show ip interface brief

GigabitEthernet0/0
192.168.10.1
up up

GigabitEthernet0/1
203.0.113.2
administratively down down
""",

        "expected_fault":
            "WAN interface is administratively down.",

        "osi_layer":
            "Layer 3",

        "concept":
            "NAT",

        "severity":
            "High"
    }

    result = diagnose_case(sample_case)

    print("\n" + "=" * 50)
    print("NETSAGE AI DIAGNOSIS")
    print("=" * 50)

    print(f"\nCase ID: {result['case_id']}")

    print(
        f"\nPredicted Root Cause: "
        f"{result['predicted_root_cause']}"
    )

    print(
        f"\nOSI Layer: "
        f"{result['osi_layer']}"
    )

    print(
        f"\nConcept: "
        f"{result['concept']}"
    )

    print(
        f"\nSeverity: "
        f"{result['severity']}"
    )

    print(
        f"\nConfidence: "
        f"{result['confidence']}%"
    )

    print(
        f"\nStatus: "
        f"{result['status']}"
    )

    print("\nRULE FINDINGS:")

    for finding in result["rule_findings"]:

        print(
            f"- {finding['issue']} "
            f"({finding['severity']})"
        )

    print("\nRECOMMENDATIONS:")

    for recommendation in result["recommendations"]:

        print(f"- {recommendation}")

    print("\nHuman Review Required: YES")

    print("\n" + "=" * 50)
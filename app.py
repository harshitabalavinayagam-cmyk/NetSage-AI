import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib.enums import TA_CENTER

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)


from engine.diagnosis_engine import diagnose_case
# -------------------------------------------------
# EVIDENCE QUALITY ANALYZER
# -------------------------------------------------

def analyze_evidence(case, diagnosis):

    score = 0
    reasons = []

    # Check symptom
    if case.get("symptom"):
        score += 20
        reasons.append("Symptom information provided")

    # Check topology information
    if case.get("topology_note"):
        score += 20
        reasons.append("Topology context provided")

    # Check show-command evidence
    show_output = case.get("show_output", "")

    if show_output and len(show_output.strip()) > 30:
        score += 30
        reasons.append("Detailed network evidence provided")

    # Check deterministic findings
    findings = diagnosis.get("rule_findings", [])

    if findings:
        score += 20
        reasons.append(
            f"{len(findings)} rule-based finding(s) detected"
        )

    # Check expected network concept
    if case.get("concept"):
        score += 10
        reasons.append(
            f"Network concept identified: {case['concept']}"
        )

    return min(score, 100), reasons

 # -------------------------------------------------
# INTELLIGENT EVIDENCE QUALITY ANALYZER
# -------------------------------------------------

def analyze_evidence_quality(case, diagnosis):

    issues = []

    if diagnosis is None:
        diagnosis = {}

    # Get information from the selected/custom case
    symptom = str(case.get("symptom", "")).strip()
    topology = str(case.get("topology_note", "")).strip()
    evidence = str(case.get("show_output", "")).strip()

    # Get findings from the diagnosis engine
    findings = diagnosis.get("rule_findings", [])

    # ---------------------------------------------
    # 1. CHECK FOR MISSING INFORMATION
    # ---------------------------------------------

    if not symptom:
        issues.append("⚠️ Network symptom is missing.")

    if not topology:
        issues.append("⚠️ Network topology information is missing.")

    if not evidence:
        issues.append("⚠️ Network command output/evidence is missing.")

    # ---------------------------------------------
    # 2. CHECK IF EVIDENCE IS TOO SHORT
    # ---------------------------------------------

    if evidence and len(evidence) < 30:
        issues.append(
            "⚠️ Evidence is very limited. More command output may improve the diagnosis."
        )

    # ---------------------------------------------
    # 3. CHECK FOR MULTIPLE POSSIBLE ISSUES
    # ---------------------------------------------

    if len(findings) > 1:
        issues.append(
            f"🔎 Multiple possible issues detected ({len(findings)} findings). "
            "Human verification is recommended."
        )

    # ---------------------------------------------
    # 4. CHECK IF NO RULE MATCHED
    # ---------------------------------------------

    if evidence and not findings:
        issues.append(
            "🔎 Evidence was provided, but no known diagnostic rule matched it."
        )

    # ---------------------------------------------
    # 5. CALCULATE EVIDENCE QUALITY SCORE
    # ---------------------------------------------

    quality_score = 100

    for issue in issues:

        if "symptom is missing" in issue:
            quality_score -= 20

        elif "topology information is missing" in issue:
            quality_score -= 15

        elif "command output/evidence is missing" in issue:
            quality_score -= 30

        elif "very limited" in issue:
            quality_score -= 15

        elif "Multiple possible issues" in issue:
            quality_score -= 10

        elif "no known diagnostic rule" in issue:
            quality_score -= 10

    quality_score = max(0, quality_score)

    return quality_score, issues   

# -------------------------------------------------
# DIAGNOSIS RISK LEVEL CALCULATOR
# -------------------------------------------------

# -------------------------------------------------
# DIAGNOSIS RISK LEVEL CALCULATOR
# -------------------------------------------------

def calculate_risk_level(case, diagnosis, quality_score):

    # ---------------------------------------------
    # GET CONFIDENCE
    # ---------------------------------------------

    confidence = diagnosis.get("confidence", 0)

    # ---------------------------------------------
    # GET SEVERITY
    # First try detected finding
    # If not available, use user-selected severity
    # ---------------------------------------------

    findings = diagnosis.get("findings", [])

    severity = case.get("severity", "Low")

    if findings:

        finding_severity = findings[0].get("severity")

        if finding_severity:
            severity = finding_severity

    # Convert to lowercase for safe comparison
    severity = str(severity).strip().lower()

    # ---------------------------------------------
    # CRITICAL RISK
    # ---------------------------------------------

    if severity == "critical":

        return (
            "🔴 Critical Risk – Immediate Human Review Required",
            "critical"
        )

    # ---------------------------------------------
    # HIGH RISK
    # ---------------------------------------------

    elif severity == "high":

        if confidence < 70 or quality_score < 70:

            return (
                "🟠 High Risk – Verify Before Making Changes",
                "high"
            )

        else:

            return (
                "🟠 High Risk – Strong Evidence Detected",
                "high"
            )

    # ---------------------------------------------
    # MEDIUM / MODERATE RISK
    # ---------------------------------------------

    elif severity in ["medium", "moderate"]:

        if confidence < 50 or quality_score < 60:

            return (
                "🟡 Moderate Risk – Human Verification Recommended",
                "medium"
            )

        else:

            return (
                "🟡 Moderate Risk",
                "medium"
            )

    # ---------------------------------------------
    # LOW RISK WITH POOR EVIDENCE
    # ---------------------------------------------

    elif confidence < 50 or quality_score < 50:

        return (
            "🟡 Moderate Risk – Insufficient Diagnostic Evidence",
            "medium"
        )

    # ---------------------------------------------
    # LOW RISK
    # ---------------------------------------------

    else:

        return (
            "🟢 Low Risk",
            "low"
        )


    # -------------------------------------------------
# SMART TROUBLESHOOTING PLAYBOOK GENERATOR
# -------------------------------------------------

def generate_playbook(case, diagnosis):

    root_cause = str(
        diagnosis.get(
            "predicted_root_cause",
            ""
        )
    ).lower()

    concept = str(
        case.get(
            "concept",
            ""
        )
    ).lower()

    findings = diagnosis.get(
        "rule_findings",
        []
    )

    # ---------------------------------------------
    # DHCP PLAYBOOK
    # ---------------------------------------------

    if "dhcp" in root_cause or concept == "dhcp":

        return [
            {
                "step": "Check DHCP Pool Status",
                "action": (
                    "Verify whether the DHCP pool has "
                    "available IP addresses."
                ),
                "command": "show ip dhcp pool",
                "expected": (
                    "Available addresses should be greater than 0."
                )
            },
            {
                "step": "Check DHCP Bindings",
                "action": (
                    "Review active DHCP leases and identify "
                    "unused or stale bindings."
                ),
                "command": "show ip dhcp binding",
                "expected": (
                    "Bindings should correspond to valid active devices."
                )
            },
            {
                "step": "Verify DHCP Configuration",
                "action": (
                    "Check the configured network, excluded addresses, "
                    "default gateway, and DNS settings."
                ),
                "command": "show running-config | section dhcp",
                "expected": (
                    "DHCP pool settings should match the intended network."
                )
            },
            {
                "step": "Apply Corrective Action",
                "action": (
                    "Increase the DHCP scope or remove invalid leases "
                    "only after verifying the impact."
                ),
                "command": "Manual configuration review",
                "expected": (
                    "Clients should successfully receive valid IP addresses."
                )
            }
        ]

    # ---------------------------------------------
    # VLAN PLAYBOOK
    # ---------------------------------------------

    elif "vlan" in root_cause or concept == "vlan":

        return [
            {
                "step": "Check VLAN Configuration",
                "action": (
                    "Verify that the required VLAN exists "
                    "and is active."
                ),
                "command": "show vlan brief",
                "expected": (
                    "Required VLAN should exist and required ports "
                    "should be assigned correctly."
                )
            },
            {
                "step": "Check Switchport Configuration",
                "action": (
                    "Verify the VLAN assignment and port mode."
                ),
                "command": "show interfaces switchport",
                "expected": (
                    "Access or trunk mode should match the network design."
                )
            },
            {
                "step": "Check Trunk Links",
                "action": (
                    "Verify that the required VLAN is allowed "
                    "across trunk connections."
                ),
                "command": "show interfaces trunk",
                "expected": (
                    "The required VLAN should be allowed and active."
                )
            },
            {
                "step": "Test Connectivity",
                "action": (
                    "Test communication between devices "
                    "after verifying VLAN configuration."
                ),
                "command": "ping <destination-ip>",
                "expected": (
                    "Packets should reach the destination successfully."
                )
            }
        ]

    # ---------------------------------------------
    # DNS PLAYBOOK
    # ---------------------------------------------

    elif "dns" in root_cause or concept == "dns":

        return [
            {
                "step": "Check DNS Server Configuration",
                "action": (
                    "Verify the configured DNS server addresses."
                ),
                "command": "ipconfig /all",
                "expected": (
                    "Configured DNS servers should be reachable "
                    "and valid."
                )
            },
            {
                "step": "Test DNS Resolution",
                "action": (
                    "Test whether domain names can be resolved."
                ),
                "command": "nslookup google.com",
                "expected": (
                    "A valid DNS response should be returned."
                )
            },
            {
                "step": "Test DNS Server Reachability",
                "action": (
                    "Verify network connectivity to the DNS server."
                ),
                "command": "ping <dns-server-ip>",
                "expected": (
                    "The DNS server should be reachable."
                )
            },
            {
                "step": "Verify DNS Service",
                "action": (
                    "Check whether the DNS service is running "
                    "and responding to queries."
                ),
                "command": "Check DNS server/service logs",
                "expected": (
                    "DNS service should be operational."
                )
            }
        ]

    # ---------------------------------------------
    # ROUTING PLAYBOOK
    # ---------------------------------------------

    elif "routing" in root_cause or "route" in root_cause or concept == "routing":

        return [
            {
                "step": "Check Routing Table",
                "action": (
                    "Verify whether a route exists for the destination network."
                ),
                "command": "show ip route",
                "expected": (
                    "A valid route should exist for the destination."
                )
            },
            {
                "step": "Check Interface Status",
                "action": (
                    "Verify that the relevant router interfaces are operational."
                ),
                "command": "show ip interface brief",
                "expected": (
                    "Required interfaces should show up/up."
                )
            },
            {
                "step": "Test Next-Hop Reachability",
                "action": (
                    "Verify connectivity to the next-hop router."
                ),
                "command": "ping <next-hop-ip>",
                "expected": (
                    "The next-hop router should respond."
                )
            },
            {
                "step": "Trace the Path",
                "action": (
                    "Identify where communication fails along the route."
                ),
                "command": "traceroute <destination-ip>",
                "expected": (
                    "The route should progress toward the destination."
                )
            }
        ]

    # ---------------------------------------------
    # WIFI PLAYBOOK
    # ---------------------------------------------

    elif "wifi" in root_cause or "wireless" in root_cause or concept == "wifi":

        return [
            {
                "step": "Check Wireless Connection",
                "action": (
                    "Verify that the device is connected to the correct SSID."
                ),
                "command": "netsh wlan show interfaces",
                "expected": (
                    "The device should show a valid wireless connection."
                )
            },
            {
                "step": "Check IP Configuration",
                "action": (
                    "Verify that the wireless client received valid IP settings."
                ),
                "command": "ipconfig /all",
                "expected": (
                    "Client should have valid IP, gateway, and DNS settings."
                )
            },
            {
                "step": "Check Signal Quality",
                "action": (
                    "Verify signal strength and connection quality."
                ),
                "command": "netsh wlan show interfaces",
                "expected": (
                    "Signal strength should be sufficient for stable communication."
                )
            },
            {
                "step": "Test Network Access",
                "action": (
                    "Test gateway and internet connectivity."
                ),
                "command": "ping <gateway-ip>",
                "expected": (
                    "Gateway should respond successfully."
                )
            }
        ]

    # ---------------------------------------------
    # FIREWALL PLAYBOOK
    # ---------------------------------------------

    elif "firewall" in root_cause or concept == "firewall":

        return [
            {
                "step": "Identify Blocked Traffic",
                "action": (
                    "Check firewall rules relevant to the affected traffic."
                ),
                "command": "Review firewall rules/logs",
                "expected": (
                    "Required traffic should not be blocked."
                )
            },
            {
                "step": "Check Rule Order",
                "action": (
                    "Verify whether a higher-priority rule overrides the intended rule."
                ),
                "command": "Review firewall policy order",
                "expected": (
                    "Allow rules should take precedence where appropriate."
                )
            },
            {
                "step": "Verify Ports and Protocols",
                "action": (
                    "Confirm that the required protocol and ports are permitted."
                ),
                "command": "Check ACL / security policy",
                "expected": (
                    "Required ports and protocols should be allowed."
                )
            },
            {
                "step": "Retest Connectivity",
                "action": (
                    "Test communication after verified policy changes."
                ),
                "command": "Test application or ping",
                "expected": (
                    "Required communication should succeed."
                )
            }
        ]

    # ---------------------------------------------
    # GENERIC PLAYBOOK
    # ---------------------------------------------

    else:

        playbook = []

        # Use rule findings if available

        for index, finding in enumerate(
            findings,
            start=1
        ):

            playbook.append(
                {
                    "step": f"Investigate Finding {index}",
                    "action": finding.get(
                        "recommendation",
                        "Investigate the detected issue."
                    ),
                    "command": "Review related network configuration",
                    "expected": (
                        "Configuration should match the intended network design."
                    )
                }
            )

        # If no findings exist

        if not playbook:

            playbook = [
                {
                    "step": "Collect Additional Evidence",
                    "action": (
                        "Gather interface status, IP configuration, "
                        "routing information, and relevant logs."
                    ),
                    "command": "ipconfig /all / show ip interface brief",
                    "expected": (
                        "Enough evidence should be collected "
                        "to isolate the fault."
                    )
                },
                {
                    "step": "Verify Physical and Logical Connectivity",
                    "action": (
                        "Check cable/link status and network configuration."
                    ),
                    "command": "ping <gateway-ip>",
                    "expected": (
                        "The gateway should respond if connectivity is healthy."
                    )
                },
                {
                    "step": "Run Additional Diagnostics",
                    "action": (
                        "Use protocol-specific commands based on "
                        "the affected network service."
                    ),
                    "command": "Collect relevant show commands",
                    "expected": (
                        "Additional evidence should narrow down the root cause."
                    )
                }
            ]

        return playbook

    # -------------------------------------------------
# SAVE DIAGNOSIS HISTORY
# -------------------------------------------------

def save_diagnosis_history(
    case,
    diagnosis,
    quality_score,
    risk_message
):

    history_file = "data/diagnosis_history.csv"

    history_data = {
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "case_id": case.get(
            "case_id",
            "UNKNOWN"
        ),

        "concept": case.get(
            "concept",
            "Unknown"
        ),

        "severity": case.get(
            "severity",
            "Unknown"
        ),

        "predicted_root_cause": diagnosis.get(
            "predicted_root_cause",
            "Unknown"
        ),

        "confidence": diagnosis.get(
            "confidence",
            0
        ),

        "evidence_quality": quality_score,

        "risk_level": risk_message
    }

    history_df = pd.DataFrame(
        [history_data]
    )

    try:

        existing_history = pd.read_csv(
            history_file
        )

        updated_history = pd.concat(
            [
                existing_history,
                history_df
            ],
            ignore_index=True
        )

    except (
        FileNotFoundError,
        pd.errors.EmptyDataError
    ):

        updated_history = history_df

    updated_history.to_csv(
        history_file,
        index=False
    )

    # -------------------------------------------------
# LOAD DIAGNOSIS HISTORY
# -------------------------------------------------

def load_diagnosis_history():

    history_file = "data/diagnosis_history.csv"

    try:

        history_df = pd.read_csv(
            history_file
        )

        return history_df

    except (
        FileNotFoundError,
        pd.errors.EmptyDataError
    ):

        return pd.DataFrame()

    # -------------------------------------------------
# SIMILAR PAST CASE FINDER
# -------------------------------------------------

def find_similar_cases(case, diagnosis):

    history_df = load_diagnosis_history()

    # If no previous history exists
    if history_df.empty:

        return pd.DataFrame()

    # ---------------------------------------------
    # GET CURRENT CASE INFORMATION
    # ---------------------------------------------

    current_concept = str(
        case.get("concept", "")
    ).strip().lower()

    current_root_cause = str(
        diagnosis.get(
            "predicted_root_cause",
            ""
        )
    ).strip().lower()

    # ---------------------------------------------
    # CREATE COMPARISON COLUMNS
    # ---------------------------------------------

    history_df["concept_lower"] = (
        history_df["concept"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    history_df["root_cause_lower"] = (
        history_df["predicted_root_cause"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # ---------------------------------------------
    # FIND SIMILAR CASES
    # ---------------------------------------------

    similar_cases = history_df[
        (
            history_df["concept_lower"]
            == current_concept
        )
        |
        (
            history_df["root_cause_lower"]
            == current_root_cause
        )
    ]

    # Remove helper columns before returning

    similar_cases = similar_cases.drop(
        columns=[
            "concept_lower",
            "root_cause_lower"
        ]
    )

    # ---------------------------------------------
    # RETURN ONLY LAST 5 SIMILAR CASES
    # ---------------------------------------------

    return similar_cases.tail(5)
# -------------------------------------------------
# SAVE HUMAN REVIEW
# -------------------------------------------------

def save_review(case, diagnosis, review, comments):

    review_file = "data/review_log.csv"

    review_data = {
        "case_id": case.get("case_id", ""),
        "predicted_root_cause": diagnosis.get(
            "predicted_root_cause", ""
        ),
        "confidence": diagnosis.get(
            "confidence", 0
        ),
        "review": review,
        "comments": comments
    }

    review_df = pd.DataFrame([review_data])

    try:

        existing_df = pd.read_csv(review_file)

        updated_df = pd.concat(
            [existing_df, review_df],
            ignore_index=True
        )

    except (FileNotFoundError, pd.errors.EmptyDataError):

        updated_df = review_df

    updated_df.to_csv(
        review_file,
        index=False
    )
# -------------------------------------------------
# REVIEW ANALYTICS
# -------------------------------------------------

def get_review_analytics():

    review_file = "data/review_log.csv"

    try:

        review_df = pd.read_csv(review_file)

    except FileNotFoundError:

        return None

    if review_df.empty:

        return None

    total_reviews = len(review_df)

    correct_reviews = len(
        review_df[
            review_df["review"] == "✅ Correct"
        ]
    )

    incorrect_reviews = len(
        review_df[
            review_df["review"] == "❌ Incorrect"
        ]
    )

    investigation_reviews = len(
        review_df[
            review_df["review"] == "🔎 Needs Investigation"
        ]
    )

    accuracy = (
        correct_reviews / total_reviews
    ) * 100

    return {
        "data": review_df,
        "total_reviews": total_reviews,
        "correct_reviews": correct_reviews,
        "incorrect_reviews": incorrect_reviews,
        "investigation_reviews": investigation_reviews,
        "accuracy": round(accuracy, 1)
    }
# -------------------------------------------------
# PDF INCIDENT REPORT GENERATOR
# -------------------------------------------------

def generate_incident_report(
    case,
    diagnosis,
    quality_score,
    risk_message,
    playbook,
    similar_cases
):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    elements = []

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        spaceBefore=15,
        spaceAfter=10
    )

    normal_style = styles["BodyText"]

    # ---------------------------------------------
    # REPORT TITLE
    # ---------------------------------------------

    elements.append(
        Paragraph(
            "NetSage AI – Network Incident Report",
            title_style
        )
    )

    elements.append(
        Paragraph(
            "Evidence-First Network Troubleshooting Copilot",
            normal_style
        )
    )

    elements.append(
        Spacer(1, 15)
    )

    report_time = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    elements.append(
        Paragraph(
            f"<b>Generated:</b> {report_time}",
            normal_style
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    # ---------------------------------------------
    # CASE INFORMATION
    # ---------------------------------------------

    elements.append(
        Paragraph(
            "1. Case Information",
            heading_style
        )
    )

    case_data = [
        ["Case ID", str(case.get("case_id", "Unknown"))],
        ["Network Concept", str(case.get("concept", "Unknown"))],
        ["OSI Layer", str(case.get("osi_layer", "Unknown"))],
        ["Severity", str(case.get("severity", "Unknown"))]
    ]

    case_table = Table(
        case_data,
        colWidths=[150, 330]
    )

    case_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 8)
        ])
    )

    elements.append(case_table)

    elements.append(
        Spacer(1, 15)
    )

    # ---------------------------------------------
    # NETWORK SYMPTOM
    # ---------------------------------------------

    elements.append(
        Paragraph(
            "2. Reported Network Symptom",
            heading_style
        )
    )

    symptom = str(
        case.get("symptom", "No symptom provided")
    )

    elements.append(
        Paragraph(
            symptom.replace("\n", "<br/>"),
            normal_style
        )
    )

    # ---------------------------------------------
    # DIAGNOSIS
    # ---------------------------------------------

    elements.append(
        Paragraph(
            "3. AI-Assisted Diagnosis",
            heading_style
        )
    )

    diagnosis_data = [
        [
            "Predicted Root Cause",
            str(
                diagnosis.get(
                    "predicted_root_cause",
                    "Unknown"
                )
            )
        ],
        [
            "Confidence",
            f"{diagnosis.get('confidence', 0)}%"
        ],
        [
            "Evidence Quality",
            f"{quality_score}%"
        ],
        [
            "Risk Assessment",
            str(risk_message)
        ]
    ]

    diagnosis_table = Table(
        diagnosis_data,
        colWidths=[180, 300]
    )

    diagnosis_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 8)
        ])
    )

    elements.append(diagnosis_table)

    elements.append(
        Spacer(1, 15)
    )

    # ---------------------------------------------
    # NETWORK EVIDENCE
    # ---------------------------------------------

    elements.append(
        Paragraph(
            "4. Network Evidence",
            heading_style
        )
    )

    evidence = str(
        case.get(
            "show_output",
            "No evidence provided"
        )
    )

    evidence_text = evidence.replace(
        "&",
        "&amp;"
    ).replace(
        "<",
        "&lt;"
    ).replace(
        ">",
        "&gt;"
    ).replace(
        "\n",
        "<br/>"
    )

    elements.append(
        Paragraph(
            evidence_text,
            normal_style
        )
    )

    elements.append(
        Spacer(1, 15)
    )

    # ---------------------------------------------
    # TROUBLESHOOTING PLAYBOOK
    # ---------------------------------------------

    elements.append(
        Paragraph(
            "5. Smart Troubleshooting Playbook",
            heading_style
        )
    )

    for index, item in enumerate(
        playbook,
        start=1
    ):

        elements.append(
            Paragraph(
                f"<b>Step {index}: {item['step']}</b>",
                normal_style
            )
        )

        elements.append(
            Paragraph(
                f"<b>Action:</b> {item['action']}",
                normal_style
            )
        )

        elements.append(
            Paragraph(
                f"<b>Command / Check:</b> "
                f"{item['command']}",
                normal_style
            )
        )

        elements.append(
            Paragraph(
                f"<b>Expected Result:</b> "
                f"{item['expected']}",
                normal_style
            )
        )

        elements.append(
            Spacer(1, 10)
        )

    # ---------------------------------------------
    # HISTORICAL INSIGHT
    # ---------------------------------------------

    elements.append(
        Paragraph(
            "6. Historical Case Insight",
            heading_style
        )
    )

    similar_count = len(similar_cases)

    elements.append(
        Paragraph(
            f"NetSage found <b>{similar_count}</b> "
            f"similar past case(s) in the diagnosis history.",
            normal_style
        )
    )

    # ---------------------------------------------
    # RESPONSIBLE AI
    # ---------------------------------------------

    elements.append(
        Spacer(1, 20)
    )

    elements.append(
        Paragraph(
            "7. Responsible AI Notice",
            heading_style
        )
    )

    elements.append(
        Paragraph(
            "This report provides an AI-assisted troubleshooting "
            "recommendation. It does not automatically modify network "
            "configurations. A qualified network administrator should "
            "verify all evidence before applying configuration changes.",
            normal_style
        )
    )

    # ---------------------------------------------
    # BUILD PDF
    # ---------------------------------------------

    document.build(elements)

    buffer.seek(0)

    return buffer

# -------------------------------------------------
# SYSTEM STATISTICS
# -------------------------------------------------

def get_system_statistics():

    # Total dataset cases
    total_cases = len(df)

    # Diagnosis history count
    history_df = load_diagnosis_history()

    total_diagnoses = len(history_df)

    # Human review accuracy
    analytics = get_review_analytics()

    if analytics is None:

        review_accuracy = 0

    else:

        review_accuracy = analytics["accuracy"]

    return {
        "total_cases": total_cases,
        "total_diagnoses": total_diagnoses,
        "review_accuracy": review_accuracy
    }



# -------------------------------------------------
# NETWORK HEALTH SCORE CALCULATOR
# -------------------------------------------------

def calculate_network_health(
    diagnosis,
    quality_score,
    risk_level
):

    # Start with a perfect score

    health_score = 100

    reasons = []

    # ---------------------------------------------
    # CHECK SEVERITY
    # ---------------------------------------------

    severity = str(
        diagnosis.get(
            "severity",
            "Low"
        )
    ).strip().lower()

    if severity == "critical":

        health_score -= 50

        reasons.append(
            "🔴 Critical network issue detected"
        )

    elif severity == "high":

        health_score -= 30

        reasons.append(
            "🟠 High severity issue detected"
        )

    elif severity in ["medium", "moderate"]:

        health_score -= 15

        reasons.append(
            "🟡 Moderate network issue detected"
        )

    # ---------------------------------------------
    # CHECK RISK LEVEL
    # ---------------------------------------------

    if risk_level == "critical":

        health_score -= 20

        reasons.append(
            "🔴 Critical diagnosis risk"
        )

    elif risk_level == "high":

        health_score -= 15

        reasons.append(
            "🟠 High diagnosis risk"
        )

    elif risk_level == "medium":

        health_score -= 8

        reasons.append(
            "🟡 Moderate diagnosis risk"
        )

    # ---------------------------------------------
    # CHECK EVIDENCE QUALITY
    # ---------------------------------------------

    if quality_score < 50:

        health_score -= 15

        reasons.append(
            "🔎 Insufficient network evidence"
        )

    elif quality_score < 70:

        health_score -= 8

        reasons.append(
            "🔎 Network evidence needs improvement"
        )

    # ---------------------------------------------
    # CHECK NUMBER OF FINDINGS
    # ---------------------------------------------

    findings = diagnosis.get(
        "rule_findings",
        []
    )

    if len(findings) >= 3:

        health_score -= 15

        reasons.append(
            f"⚠️ Multiple issues detected ({len(findings)})"
        )

    elif len(findings) == 2:

        health_score -= 10

        reasons.append(
            "⚠️ Two network issues detected"
        )

    # Keep score between 0 and 100

    health_score = max(
        0,
        min(health_score, 100)
    )

    return health_score, reasons

    # -------------------------------------------------
# QUICK DEMO CASES
# -------------------------------------------------

def get_demo_cases():

    return {

        "🟦 VLAN Mismatch": {
            "concept": "VLAN",
            "osi_layer": "Layer 2",
            "severity": "Medium",
            "symptom": (
                "PC1 cannot communicate with PC2 "
                "even though both devices are connected "
                "to the same switch."
            ),
            "topology_note": (
                "PC1 is connected to Switch1 on Fa0/5. "
                "PC2 is connected to Switch1 on Fa0/6."
            ),
            "show_output": (
                "Switch# show interfaces fa0/5 switchport\n"
                "Access Mode VLAN: 10\n\n"
                "Switch# show interfaces fa0/6 switchport\n"
                "Access Mode VLAN: 20\n\n"
                "Switch# show vlan brief\n"
                "10 active Fa0/5\n"
                "20 active Fa0/6"
            )
        },

        "🟩 DHCP Pool Exhaustion": {
            "concept": "DHCP",
            "osi_layer": "Layer 3",
            "severity": "High",
            "symptom": (
                "Users cannot obtain IP addresses "
                "automatically."
            ),
            "topology_note": (
                "Multiple PCs connect through Switch1 "
                "to Router1, which provides DHCP services."
            ),
            "show_output": (
                "Router# show ip dhcp pool\n\n"
                "Pool OFFICE\n"
                "Available addresses: 0\n"
                "Leased addresses: 254"
            )
        },

        "🟨 DNS Failure": {
            "concept": "DNS",
            "osi_layer": "Layer 7",
            "severity": "Medium",
            "symptom": (
                "Users can access websites using IP addresses "
                "but domain names are not resolving."
            ),
            "topology_note": (
                "Clients connect through Router1 to the internet "
                "and use an internal DNS server."
            ),
            "show_output": (
                "PC> nslookup example.com\n"
                "DNS request timed out.\n\n"
                "PC> ping 8.8.8.8\n"
                "Reply received"
            )
        },

        "🟥 Interface Down": {
            "concept": "Switching",
            "osi_layer": "Layer 1",
            "severity": "High",
            "symptom": (
                "A connected device cannot communicate "
                "with the network."
            ),
            "topology_note": (
                "PC1 is connected to Switch1 on interface Fa0/10."
            ),
            "show_output": (
                "Switch# show interfaces status\n\n"
                "Port      Status       VLAN\n"
                "Fa0/10    notconnect   10"
            )
        }
    }
# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------

st.set_page_config(
    page_title="NetSage AI",
    page_icon="🌐",
    layout="wide"
)


# -------------------------------------------------
# LOAD DATASET
# -------------------------------------------------

@st.cache_data
def load_cases():
    return pd.read_csv("data/cases.csv")


df = load_cases()


# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.title("🌐 NetSage AI")

st.subheader(
    "Evidence-First Network Troubleshooting Copilot"
)

st.caption(
    "AI-assisted diagnosis with deterministic rule checks and human review."
)

# -------------------------------------------------
# SYSTEM DASHBOARD
# -------------------------------------------------

system_stats = get_system_statistics()

st.markdown("### 📊 NetSage System Dashboard")

dashboard_col1, dashboard_col2, dashboard_col3, dashboard_col4 = st.columns(4)


with dashboard_col1:

    st.metric(
        "🟢 System Status",
        "Online"
    )


with dashboard_col2:

    st.metric(
        "📂 Dataset Cases",
        system_stats["total_cases"]
    )


with dashboard_col3:

    st.metric(
        "🧠 Diagnoses Run",
        system_stats["total_diagnoses"]
    )


with dashboard_col4:

    st.metric(
        "🎯 Verified Accuracy",
        f"{system_stats['review_accuracy']}%"
    )

st.divider()


# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.title("⚙️ NetSage Controls")

concepts = ["All"] + sorted(
    df["concept"].dropna().unique().tolist()
)

selected_concept = st.sidebar.selectbox(
    "Filter by Network Concept",
    concepts
)


if selected_concept == "All":

    filtered_df = df

else:

    filtered_df = df[
        df["concept"] == selected_concept
    ]


# -------------------------------------------------
# CASE SELECTION
# -------------------------------------------------

case_mode = st.radio(
    "Choose Analysis Mode",
    [
        "📂 Existing Dataset Case",
        "✨ Analyze Custom Case",
        "⚡ Quick Demo Case"
    ],
    horizontal=True
)


# -------------------------------------------------
# EXISTING DATASET CASE
# -------------------------------------------------

if case_mode == "📂 Existing Dataset Case":

    case_options = filtered_df["case_id"].tolist()

    selected_case_id = st.selectbox(
        "🔎 Select a Network Troubleshooting Case",
        case_options
    )

    selected_case_row = filtered_df[
        filtered_df["case_id"] == selected_case_id
    ].iloc[0]

    case = selected_case_row.to_dict()


# -------------------------------------------------
# CUSTOM NETWORK CASE
# -------------------------------------------------

elif case_mode == "✨ Analyze Custom Case":

    st.info(
        "✨ Enter your own network issue and let NetSage AI "
        "analyze the available evidence."
    )

    custom_concept = st.selectbox(
        "🌐 Network Concept",
        [
            "VLAN",
            "DHCP",
            "DNS",
            "Routing",
            "Switching",
            "IP Addressing",
            "WiFi",
            "Firewall",
            "Other"
        ]
    )

    custom_os_layer = st.selectbox(
        "📡 OSI Layer",
        [
            "Layer 1",
            "Layer 2",
            "Layer 3",
            "Layer 4",
            "Layer 7",
            "Unknown"
        ]
    )

    custom_severity = st.selectbox(
        "⚠️ Severity",
        [
            "Low",
            "Medium",
            "High",
            "Critical"
        ]
    )

    custom_symptom = st.text_area(
        "🚨 Describe the Network Symptom",
        placeholder=(
            "Example: PC1 cannot communicate with PC2 "
            "even though both devices are connected to the same switch."
        )
    )

    custom_topology = st.text_area(
        "🗺️ Describe the Network Topology",
        placeholder=(
            "Example: PC1 is connected to Switch1 on Fa0/5 "
            "and PC2 is connected to Switch1 on Fa0/6."
        )
    )

    custom_evidence = st.text_area(
        "🖥️ Paste Network Evidence / Command Output",
        height=200,
        placeholder=(
            "Example:\n\n"
            "Switch# show interfaces fa0/5 switchport\n"
            "Administrative Mode: static access\n"
            "Access Mode VLAN: 10\n\n"
            "Switch# show vlan brief\n"
            "10 active Fa0/5\n"
            "20 active Fa0/6"
        )
    )


    # Create custom case dictionary

    case = {
    "case_id": "CUSTOM-CASE",
    "concept": custom_concept,
    "osi_layer": custom_os_layer,
    "severity": custom_severity,
    "symptom": custom_symptom,

    "topology_note": custom_topology,

    "show_output": custom_evidence,

    "expected_fault": "Custom diagnosis based on the provided network evidence."
}

    # -------------------------------------------------
# QUICK DEMO CASE
# -------------------------------------------------

elif case_mode == "⚡ Quick Demo Case":

    st.info(
        "⚡ Select a ready-made network issue "
        "for a fast demonstration of NetSage AI."
    )

    demo_cases = get_demo_cases()

    selected_demo = st.selectbox(
        "Select a Demo Scenario",
        list(demo_cases.keys())
    )

    selected_demo_case = demo_cases[
        selected_demo
    ]

    case = {
        "case_id": "DEMO-CASE",

        "concept": selected_demo_case[
            "concept"
        ],

        "osi_layer": selected_demo_case[
            "osi_layer"
        ],

        "severity": selected_demo_case[
            "severity"
        ],

        "symptom": selected_demo_case[
            "symptom"
        ],

        "topology_note": selected_demo_case[
            "topology_note"
        ],

        "show_output": selected_demo_case[
            "show_output"
        ],

        "expected_fault": (
            "Demo case for NetSage AI "
            "troubleshooting demonstration."
        )
    }
# Keep dataset and custom cases compatible with the shared diagnosis flow.
case["topology_note"] = case.get(
    "topology_note",
    case.get("topology_context", "")
)
case["show_output"] = case.get(
    "show_output",
    case.get("network_evidence", "")
)

# -------------------------------------------------
# SESSION STATE INIT + CASE CHANGE DETECTION
# -------------------------------------------------

if "diagnosis" not in st.session_state:
    st.session_state.diagnosis = None

if "last_case_id" not in st.session_state:
    st.session_state.last_case_id = None

current_case_signature = (
    str(case_mode)
    + "|"
    + str(case.get("case_id", ""))
    + "|"
    + str(case.get("concept", ""))
    + "|"
    + str(case.get("symptom", ""))
    + "|"
    + str(case.get("show_output", ""))
)
if (
    st.session_state.last_case_id is not None
    and st.session_state.last_case_id
    != current_case_signature
):

    st.session_state.diagnosis = None

st.session_state.last_case_id = current_case_signature

# -------------------------------------------------
# DISPLAY CASE INFORMATION
# -------------------------------------------------

st.subheader("📋 Case Information")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Concept",
        case["concept"]
    )

with col2:

    st.metric(
        "OSI Layer",
        case["osi_layer"]
    )

with col3:

    st.metric(
        "Severity",
        case["severity"]
    )


st.markdown("### 🚨 Symptom")

st.info(case["symptom"])


st.markdown("### 🗺️ Topology Context")

st.write(case["topology_note"])


st.markdown("### 💻 Network Evidence")

st.code(
    case["show_output"],
    language="text"
)


st.divider()


# -------------------------------------------------
# RUN DIAGNOSIS BUTTON
# -------------------------------------------------

if st.button(
    "🧠 Run NetSage Diagnosis",
    type="primary",
    use_container_width=True
):

    if (
        case_mode == "✨ Analyze Custom Case"
        and (
            not custom_symptom.strip()
            or not custom_evidence.strip()
        )
    ):

        st.error(
            "⚠️ Please enter at least the Network Symptom "
            "and Network Evidence before running the diagnosis."
        )

    else:

        with st.spinner(
            "Analyzing network evidence..."
        ):

            st.session_state.diagnosis = diagnose_case(case)

        quality_score_for_history, _ = analyze_evidence_quality(
            case,
            st.session_state.diagnosis
        )

        risk_message_for_history, _ = calculate_risk_level(
            case,
            st.session_state.diagnosis,
            quality_score_for_history
        )

        save_diagnosis_history(
            case,
            st.session_state.diagnosis,
            quality_score_for_history,
            risk_message_for_history
        )

        st.success("Diagnosis completed!")

diagnosis = {
    "confidence": 0,
    "severity": "Unknown",
    "predicted_root_cause": "No root cause available.",
    "rule_findings": [],
    "recommendations": []
}

if st.session_state.diagnosis:
    diagnosis.update(st.session_state.diagnosis)

if diagnosis:

    # ---------------------------------------------
    # DIAGNOSIS RESULTS
    # ---------------------------------------------

    st.subheader("🧠 Diagnosis Result")
    # ---------------------------------------------
    # EVIDENCE CONFIDENCE METER
    # ---------------------------------------------

    evidence_score, evidence_reasons = analyze_evidence(
        case,
        diagnosis
    )

    st.markdown("### 📊 Evidence Confidence Meter")

    meter_col1, meter_col2 = st.columns([1, 3])

    with meter_col1:

        st.metric(
            "Evidence Score",
            f"{evidence_score}%"
        )

    with meter_col2:

        st.progress(evidence_score / 100)


    # Evidence interpretation

    if evidence_score >= 80:

        st.success(
            "Strong evidence: The diagnosis is supported by "
            "multiple pieces of network information."
        )

    elif evidence_score >= 60:

        st.warning(
            "Moderate evidence: Verify additional network "
            "details before applying a fix."
        )

    else:

        st.error(
            "Weak evidence: More troubleshooting data is required."
        )


    with st.expander("🔍 Why this evidence score?"):

        for reason in evidence_reasons:

            st.write(f"✅ {reason}")

    result_col1, result_col2, result_col3 = st.columns(3)


    with result_col1:

        st.metric(
            "Confidence",
            f"{diagnosis['confidence']}%"
        )


    with result_col2:

        st.metric(
            "Severity",
            diagnosis["severity"]
        )


    with result_col3:

        st.metric(
            "Human Review",
            "Required"
        )


    st.markdown("### 🎯 Predicted Root Cause")
    st.error(diagnosis["predicted_root_cause"])

    # ---------------------------------------------
    # TROUBLESHOOTING DECISION PATH
    # ---------------------------------------------

    st.markdown("### 🧭 NetSage Troubleshooting Decision Path")

    path_col1, path_col2, path_col3, path_col4 = st.columns(4)


    with path_col1:

        st.info(
            "1️⃣ Evidence\n\n"
            "Symptom + topology + show output"
        )


    with path_col2:

        if diagnosis["rule_findings"]:

            st.success(
                "2️⃣ Rule Check\n\n"
                "Configuration pattern detected"
            )

        else:

            st.warning(
                "2️⃣ Rule Check\n\n"
                "No direct rule violation"
            )


    with path_col3:

        st.info(
            "3️⃣ Diagnosis\n\n"
            f"{diagnosis['confidence']}% confidence"
        )


    with path_col4:

        st.warning(
            "4️⃣ Human Review\n\n"
            "Verify before applying changes"
        )
# -------------------------------------------------
# INTELLIGENT EVIDENCE ANALYSIS DISPLAY
# -------------------------------------------------

st.divider()

st.subheader("🔬 Intelligent Evidence Analysis")

quality_score, evidence_issues = analyze_evidence_quality(
    case,
    diagnosis
)
risk_message, risk_level = calculate_risk_level(
    case,
    diagnosis,
    quality_score
)
health_score, health_reasons = calculate_network_health(
    diagnosis,
    quality_score,
    risk_level
)

playbook = generate_playbook(
    case,
    diagnosis
)
similar_cases = find_similar_cases(
    case,
    diagnosis
)
save_diagnosis_history(
    case,
    diagnosis,
    quality_score,
    risk_message
)
st.write("DEBUG Severity:", case.get("severity"))
st.write("DEBUG Confidence:", diagnosis.get("confidence"))
st.write("DEBUG Evidence Quality:", quality_score)

st.write(f"### Evidence Quality Score: {quality_score}%")

st.progress(quality_score / 100)

if evidence_issues:

    st.warning(
        "NetSage identified the following evidence limitations:"
    )

    for issue in evidence_issues:
        st.write(issue)

else:

    st.success(
        "✅ Evidence quality is strong. "
        "No major evidence limitations were detected."
    )

if quality_score < 70:

    st.info(
        "👤 Human review is recommended because the available "
        "evidence is incomplete or uncertain."
    )
    # -------------------------------------------------
# DIAGNOSIS RISK LEVEL DISPLAY
# -------------------------------------------------

st.divider()

st.subheader("🚦 Diagnosis Risk Level")

if risk_level == "critical":

    st.error(risk_message)

elif risk_level == "high":

    st.warning(risk_message)

elif risk_level == "medium":

    st.info(risk_message)

else:

    st.success(risk_message)

    # -------------------------------------------------
# NETWORK HEALTH SCORE
# -------------------------------------------------

st.divider()

st.subheader("🏥 Network Health Score")

health_col1, health_col2 = st.columns(
    [1, 3]
)

with health_col1:

    st.metric(
        "Health Score",
        f"{health_score}/100"
    )


with health_col2:

    st.progress(
        health_score / 100
    )

    # ---------------------------------------------
    # HEALTH STATUS
    # ---------------------------------------------

if health_score >= 80:

    st.success(
        "🟢 Healthy Network"
    )

elif health_score >= 60:

    st.info(
        "🟡 Network Needs Attention"
    )

elif health_score >= 40:

    st.warning(
        "🟠 Network Health is Poor"
    )

else:

    st.error(
        "🔴 Critical Network Condition"
    )

with st.expander(
    "🔍 Why this health score?"
):

    if health_reasons:

        for reason in health_reasons:

            st.write(reason)

    else:

        st.success(
            "No major network health risks were detected."
        )

# -------------------------------------------------
# SIMILAR PAST CASES
# -------------------------------------------------

st.divider()

st.subheader("🔎 Similar Past Cases")

if similar_cases.empty:

    st.info(
        "No similar previous diagnosis was found. "
        "This may be a new type of network issue."
    )

else:

    st.success(
        f"Found {len(similar_cases)} similar past case(s)."
    )

    # Select useful columns only

    display_columns = [
        "timestamp",
        "case_id",
        "concept",
        "severity",
        "predicted_root_cause",
        "confidence",
        "risk_level"
    ]

    # Keep only columns that actually exist

    available_columns = [
        column
        for column in display_columns
        if column in similar_cases.columns
    ]

    st.dataframe(
        similar_cases[
            available_columns
        ],
        use_container_width=True
    )

    # ---------------------------------------------
    # SMART INSIGHT
    # ---------------------------------------------

    st.markdown("### 💡 NetSage Historical Insight")

    most_common_cause = (
        similar_cases[
            "predicted_root_cause"
        ]
        .mode()
        .iloc[0]
    )

    occurrence_count = len(
        similar_cases[
            similar_cases[
                "predicted_root_cause"
            ]
            == most_common_cause
        ]
    )

    st.info(
        f"The most common root cause among similar "
        f"past cases was **{most_common_cause}**, "
        f"appearing in {occurrence_count} recorded case(s)."
    )

    # -------------------------------------------------
# SMART TROUBLESHOOTING PLAYBOOK DISPLAY
# -------------------------------------------------

st.divider()

st.subheader("🛠️ Smart Troubleshooting Playbook")

st.caption(
    "A step-by-step investigation plan generated from the "
    "network concept, detected findings, and available evidence."
)

for index, item in enumerate(playbook, start=1):

    with st.expander(
        f"Step {index}: {item['step']}",
        expanded=(index == 1)
    ):

        st.markdown("#### 🔧 Action")

        st.write(
            item["action"]
        )

        st.markdown("#### 💻 Command / Check")

        st.code(
            item["command"],
            language="text"
        )

        st.markdown("#### ✅ Expected Result")

        st.success(
            item["expected"]
        )


# ---------------------------------------------
# PLAYBOOK SAFETY NOTICE
# ---------------------------------------------

if risk_level in ["critical", "high"]:

    st.warning(
        "⚠️ Safety Check: This case has a high diagnostic risk. "
        "Verify the network state and configuration before "
        "applying any corrective changes."
    )

elif risk_level == "medium":

    st.info(
        "🔎 Verification Recommended: Collect additional evidence "
        "and confirm the diagnosis before making configuration changes."
    )

else:

    st.success(
        "✅ Evidence quality is acceptable. Follow the playbook "
        "while monitoring the network for unexpected changes."
    )


# -------------------------------------------------
# DOWNLOAD INCIDENT REPORT
# -------------------------------------------------

st.divider()

st.subheader("📄 Export Network Incident Report")

st.write(
    "Generate a professional PDF report containing the "
    "diagnosis, evidence analysis, risk assessment, "
    "historical insight, and troubleshooting playbook."
)

pdf_report = generate_incident_report(
    case,
    diagnosis,
    quality_score,
    risk_message,
    playbook,
    similar_cases
)

st.download_button(
    label="📥 Download Professional PDF Report",
    data=pdf_report,
    file_name="NetSage_Incident_Report.pdf",
    mime="application/pdf",
    use_container_width=True
)
# -------------------------------------------------
# EXPLAINABLE AI - DIAGNOSIS TRANSPARENCY PANEL
# -------------------------------------------------

st.divider()

st.subheader("🧠 Why did NetSage give this diagnosis?")

with st.expander(
    "🔍 View Diagnosis Explanation",
    expanded=False
):

    # ---------------------------------------------
    # ROOT CAUSE
    # ---------------------------------------------

    st.markdown("### 🎯 Predicted Root Cause")

    st.write(
        diagnosis.get(
            "predicted_root_cause",
            "No root cause available."
        )
    )


    # ---------------------------------------------
    # FINDINGS AND EVIDENCE
    # ---------------------------------------------

    st.markdown("### 🔎 Evidence and Rule Analysis")

    findings = diagnosis.get("rule_findings", [])

    if findings:

        st.write(
            "NetSage detected the following issue(s) "
            "from the provided network evidence:"
        )

        for index, finding in enumerate(findings, start=1):

            issue = finding.get("issue", "Unknown Issue")
            severity = finding.get("severity", "Unknown")
            evidence_text = finding.get(
                "evidence",
                "No evidence explanation available."
            )

            st.markdown(f"#### Finding {index}: {issue}")

            st.write(f"**Severity:** {severity}")

            st.write(
                f"**Why it was detected:** {evidence_text}"
            )

            st.divider()

    else:

        st.warning(
            "No deterministic rule directly matched "
            "the provided evidence."
        )

        st.write(
            "The diagnosis may be based on the available "
            "case context."
        )


    # ---------------------------------------------
    # CONFIDENCE EXPLANATION
    # ---------------------------------------------

    st.markdown("### 📊 Confidence Explanation")

    confidence = diagnosis.get("confidence", 0)

    st.write(
        f"NetSage assigned a confidence score of "
        f"**{confidence}%**."
    )

    if confidence >= 80:

        st.success(
            "High confidence: strong evidence or rule-based "
            "support was found."
        )

    elif confidence >= 50:

        st.warning(
            "Medium confidence: some supporting evidence "
            "was found, but additional verification may help."
        )

    else:

        st.error(
            "Low confidence: human verification is recommended "
            "before making network changes."
        )


    # ---------------------------------------------
    # RECOMMENDED NEXT ACTION
    # ---------------------------------------------

    st.markdown("### 🛠️ Recommended Next Action")

    if evidence_issues or confidence < 70:

        st.info(
            "Collect additional network evidence and request "
            "human review before applying configuration changes."
        )

    else:

        st.success(
            "The evidence is sufficiently strong to proceed "
            "with the recommended troubleshooting steps."
        )
    st.markdown("### 🔍 Rule-Based Findings")
     # ---------------------------------------------
    # EVIDENCE SUMMARY
    # ---------------------------------------------

    st.markdown("### 📌 Evidence Summary")

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:

        st.metric(
            "Evidence Score",
            f"{evidence_score}%"
        )

    with summary_col2:

        st.metric(
            "Rule Findings",
            len(diagnosis["rule_findings"])
        )

    with summary_col3:

        st.metric(
            "Diagnosis Confidence",
            f"{diagnosis['confidence']}%"
        )


    if diagnosis["rule_findings"]:

        for finding in diagnosis["rule_findings"]:

            with st.expander(
                f"⚠️ {finding['issue']} "
                f"— {finding['severity']}"
            ):

                st.write(
                    "**Evidence:**",
                    finding["evidence"]
                )

                st.write(
                    "**Recommendation:**",
                    finding["recommendation"]
                )

    else:

        st.info(
            "No deterministic rule violation was detected. "
            "Diagnosis is based on available case evidence."
        )


    st.markdown("### 🛠️ Recommended Troubleshooting Steps")


    for index, recommendation in enumerate(
        diagnosis["recommendations"],
        start=1
    ):

        st.write(
            f"{index}. {recommendation}"
        )


    st.divider()

# ---------------------------------------------
# HUMAN REVIEW
# ---------------------------------------------

st.divider()

st.subheader("👤 Human Review")

st.write(
    "Review the diagnosis generated by NetSage AI "
    "before taking any network action."
)

review = st.radio(
    "Was the diagnosis useful?",
    [
        "✅ Correct",
        "❌ Incorrect",
        "🔎 Needs Investigation"
    ],
    horizontal=True
)

comments = st.text_area(
    "📝 Review Comments",
    placeholder=(
        "Example: The VLAN assignment was verified "
        "and the diagnosis was correct."
    )
)

if st.button(
    "💾 Submit Review",
    use_container_width=True
):

    save_review(
        case,
        diagnosis,
        review,
        comments
    )

    st.success(
        "✅ Review saved successfully!"
    )
    # ---------------------------------------------
# REVIEW ANALYTICS DASHBOARD
# ---------------------------------------------

st.divider()

st.subheader("📊 Human Review Analytics")

analytics = get_review_analytics()


if analytics is None:

    st.info(
        "No review data available yet. "
        "Submit a Human Review to start generating analytics."
    )

else:

    analytics_col1, analytics_col2, analytics_col3, analytics_col4 = st.columns(4)


    with analytics_col1:

        st.metric(
            "Total Reviews",
            analytics["total_reviews"]
        )


    with analytics_col2:

        st.metric(
            "Correct",
            analytics["correct_reviews"]
        )


    with analytics_col3:

        st.metric(
            "Incorrect",
            analytics["incorrect_reviews"]
        )


    with analytics_col4:

        st.metric(
            "Needs Investigation",
            analytics["investigation_reviews"]
        )


    st.markdown("### 🎯 Human-Verified Diagnosis Accuracy")

    st.progress(
        analytics["accuracy"] / 100
    )

    st.write(
        f"**{analytics['accuracy']}%** of reviewed "
        "NetSage diagnoses were marked as correct."
    )


    with st.expander("📋 View Review History"):

        st.dataframe(
            analytics["data"],
            use_container_width=True
        )
    # ---------------------------------------------
    # RESPONSIBLE AI SECTION
    # ---------------------------------------------

    st.subheader("🛡️ Responsible AI")

    st.warning(
        "This diagnosis is a troubleshooting recommendation, "
        "not an automatic network configuration change."
    )

    st.info(
        "A human network administrator should verify evidence "
        "before applying any configuration changes."
    )
    # -------------------------------------------------
# DIAGNOSIS HISTORY
# -------------------------------------------------

st.divider()

st.subheader("📚 Diagnosis History")

history_df = load_diagnosis_history()

if history_df.empty:

    st.info(
        "No diagnosis history available yet. "
        "Run a network diagnosis to create the first history record."
    )

else:

    st.write(
        f"Total diagnoses recorded: {len(history_df)}"
    )

    st.dataframe(
        history_df,
        use_container_width=True
    )
    st.divider()

st.markdown("### 🗑️ History Management")

confirm_clear = st.checkbox(
    "I understand that clearing history cannot be undone."
)

if confirm_clear:

    if st.button(
        "🗑️ Clear Diagnosis History",
        use_container_width=True
    ):

        empty_history = pd.DataFrame(
            columns=[
                "timestamp",
                "case_id",
                "concept",
                "severity",
                "predicted_root_cause",
                "confidence",
                "evidence_quality",
                "risk_level"
            ]
        )

        empty_history.to_csv(
            "data/diagnosis_history.csv",
            index=False
        )

        st.success(
            "Diagnosis history cleared successfully!"
        )


        # -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.divider()

st.caption(
    "🌐 NetSage AI | Evidence-First Network Troubleshooting Copilot"
)

st.caption(
    "Built with Python, Streamlit, Pandas, Rule-Based AI, "
    "Explainable AI, Human-in-the-Loop Review, and Responsible AI principles."
)

st.caption(
    "⚠️ NetSage AI provides troubleshooting recommendations. "
    "Always verify network changes before applying them in production."
)

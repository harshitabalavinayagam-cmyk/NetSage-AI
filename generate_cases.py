import csv
import os


cases = [
    # ================= VLAN CASES =================

    {
        "case_id": "VLAN-001",
        "symptom": "PC1 cannot communicate with PC2 although both are expected to be in VLAN 20.",
        "topology_note": "PC1 connected to Switch1 Fa0/5 and PC2 connected to Switch1 Fa0/6.",
        "show_output": """Switch# show interfaces fa0/5 switchport
Administrative Mode: static access
Operational Mode: static access
Access Mode VLAN: 10

Switch# show vlan brief
10 SALES active Fa0/5
20 HR active Fa0/6""",
        "expected_fault": "PC1 is assigned to VLAN 10 instead of VLAN 20.",
        "osi_layer": "Layer 2",
        "concept": "VLAN",
        "severity": "Medium"
    },

    {
        "case_id": "VLAN-002",
        "symptom": "Devices in VLAN 30 on two switches cannot communicate.",
        "topology_note": "Switch1 and Switch2 are connected through a trunk link.",
        "show_output": """Switch# show interfaces trunk
Port        Mode         Encapsulation  Status        Native vlan
Fa0/24      on           802.1q         trunking      1

Vlans allowed on trunk
10,20

Switch# show vlan brief
30 ENGINEERING active""",
        "expected_fault": "VLAN 30 is not allowed on the trunk.",
        "osi_layer": "Layer 2",
        "concept": "VLAN",
        "severity": "High"
    },

    {
        "case_id": "VLAN-003",
        "symptom": "PC connected to Fa0/10 cannot access the department network.",
        "topology_note": "PC should belong to VLAN 40.",
        "show_output": """Switch# show vlan brief
10 SALES active
20 HR active
30 ENGINEERING active

Switch# show interfaces fa0/10 switchport
Access Mode VLAN: 1""",
        "expected_fault": "VLAN 40 is missing and the port remains in VLAN 1.",
        "osi_layer": "Layer 2",
        "concept": "VLAN",
        "severity": "High"
    },

    {
        "case_id": "VLAN-004",
        "symptom": "Users in VLAN 50 cannot communicate across switches.",
        "topology_note": "VLAN 50 should pass through the trunk.",
        "show_output": """Switch# show interfaces trunk
Vlans allowed on trunk
10,20,30,40

Switch# show vlan brief
50 GUEST active""",
        "expected_fault": "VLAN 50 is not allowed on the trunk.",
        "osi_layer": "Layer 2",
        "concept": "VLAN",
        "severity": "Medium"
    },

    # ================= GATEWAY CASES =================

    {
        "case_id": "GW-001",
        "symptom": "PC can communicate with devices in the same network but cannot reach other networks.",
        "topology_note": "PC address is 192.168.10.20/24.",
        "show_output": """PC> ipconfig

IP Address: 192.168.10.20
Subnet Mask: 255.255.255.0
Default Gateway: 192.168.1.1""",
        "expected_fault": "Default gateway is configured for the wrong network.",
        "osi_layer": "Layer 3",
        "concept": "Gateway",
        "severity": "High"
    },

    {
        "case_id": "GW-002",
        "symptom": "PC cannot reach its default gateway.",
        "topology_note": "Router interface should be 10.0.0.1.",
        "show_output": """PC> ipconfig
IP Address: 10.0.0.10
Subnet Mask: 255.255.255.0
Default Gateway: 10.0.0.254

Router# show ip interface brief
GigabitEthernet0/0 10.0.0.1 up up""",
        "expected_fault": "PC default gateway does not match the router interface.",
        "osi_layer": "Layer 3",
        "concept": "Gateway",
        "severity": "High"
    },

    {
        "case_id": "GW-003",
        "symptom": "Multiple PCs cannot access external networks.",
        "topology_note": "All PCs are in 172.16.5.0/24.",
        "show_output": """PC> ipconfig
IP Address: 172.16.5.20
Subnet Mask: 255.255.255.0
Default Gateway: 172.16.6.1""",
        "expected_fault": "Gateway belongs to a different subnet.",
        "osi_layer": "Layer 3",
        "concept": "Gateway",
        "severity": "High"
    },

    # ================= DHCP CASES =================

    {
        "case_id": "DHCP-001",
        "symptom": "Client receives an APIPA address instead of a valid network address.",
        "topology_note": "Client should receive an address from 192.168.20.0/24.",
        "show_output": """PC> ipconfig
IP Address: 169.254.10.15

Router# show ip dhcp pool
Pool OFFICE
Network 192.168.20.0 /24
Leased addresses: 0""",
        "expected_fault": "DHCP allocation is failing; client is not receiving a valid lease.",
        "osi_layer": "Layer 7",
        "concept": "DHCP",
        "severity": "High"
    },

    {
        "case_id": "DHCP-002",
        "symptom": "New clients cannot obtain IP addresses.",
        "topology_note": "Existing clients already occupy most addresses.",
        "show_output": """Router# show ip dhcp pool
Pool LAB
Network 192.168.30.0 /24
Total addresses: 10
Leased addresses: 10
Available addresses: 0""",
        "expected_fault": "DHCP pool is exhausted.",
        "osi_layer": "Layer 7",
        "concept": "DHCP",
        "severity": "High"
    },

    {
        "case_id": "DHCP-003",
        "symptom": "Client receives an IP address from the wrong network.",
        "topology_note": "Client belongs to VLAN 40 and should receive 192.168.40.0/24.",
        "show_output": """Router# show ip dhcp pool
Pool VLAN40
Network 192.168.50.0 /24

PC> ipconfig
IP Address: 192.168.50.12""",
        "expected_fault": "DHCP pool network does not match the client VLAN.",
        "osi_layer": "Layer 7",
        "concept": "DHCP",
        "severity": "Medium"
    },

    {
        "case_id": "DHCP-004",
        "symptom": "Remote subnet clients cannot obtain DHCP addresses.",
        "topology_note": "DHCP server is on another network.",
        "show_output": """Router# show running-config interface g0/1
interface GigabitEthernet0/1
 ip address 192.168.60.1 255.255.255.0

Router# show ip dhcp relay
No helper address configured""",
        "expected_fault": "DHCP relay or ip helper-address is missing.",
        "osi_layer": "Layer 3/7",
        "concept": "DHCP",
        "severity": "High"
    },

    # ================= DNS CASES =================

    {
        "case_id": "DNS-001",
        "symptom": "Users can ping 8.8.8.8 but cannot access www.example.com.",
        "topology_note": "Internet connectivity is working.",
        "show_output": """PC> ipconfig
IP Address: 192.168.1.10
Default Gateway: 192.168.1.1
DNS Server: 0.0.0.0""",
        "expected_fault": "DNS server is not configured.",
        "osi_layer": "Layer 7",
        "concept": "DNS",
        "severity": "Medium"
    },

    {
        "case_id": "DNS-002",
        "symptom": "Internal website hostname cannot be resolved.",
        "topology_note": "DNS server should be 10.10.10.5.",
        "show_output": """PC> ipconfig
DNS Server: 10.10.10.50

PC> nslookup intranet.local
Server: 10.10.10.50
Request timed out""",
        "expected_fault": "Incorrect DNS server address is configured.",
        "osi_layer": "Layer 7",
        "concept": "DNS",
        "severity": "Medium"
    },

    {
        "case_id": "DNS-003",
        "symptom": "Only one hostname cannot be resolved while other names work.",
        "topology_note": "DNS server is reachable.",
        "show_output": """PC> nslookup server.company.local
*** server.company.local not found

PC> nslookup portal.company.local
Name: portal.company.local
Address: 192.168.100.10""",
        "expected_fault": "DNS record for server.company.local is missing.",
        "osi_layer": "Layer 7",
        "concept": "DNS",
        "severity": "Low"
    },

    # ================= ROUTING CASES =================

    {
        "case_id": "ROUTE-001",
        "symptom": "Network 192.168.30.0 cannot reach network 192.168.40.0.",
        "topology_note": "Two routers connect the networks.",
        "show_output": """Router# show ip route
C 192.168.30.0/24 is directly connected
C 10.0.0.0/30 is directly connected

No route to 192.168.40.0/24""",
        "expected_fault": "Static or dynamic route to 192.168.40.0/24 is missing.",
        "osi_layer": "Layer 3",
        "concept": "Routing",
        "severity": "High"
    },

    {
        "case_id": "ROUTE-002",
        "symptom": "Packets cannot reach a remote branch network.",
        "topology_note": "Static route uses next hop 10.1.1.2.",
        "show_output": """Router# show running-config
ip route 192.168.70.0 255.255.255.0 10.1.1.2

Router# ping 10.1.1.2
.....
Success rate is 0 percent""",
        "expected_fault": "Configured next hop is unreachable.",
        "osi_layer": "Layer 3",
        "concept": "Routing",
        "severity": "High"
    },

    {
        "case_id": "ROUTE-003",
        "symptom": "Branch network intermittently loses connectivity.",
        "topology_note": "Routing protocol is expected to advertise all LAN networks.",
        "show_output": """Router# show ip route
O 192.168.80.0/24 [110/2]
C 192.168.90.0/24 is directly connected

Router# show ip ospf neighbor
Neighbor ID: 2.2.2.2 FULL""",
        "expected_fault": "Required network is not being advertised into OSPF.",
        "osi_layer": "Layer 3",
        "concept": "Routing",
        "severity": "Medium"
    },

    {
        "case_id": "ROUTE-004",
        "symptom": "Router forwards traffic to an incorrect network path.",
        "topology_note": "Destination should be reached through 172.20.1.2.",
        "show_output": """Router# show ip route 192.168.100.0
S 192.168.100.0/24 [1/0] via 172.20.1.3""",
        "expected_fault": "Static route uses the wrong next-hop address.",
        "osi_layer": "Layer 3",
        "concept": "Routing",
        "severity": "High"
    },

    {
        "case_id": "ROUTE-005",
        "symptom": "Remote traffic is sent to the wrong router.",
        "topology_note": "Default route should point to 192.0.2.1.",
        "show_output": """Router# show ip route
Gateway of last resort is 192.0.2.254

S* 0.0.0.0/0 via 192.0.2.254""",
        "expected_fault": "Default route points to the wrong gateway.",
        "osi_layer": "Layer 3",
        "concept": "Routing",
        "severity": "High"
    },

    # ================= ACL CASES =================

    {
        "case_id": "ACL-001",
        "symptom": "Users can ping the web server but cannot open its HTTP service.",
        "topology_note": "Web server address is 192.168.100.10.",
        "show_output": """Router# show access-lists
Extended IP access list WEB-FILTER
10 deny tcp any host 192.168.100.10 eq 80
20 permit ip any any""",
        "expected_fault": "ACL explicitly blocks HTTP traffic to the web server.",
        "osi_layer": "Layer 3/4",
        "concept": "ACL",
        "severity": "High"
    },

    {
        "case_id": "ACL-002",
        "symptom": "A department cannot access an internal application.",
        "topology_note": "Traffic originates from 10.20.0.0/16.",
        "show_output": """Router# show access-lists
Standard IP access list 10
10 deny 10.20.0.0 0.0.255.255
20 permit any""",
        "expected_fault": "ACL denies traffic from the department subnet.",
        "osi_layer": "Layer 3",
        "concept": "ACL",
        "severity": "High"
    },

    {
        "case_id": "ACL-003",
        "symptom": "SSH access to the router fails from the management PC.",
        "topology_note": "Management PC address is 192.168.200.50.",
        "show_output": """Router# show running-config | section line vty
line vty 0 4
 access-class 50 in

Router# show access-lists 50
10 permit 192.168.200.60
20 deny any""",
        "expected_fault": "Management PC is not permitted by the VTY ACL.",
        "osi_layer": "Layer 3/7",
        "concept": "ACL",
        "severity": "Medium"
    },

    {
        "case_id": "ACL-004",
        "symptom": "Guest users cannot access the internet.",
        "topology_note": "Guest VLAN is 192.168.150.0/24.",
        "show_output": """Router# show access-lists
Extended IP access list GUEST
10 deny ip 192.168.150.0 0.0.0.255 any
20 permit ip any any""",
        "expected_fault": "ACL denies all guest VLAN traffic.",
        "osi_layer": "Layer 3",
        "concept": "ACL",
        "severity": "High"
    },

    # ================= NAT CASES =================

    {
        "case_id": "NAT-001",
        "symptom": "Internal users cannot access the internet.",
        "topology_note": "Inside network is 192.168.10.0/24.",
        "show_output": """Router# show ip nat translations
No entries found

Router# show running-config | include ip nat
ip nat inside source list 1 interface GigabitEthernet0/1 overload

Router# show ip interface brief
GigabitEthernet0/0 192.168.10.1 up up
GigabitEthernet0/1 203.0.113.2 up up""",
        "expected_fault": "NAT inside/outside interface configuration is missing.",
        "osi_layer": "Layer 3",
        "concept": "NAT",
        "severity": "High"
    },

    {
        "case_id": "NAT-002",
        "symptom": "Only some internal devices can access the internet.",
        "topology_note": "NAT ACL should include 192.168.20.0/24.",
        "show_output": """Router# show access-lists 1
Standard IP access list 1
10 permit 192.168.10.0 0.0.0.255

Router# show ip nat translations
No translation for 192.168.20.25""",
        "expected_fault": "NAT access list does not include 192.168.20.0/24.",
        "osi_layer": "Layer 3",
        "concept": "NAT",
        "severity": "Medium"
    },

    {
        "case_id": "NAT-003",
        "symptom": "Internal network can ping the router but cannot reach public addresses.",
        "topology_note": "Outside interface should connect to ISP.",
        "show_output": """Router# show ip interface brief
GigabitEthernet0/0 192.168.30.1 up up
GigabitEthernet0/1 unassigned administratively down down""",
        "expected_fault": "NAT outside interface is administratively down.",
        "osi_layer": "Layer 1/3",
        "concept": "NAT",
        "severity": "High"
    },

    # ================= WIRELESS CASES =================

    {
        "case_id": "WIFI-001",
        "symptom": "Wireless clients cannot connect to the corporate Wi-Fi.",
        "topology_note": "SSID should be CorpNet.",
        "show_output": """AccessPoint# show wireless summary
SSID: Corp_Net
Status: Enabled""",
        "expected_fault": "Configured SSID does not match the expected SSID.",
        "osi_layer": "Layer 2",
        "concept": "Wireless",
        "severity": "Medium"
    },

    {
        "case_id": "WIFI-002",
        "symptom": "Wireless clients connect but receive no IP address.",
        "topology_note": "Wireless clients should use VLAN 60.",
        "show_output": """AccessPoint# show vlan
SSID GuestWiFi VLAN 60

Router# show ip dhcp pool
Pool VLAN50
Network 192.168.50.0 /24""",
        "expected_fault": "DHCP pool does not match the wireless VLAN.",
        "osi_layer": "Layer 2/7",
        "concept": "Wireless",
        "severity": "High"
    },

    {
        "case_id": "WIFI-003",
        "symptom": "Guest Wi-Fi users can access internal company servers.",
        "topology_note": "Guest network must be isolated from internal network.",
        "show_output": """Router# show access-lists
Extended IP access list GUEST-OUT
10 permit ip 192.168.70.0 0.0.0.255 any""",
        "expected_fault": "Guest isolation ACL is missing; guest traffic is allowed to all networks.",
        "osi_layer": "Layer 3/4",
        "concept": "Wireless",
        "severity": "Critical"
    },

    {
        "case_id": "WIFI-004",
        "symptom": "Wireless clients repeatedly disconnect.",
        "topology_note": "Access point should operate on a non-overlapping channel.",
        "show_output": """AccessPoint# show wireless channel
Channel: 6

Nearby APs:
AP1 Channel 6
AP2 Channel 6
AP3 Channel 6""",
        "expected_fault": "Severe co-channel interference affects wireless stability.",
        "osi_layer": "Layer 1",
        "concept": "Wireless",
        "severity": "Medium"
    }
]


output_file = os.path.join("data", "cases.csv")

with open(output_file, "w", newline="", encoding="utf-8") as file:
    fieldnames = [
        "case_id",
        "symptom",
        "topology_note",
        "show_output",
        "expected_fault",
        "osi_layer",
        "concept",
        "severity"
    ]

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(cases)


print("SUCCESS!")
print(f"{len(cases)} network troubleshooting cases created.")
print(f"Dataset saved to: {output_file}")
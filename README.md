# CloudStack Kea IPv6
The code in this repository generates a Kea configuration based on the CloudStack database.

CloudStack currently does not support IPv6 with Prefix Delegation, but this is required for the operation
of Aurora Elements.

Instances already aqcuire a IPv6 Address using Stateless Autoconfiguration (SLAAC), for that Kea nor DHCPv6 is required.

More information about IPv6 in Basic Networking can be found on [the Apache wiki](https://cwiki.apache.org/confluence/display/CLOUDSTACK/IPv6+in+Basic+Networking).

# Prefix Delegation
Using IPv6 [Prefix Delegation](https://en.wikipedia.org/wiki/Prefix_delegation) (IA_PD) Instances can obtain a /60 subnet routed to them in additional do the IPv6 Address they
already obtained through SLAAC.

In order to do this a DHCPv6 server has to run and provide the proper answers.

For this to work the routers/gateways have to support Prefix Delegation through their DHCPv6 Relay. This relay inspects all the traffic
and sees a Prefix being assigned to a host. It then creates a route towards that host.

The example output is from a Juniper MX960 router which shows the routed prefixes:

<pre>
Prefix                  Session Id  Expires  State    Interface    Client DUID
2a00:f10:500:10::/60    3364        171616   BOUND    xe-0/1/0.709 LL_TIME0x1-0x1e91870e-06:a5:de:00:04:47
2a00:f10:500::/60       3362        171238   BOUND    xe-0/1/0.709 LL_TIME0x1-0x1eaa37f5-06:32:b2:00:04:79
</pre>


# Kea Configuration
Kea can be configured to hand out prefixes using IA_PD. IA_NA (Address assignment) is not used since Instances obtain their address through SLAAC.

The [kea guide](http://kea.isc.org/docs/kea-guide.html) shows how reservations can be made for specific hosts so that they always obtain the proper prefix.

A snippet of configuration:

<pre>"reservations": [
    {
        "hw-address": "06:32:b2:00:03:57",
        "prefixes": ["2a00:f10:600::/60"]
    },
    {
        "hw-address": "06:a5:de:00:03:78",
        "prefixes": ["2a00:f10:600:10::/60"]
    }
]</pre>

A full example can be found in this repository.

**NOTE:*** Make sure Kea is listening on a Unicast address where DHCPv6 traffic is forwarded to by the relay agent in the routers/gateways. See the example directory for a full Kea configuration example.

## Generating Kea configuration
In order to generate the Kea configuration a few things are required:
- Admin API access to CloudStack
- Static Mapping between CloudStack VLAN IDs and Kea's 'interface-id' setting
- Static Mapping between CloudStack VLAN IDs and the /40 subnet to use

With this information the Python code in this repository can generate a Kea configuration where it reserves a /60 subnet for each Instance
in that network/POD.

# Usage
The tool is rather simple to use. It looks for *config.json* which configures:
- CloudStack API access
- Kea source configuration file

Now the tool can be run:

<pre>$ ./cloudstack-kea-config.py --keacfg example/kea-dhcp6.conf --config config.json</pre>

If all goes well it will print to stdout a Kea configuration with the prefix information injected into it.

For example:

<pre>{
  "Dhcp6": {
    "subnet6": [
      {
        "interface-id": "VLAN2701",
        "subnet": "2a05:1500:202::/64",
        "reservations": [
          {
            "prefix": "2a00:f10:500::/60",
            "hw-address": "06:51:34:00:00:5e"
          }
        ],
        "reservation-mode": "out-of-pool"
      }</pre>

## config.json
The configuration file contains the API access and the mappings. An example configuration file can be found in the repository.

# DHCPv6 Relay Agent
In the routers/gateways the DHCPv6 Relay Agent has to be configured to forward DHCPv6 traffic to Kea via Unicast.

How this has to be configured depends on your routing platform.

Below are some configuration examples per platform.

In general the following pieces are *mandatory* regardless of the platform which is used:

- Support for DHCPv6 Prefix Delegation
- Forward DHCPv6 traffic to Unicast address where Kea listens on
- The prefixes handed out by Kea have to be routed to the routers (Static, BGP, OSPF, etc)
- DHCPv6 Option 37 (remote-id), [RFC4649](https://tools.ietf.org/html/rfc4649), has to be supported by the platform

[RFC4649](https://tools.ietf.org/html/rfc4649) is mandatory and Kea is configured to extract the MAC address from there:

<pre>{
  "Dhcp6": {
    "mac-sources": [
      "remote-id"
    ]
  }
}</pre>

This way clients can **NOT** spoof/fake requests to the DHCPv6 server since the gateway/router inserts the MAC address into the DHCPv6 packet.

CloudStack already prevents MAC spoofing so this makes it impossible to spoof requests to the DHCPv6 server.

## Brocade XMR
Will follow

## Juniper MX / JunOS
At PCextreme we use the Juniper MX960 routing platform and we configured the DHCPv6 Relay Agent as shown below:

<pre>dhcp-relay {
    dhcpv6 {
        group VLAN709 {
            relay-agent-interface-id {
                use-option-82;
            }
            interface xe-0/1/0.709 {
                overrides {
                    allow-snooped-clients;
                }
            }
        }
        server-group {
            kea-cloudstack {
                2001:db8:100::69;
            }
        }
        active-server-group kea-cloudstack;
    }
}</pre>

# Future
In the future this has to be integrated into CloudStack. But in the meantime we use this code to have a DHCPv6 server running for IA_PD.

Kea can be fully database driven, so that might be work exploring.

What will *never* change is that Kea needs to run on a seperate server. It can not run inside the Virtual Router since DHCPv6 has to be relayed through
the routers/gateways for them to program the proper routes by inspecting the DHCPv6 Replies.

Kea also has to be available on the same Unicast address because that is where the routing platform forwards traffic to.

# Unit Testing
Simply run the *run-tests.sh* script and it should run the Unit Tests:

```$ ./run-tests.sh```

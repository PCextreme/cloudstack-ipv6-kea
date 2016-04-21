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

## Generating Kea configuration
In order to generate the Kea configuration a few things are required:
- Read-Only MySQL access to CloudStack database
- Static Mapping between CloudStack VLAN IDs and Kea's 'interface-id' setting
- Static Mapping between CloudStack VLAN IDs and the /40 subnet to use

With this information the Python code in this repository can generate a Kea configuration where it reserves a /60 subnet for each Instance
in that network/POD.

# Future
In the future this has to be integrated into CloudStack. But in the meantime we use this code to have a DHCPv6 server running for IA_PD.

Kea can be fully database driven, so that might be work exploring.

What will *never* change is that Kea needs to run on a seperate server. I can not run inside the Virtual Router since DHCPv6 has to be relayed through
the routers/gateways for them to program the proper routes by inspecting the DHCPv6 Replies.

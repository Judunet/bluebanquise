NIC with nmcli
--------------

Description
^^^^^^^^^^^

This role configure network interfaces to provide desired ip, prefix, gateway, etc.

This role provides all features availables in the main nmcli module.
Please refer to `nmcli module documentation <https://docs.ansible.com/ansible/latest/collections/community/general/nmcli_module.html>`_ .

Instructions
^^^^^^^^^^^^

Stack specific behaviors
""""""""""""""""""""""""

While all of the nmcli module options are supported,
some provides more integrated features:

* **conn_name**: is equal to **interface**, but has higher precedence over **interface** if both are set.
* **ifname**: is equal to **physical_device**, but has higher precedence over **ifname**  if both are set.
* **type**: is set to *ethernet* by default if not set.
* **ip4**: can be set using a simple ipv4, then role will use **networks[item.network]['.prefix4']** or if not exist to **networks[item.network]['.prefix']** to complete address, or force address with prefix if string *'/'* is present.
* **ip6**: can be set using a simple ipv6, then role will use **networks[item.network]['.prefix6']** to complete address, or force address with prefix if string *'::'* is present.
* **mtu**: has higher precedence over **networks[item.network]['mtu']** if both are set.
* **gw4**: has higher precedence over **networks[item.network]['.gateway4']** which has higher precedence over **networks[item.network]['.gateway']** (if set).
* **gw6**: has higher precedence over **networks[item.network]['.gateway6']** if both are set.

Basic ipv4
""""""""""

.. code-block:: yaml

  network_interfaces:
    - interface: eth0
      ip4: 10.10.0.1
      network: ice1-1

Force gateway and MTU
"""""""""""""""""""""

.. code-block:: yaml

  network_interfaces:
    - interface: eth0
      ip4: 10.10.0.1
      network: ice1-1
      gw4: 10.10.2.1
      mtu: 9000

Multiple ip
"""""""""""

In multiple ip modes, you need to set the prefix yourself:

.. code-block:: yaml

  network_interfaces:
    - interface: eth0
      ip4: 10.10.0.1/16,10.10.0.2/16
      network: ice1-1

Bond
""""

.. code-block:: yaml

  network_interfaces:
    - interface: bond0
      ip4: 10.10.0.1
      network: ice1-1
      type: bond
    - interface: eth0
      type: bond-slave
      master: bond0
    - interface: eth1
      type: bond-slave
      master: bond0

.. warning::
  In BlueBanquise, as the roles are relying on network_interfaces list order,
  never place bond-slave above the bond master (here bond0 definition must be
  set above eth0 and eth1).

Vlan
""""

.. code-block:: yaml

  - interface: vlan100
    type: vlan
    vlan_id: 100
    ifname: eth2
    ip4: 10.100.0.1
    network: net-100


Refer to `nmcli module documentation <https://docs.ansible.com/ansible/latest/collections/community/general/nmcli_module.html>`_
for more options.

Changelog
^^^^^^^^^

* 1.1.0: Rewamp full role to handle all nmcli module features. Benoit Leveugle <benoit.leveugle@gmail.com>
* 1.0.2: Adding Ubuntu 18.04 compatibility. johnnykeats <johnny.keats@outlook.com>
* 1.0.1: Documentation. johnnykeats <johnny.keats@outlook.com>
* 1.0.0: Role creation. Benoit Leveugle <benoit.leveugle@gmail.com>

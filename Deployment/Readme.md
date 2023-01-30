# Deployment details

Here is the information for deploying the entire application stack

In the figure below are there an overview of the four servers, and what applications runs where. The "backend" infrastructure runs on host A and B.

The deployment of host A, B, C and D can be seen in the sub folders:

- [HostA-Application](./HostA-Application/Readme.md)
- [HostB-Turn](./HostB-Turn/Readme.md)
- [HostCD-Router](./HostCD-Router/Readme.md)
- [HostCD-Clients](./HostsCD-Clients/Readme.md)

The [Deployment](./Deployment.drawio.svg) diagram describes the server deployment structure that we expect to deploy and run the tests with.

![Deployment](Deployment.drawio.svg)

## SSH Access to the hosts

To access the hosts the following ssh commands can be used

```shell
# C Clients
ssh -J agpbruger@c.thomsen-it.dk:22022 -X agpbruger@10.3.0.1 -p 22022 -o StrictHostKeyChecking=no
ssh -J agpbruger@c.thomsen-it.dk:22022 -X agpbruger@10.3.0.2 -p 22022 -o StrictHostKeyChecking=no
ssh -J agpbruger@c.thomsen-it.dk:22022 -X agpbruger@10.3.0.3 -p 22022 -o StrictHostKeyChecking=no
ssh -J agpbruger@c.thomsen-it.dk:22022 -X agpbruger@10.3.0.4 -p 22022 -o StrictHostKeyChecking=no
ssh -J agpbruger@c.thomsen-it.dk:22022 -X agpbruger@10.3.0.5 -p 22022 -o StrictHostKeyChecking=no
ssh -J agpbruger@c.thomsen-it.dk:22022 -X agpbruger@10.3.0.6 -p 22022 -o StrictHostKeyChecking=no

# D Clients
ssh -J agpbruger@d.thomsen-it.dk:22022 -X agpbruger@10.4.0.1 -p 22022 -o StrictHostKeyChecking=no
ssh -J agpbruger@d.thomsen-it.dk:22022 -X agpbruger@10.4.0.2 -p 22022 -o StrictHostKeyChecking=no
ssh -J agpbruger@d.thomsen-it.dk:22022 -X agpbruger@10.4.0.3 -p 22022 -o StrictHostKeyChecking=no
ssh -J agpbruger@d.thomsen-it.dk:22022 -X agpbruger@10.4.0.4 -p 22022 -o StrictHostKeyChecking=no
ssh -J agpbruger@d.thomsen-it.dk:22022 -X agpbruger@10.4.0.5 -p 22022 -o StrictHostKeyChecking=no
ssh -J agpbruger@d.thomsen-it.dk:22022 -X agpbruger@10.4.0.6 -p 22022 -o StrictHostKeyChecking=no
```

## Node Exporter

All hosts runs a node exporter on port 9100. The server A will create connection to the hosts via a ssh port forward, to all the clients in service files. See the setup in the playbooks a[setupNodeExporter](./Ansible/playbooks/setupNodeExporter.yaml) and [setupNodeExporterPortForward](./Ansible/playbooks/setupNodeExporterPortForward.yaml)

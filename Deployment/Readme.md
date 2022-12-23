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


## Node Exporter

All hosts runs a node exporter on port 9100. The server A will create connection to the hosts via a ssh port forward, to all the clients in service files. See the setup in the playbooks[setupNodeExporter](./Ansible/playbooks/setupNodeExporter.yaml) and [setupNodeExporterPortForward](./Ansible/playbooks/setupNodeExporterPortForward.yaml)
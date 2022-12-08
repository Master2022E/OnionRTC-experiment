# Ansible

This document describes how to setup Ansible and the plays which is implemented.

The complete list of servers and names can be found in [inventory.yaml](./inventory.yaml) but can be summarized to:

- server-[a-d]
- clients
  - c_clients
    - c[1-6]  
  - d_clients
    - d[1-6]

And can be called by group, list or individually.

## Installation and setup

Read the [getting started documentation](https://docs.ansible.com/ansible/latest/getting_started/index.html) or just install with `python -m pip install --user ansible`


If WSL is used it might be required to set the environment variable `ANSIBLE_CONFIG` to the current directory for it to find the inventory file. Set it with: `export ANSIBLE_CONFIG=$PWD`


There are some plays which requires some updated versions of external collections install them with `ansible-galaxy collection install -r` Further information can be found in the [documentation](https://docs.ansible.com/ansible/latest/collections_guide/collections_installing.html#install-multiple-collections-with-a-requirements-file).

> NOTE: the requirements installation have not been tested yet.

> NOTE: All commands is expected to be run from this directory.

## Testing the setup

Example commands for testing that ansible is working:

```shell
# Check the ram usage of the the server A with
ansible server-a -a "free -h"

# Check the hostname of the server
ansible server-c  -m ansible.builtin.setup -a "filter=ansible_hostname"
```

## SSH setup

The were accessible through password base authentication it can be disabled across all the clients with the following command.

```shell
ansible-playbook playbooks/setupSecureSSH.yaml
```

## SSH keys

The key were generated with:

```shell
mkdir -p ./playbooks/files/.ssh/

ssh-keygen -f ./playbooks/files/.ssh/id_ecdsa -t ecdsa -b 521 -q -N "" -C Deployment
```

The public key is also added to [GitHub](https://github.com/Master2022E/OnionRTC-experiment/settings/keys)

To send the keys to the remote hosts. (Client hosts C1-C6 and D1-D6) run the command 

```shell
ansible-playbook playbooks/setupSSHKeys.yaml
```

## Hostname setup

When browsing the servers can it sometimes be hard to know with certainty which server one is using, Therefor have the hostname's of the servers been defined in the [inventory list](./inventory.yaml) and the hostname can be set for each server.

**Beware that it will reboot the host!**

```shell
ansible-playbook playbooks/setupHostname.yaml -K
```

## Setup APT Package Dependencies

Play which installs the required apt dependencies.

```shell
ansible-playbook playbooks/setupPackageDependencies.yaml -K
```

## Setup Big Buck Bunny

Must be run after the git repository have been fetch, else it will fail or need the force option.

```shell
ansible-playbook playbooks/setupBigBuckbunny.yaml
```

After this the movie is accessible in `~/OnionRTC-experiment/client_scripts/BigBuckBunny.mp4`.

## Git pull

To pull the latest code the ssh keys must be distributed first. Here after is it possible to pull the latest version of the main branch.

```shell
ansible-playbook playbooks/updateGit.yaml
```

The code will be located in `/home/agpbruger/OnionRTC-experiment/`

## CPU status information

The play will display top four cpu processes running and how much CPU it consumes.

```shell
ansible-playbook playbooks/readCPU.yaml --limit c1
```

> NOTE: The -l or --limit flag is currently required. and could be i.e. `clients`, `all`, `c1` or any other host/group.

## Get client logs

To allow the developers to more easily locate errors will the clients log to a file, which then can be reviewed either on the server or locally pulled with a playbook.

```shell
ansible-playbook playbooks/getLogs.yaml --limit "c2,d2"
```

The logs will here after be located in `./playbooks/logs/c2/debug.log` and `./playbooks/logs/d2/debug.log`.

## Check for video device

To check if the video is running on all hosts:

```shell
ansible-playbook playbooks/checkForVideoDevice.yaml
```

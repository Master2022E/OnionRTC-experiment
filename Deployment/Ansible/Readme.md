# Ansible

Installed with `python -m pip install --user ansible` [Get started docs](https://docs.ansible.com/ansible/latest/getting_started/index.html)

If WSL is used it might be useful to point `export ANSIBLE_CONFIG={{CWD}}` The get ansible running.

> NOTE: All commands is expected to be run from this directory.

Example commands for testing that ansible is working:


Check the ram usage of the the server A with `ansible server-a -a "free -h"`

## SSH keys

The key were generated with:

```shell
mkdir -p ./playbooks/files/.ssh/

ssh-keygen -f ./playbooks/files/.ssh/id_ecdsa -t ecdsa -b 521 -q -N "" -C Deployment
```

The public key is also added to [GitHub](https://github.com/Master2022E/OnionRTC-experiment/settings/keys)

To send the keys to the remote hosts. (Client hosts C1-C6 and D1-D6) run the command `ansible-playbook playbooks/sshKeyPlays.yaml`


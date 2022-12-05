# Ansible

Read the [getting started documentation](https://docs.ansible.com/ansible/latest/getting_started/index.html) or just install with `python -m pip install --user ansible`

> NOTE: All commands is expected to be run from this directory.

If WSL is used it might be required to set the environment variable `ANSIBLE_CONFIG` to the current directory for it to find the inventory file. Set it with: `export ANSIBLE_CONFIG=`

Example commands for testing that ansible is working:

- Check the ram usage of the the server A with `ansible server-a -a "free -h"`

There are some plays which requires some updated versions of external collections install them with `ansible-galaxy collection install -r` Further information can be found in the [documentation](https://docs.ansible.com/ansible/latest/collections_guide/collections_installing.html#install-multiple-collections-with-a-requirements-file).

- This feature has not been tested.

## SSH keys

The key were generated with:

```shell
mkdir -p ./playbooks/files/.ssh/

ssh-keygen -f ./playbooks/files/.ssh/id_ecdsa -t ecdsa -b 521 -q -N "" -C Deployment
```

The public key is also added to [GitHub](https://github.com/Master2022E/OnionRTC-experiment/settings/keys)

To send the keys to the remote hosts. (Client hosts C1-C6 and D1-D6) run the command `ansible-playbook playbooks/sshKeyPlays.yaml`


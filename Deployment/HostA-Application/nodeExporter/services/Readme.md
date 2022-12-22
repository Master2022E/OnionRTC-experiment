# Node exporter


## Setup SSH port forwarding

Copy the service files in the service folder into /etc/systemd/system/ on the server-a.
Enable the service with `systemctl enable ssh_forwardingXY.service` and start it wit `systemctl start ssh_forwardingXY.service`, for each client. 

```
systemctl enable ssh_forwardingc1.service
systemctl start ssh_forwardingc1.service

systemctl enable ssh_forwardingc2.service
systemctl start ssh_forwardingc2.service

systemctl enable ssh_forwardingc3.service
systemctl start ssh_forwardingc3.service

systemctl enable ssh_forwardingc4.service
systemctl start ssh_forwardingc4.service

systemctl enable ssh_forwardingc5.service
systemctl start ssh_forwardingc5.service

systemctl enable ssh_forwardingc6.service
systemctl start ssh_forwardingc6.service

systemctl enable ssh_forwardingd1.service
systemctl start ssh_forwardingd1.service

systemctl enable ssh_forwardingd2.service
systemctl start ssh_forwardingd2.service

systemctl enable ssh_forwardingd3.service
systemctl start ssh_forwardingd3.service

systemctl enable ssh_forwardingd4.service
systemctl start ssh_forwardingd4.service

systemctl enable ssh_forwardingd5.service
systemctl start ssh_forwardingd5.service

systemctl enable ssh_forwardingd6.service
systemctl start ssh_forwardingd6.service
```
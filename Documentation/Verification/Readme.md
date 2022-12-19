# Verification

This documents aims to verify that the experiment is done correctly, and show the verification process taken.

## Host configurations

The experiment is executed with the following hardware specs.

|          | CPU | RAM | Disc | Network |
|:---------|----:|----:|-----:|--------:|
| Server A | 4   | 32  | ?    | ?       |
| Server B | 2   | 4   | ?    | ?       |
| Server C | 1   | 2   | ?    | ?       |
| Server D | 1   | 2   | ?    | ?       |
| Clients  | 2   | 4   | ?    | ?       |

All the hosts are virtual machines running on the same physical hardware, but with dedicated CPUs.

### CPU

The command `mpstat 5` will give a new line of output every 5 seconds with a average of the CPU usage as seen in the following output:

```shell
agpbruger@c2-tor-normal:~$ mpstat 5
Linux 5.15.0-56-generic (c2-tor-normal)         12/14/2022      _x86_64_        (2 CPU)

08:50:04 AM  CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
08:50:09 AM  all    0.10    0.00    0.00    0.00    0.00    0.00    0.10    0.00    0.00   99.80
08:50:14 AM  all    0.00    0.00    0.10    0.10    0.00    0.00    0.10    0.00    0.00   99.70
Average:     all    0.05    0.00    0.05    0.05    0.00    0.00    0.10    0.00    0.00   99.75
```

An in depth verification of each client can be found in [Verification/CPU](./CPU/)


### RAM

The command `free -h -s 5` will give a new line of output every 5 seconds with a average of the RAM usage as seen in the following output:

```shell
agpbruger@c2-tor-normal:~$ agpbruger@c2-tor-normal:~$ free -h -s 5
               total        used        free      shared  buff/cache   available
Mem:           3.7Gi       339Mi       2.2Gi       2.0Mi       1.2Gi       3.2Gi
Swap:          4.0Gi          0B       4.0Gi

               total        used        free      shared  buff/cache   available
Mem:           3.7Gi       339Mi       2.2Gi       2.0Mi       1.2Gi       3.2Gi
Swap:          4.0Gi          0B       4.0Gi

               total        used        free      shared  buff/cache   available
Mem:           3.7Gi       353Mi       2.2Gi       2.0Mi       1.2Gi       3.2Gi
```

An in depth verification of each client can be found in [Verification/RAM](./RAM/)


### Disc

TODO: Show the disk usage

### Network

TODO: Show the network usage during a run
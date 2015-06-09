## If SSH-server is not installed on the phone ##

First we establish SSH-tunnel so that the phone can do ssh to the host

On the phone:

```
mkfifo tcp_pipe
cat tcp_pipe | netcat -vlp 9000 | netcat -vlp 9001 > tcp_pipe
rm tcp_pipe
```

On the host:

```
adb forward tcp:9000 tcp:9001
mkfifo tcp_pipe
cat tcp_pipe | netcat -v localhost 9000 | netcat -v localhost 22 > tcp_pipe
rm tcp_pipe
```

Again, on the phone:

```
ssh -L 8080:ftp.de.debian.org:80 -p 9000 user@localhost
```


Replace ftp.de.debian.org with localhost:8080 in /etc/apt/sources.list and we can use apt-get.

## If SSH-server is installed ##

```
adb forward tcp:9000 tcp:22
ssh -R 8080:ftp.de.debian.org:80 -p 9000 user@localhost
```
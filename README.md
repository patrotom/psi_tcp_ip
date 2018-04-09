# TCP server #

* Project written in the Python 3 language.
* The main aim is to mediate the communication between the robot and the user.
* This communication will be realised using the TCP/IP protocol.

## Specification ##

* Use Linux built-in program `ncat` to test communication with your server from the client side. Use switch `-n` to not to print a newline and switch `-e` to skip escaping.

*Example:*
``` bash
echo -ne "Peter is Peter" | nc localhost 10000
```

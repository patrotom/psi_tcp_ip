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

* Server can receive a whole message but it is not mandatory. You have to always check the buffer for the incoming bytes and process a message once delimiter `/a/b` is read.
* It is recommended to separate the project into more logical layers.
    * Receiving of recharging and 3 other types of messages from a client...  
* Test of the authentication:

*Example:*
``` bash
echo -n Mnau\!\\a\\b29869\\a\\bclose | nc localhost 10000
```
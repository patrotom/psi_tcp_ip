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
echo -n Mnau\!\\a\\b20576 | nc localhost 10000
```

* Computing of the hash: `((ASCII * 1000) + SERVER_KEY) % 65536`
    * `65536 = (2^16) - 1` - handling of the overflow of the 16 bit number
* Test of the initial move:

*Example*
``` bash
echo -n Mnau\!\\a\\b20576\\a\\bOK 1 1\\a\\bOK 1 2\\a\\b | nc localhost 10000
```

* Test of the initial move with an error (robot did not perform move forward) in moving:

*Example*
``` bash
echo -n Mnau\!\\a\\b20576\\a\\bOK 1 1\\a\\bOK 1 1\\a\\bOK 1 2\\a\\b | nc localhost 10000
```

* Test of the moving of a robot to the inner square:

*Example*
``` bash
echo -n Mnau\!\\a\\b20576\\a\\bOK 4 5\\a\\bOK 5 5\\a\\bOK 5 4\\a\\bOK 5 3\\a\\bOK 5 2\\a\\bOK 4 2\\a\\bOK 3 2\\a\\bOK 2 2 | nc localhost 10000
```
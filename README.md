# BATTLESHIP

This is a simple online client-server implementation of the classic two-player <em>Battleship</em> game using Python and sockets.

**How to play:**
1. **Start the server:** Run the `server.py` script.
2. **Connect clients:** Run the `client.py` script on a different machine or terminal. To start the server, enter `server.py '' <port-number>` into a terminal running in file directory containing the `server.py` file. To use the client commands, type in a command with the format `client.py <Server IP-Address> <Server Port Number> <Command> <Value>`. Current command usages are `register <username>` and `recognize <username>`. A complete client command to the server would be something like `client.py 127.0.0.1 65432 register billythekid23` or `client.py 127.0.0.1 65432 recognize bobevans42`.
3. **Play the game:** Well, you can't right now... BUT if you could... Players each have a 10x10 tile board on which to set up their battleships. Once their ships are set up, they must guess where the other player's ships are on their board and fire torpedos to hit them. Each player takes a turn firing a torpedo. Once one player has hit every tile on which the enemy player's ships sit, they win! No draws!

**Technologies used:**
* Python
* Sockets

**Additional resources:**
* [Link to Python documentation](https://docs.python.org/3/)
* [Link to sockets tutorial](https://nbviewer.org/url/www.cs.colostate.edu/~cs457/lab/CS457_Lab01_TCPSocketIntro.ipynb)
    

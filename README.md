# BATTLESHIP

This is a simple online client-server implementation of the classic two-player <em>Battleship</em> game using Python and sockets.

**How to play:**
1. **Start the server:** Run the `server.py` script.
2. **Connect clients:** Run the `client.py` script on a different machine or terminal. To start the server, enter `server.py '' <port-number>` into a terminal running in file directory containing the `server.py` file. Follow the instructions given in the client itself in order to connect and start a game. Currently registration to the server is disabled. So you may login with the username "ethandb" with password "mozart" or as username "billythekid23" with password "bob" or as username "" with password "".
3. **Play the game:** Well, you can't right now... BUT if you could... Players each have a 10x10 tile board on which to set up their battleships. Once their ships are set up, they must guess where the other player's ships are on their board and fire torpedos to hit them. Each player takes a turn firing a torpedo. Once one player has hit every tile on which the enemy player's ships sit, they win! No draws!

**Technologies used:**
* Python
* Sockets

**Additional resources:**
* [Link to Python documentation](https://docs.python.org/3/)
* [Link to sockets tutorial](https://nbviewer.org/url/www.cs.colostate.edu/~cs457/lab/CS457_Lab01_TCPSocketIntro.ipynb)
    

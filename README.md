# BATTLESHIP

This is a simple online client-server implementation of the classic two-player <em>Battleship</em> game using Python and sockets.

**How to play:**
1. **Start the server:** Run the `server.py` script.
2. **Connect clients:** Run the `client.py` script on a different machine or terminal. To start the server, enter `server.py '' <port-number>` into a terminal running in file directory containing the `server.py` file. Follow the instructions given in the client itself in order to connect and start a game. Currently, to register a new user, you must register through command-line argument like this: `client.py <host> <port-number> register <username> <password>`.
3. **Play the game:** Players each have a 10x10 tile board on which to set up their battleships. Once their ships are set up, they must guess where the other player's ships are on their board and fire torpedos to hit them. Each player takes a turn firing a torpedo. Once one player has hit every tile on which the enemy player's ships sit, they win! No draws!

**Known Bugs & Limitations:**
1. If one player quits while the other player is waiting for them to take their turn, the player waiting to take their turn will not be notified that the other player has quit. Their only option is to exit the game.
2. You can never back out of any of the menus. For example, if you decide you want to join a server, but then change your mind, you cannot go back and create a server. You have to restart the program.
3. No cyber-security features.

**Technologies used:**
* Python
* Sockets

**Additional resources:**
* [Link to Python documentation](https://docs.python.org/3/)
* [Link to sockets tutorial](https://nbviewer.org/url/www.cs.colostate.edu/~cs457/lab/CS457_Lab01_TCPSocketIntro.ipynb)
    

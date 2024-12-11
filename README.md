# BATTLESHIP

This is a simple online client-server implementation of the classic two-player <em>Battleship</em> game using Python and sockets.

**How to play:**
1. **Start the server:** Run the `server.py` script. To start the server, enter `server.py '' <port-number>` into a terminal running in file directory containing the `server.py` file. 
2. **Connect clients:** Run the `client.py` script on a different machine or terminal with *no arguments*. This will launch the client. Once the client is launched, it will ask you for the server IP address and the Port Number. Once you have entered those and connected to the server, it will ask you to login. Currently, to register a new user, you must register through command-line argument like this: `client.py <host> <port-number> register <username> <password>`. To login, just enter your username, then password. The application will prompt you to create or join a game lobby. If a friend has already started the lobby, select join and enter the name of the lobby. If you want to start a lobby, select create, name the lobby, and wait for a friend to join. Once there are two players in the lobby, the game will automatically start.
3. **Play the game:** Players each have a 10x10 tile board on which to set up their battleships. Once their ships are set up, they must guess where the other player's ships are on their board and fire torpedos to hit them. Each player takes a turn firing a torpedo. Once one player has hit every tile on which the enemy player's ships sit, they win! No draws!

**Known Bugs & Limitations:**
1. If one player quits while the other player is waiting for them to take their turn, the player waiting to take their turn will not be notified that the other player has quit. Their only option is to exit the game.
2. You can never back out of any of the menus. For example, if you decide you want to join a server, but then change your mind, you cannot go back and create a server. You have to restart the program.
3. If someone logins into the same user account at the same time on different terminals, they can desync. Essentially, it's two different clients, but making calls as one.
4. No cyber-security features. Anyone may be able to snoop on this program, and it transfers passwords and usernames without encryption. Do not use passwords you actually care about.
5. Only way to exit the game is hitting CTRL+C or exiting the command prompt

**Technologies used:**
* Python
* Sockets

**Additional resources:**
* [Link to Python documentation](https://docs.python.org/3/)
* [Link to sockets tutorial](https://nbviewer.org/url/www.cs.colostate.edu/~cs457/lab/CS457_Lab01_TCPSocketIntro.ipynb)
    
**Roadmap for Future Additions**
1. Fix UI and disconnection issues and add disconnection alerts
2. Add exit game options
2. Add a chat functionality
3. Add basic cybersecurity functions
4. Add server browser
5. Add user profile viewer

**Retrospective**
* What went right
    * Players are able to maintain profiles
    * Players can connect to a host server and communicate with it
    * Players can create lobbies and successfully complete a game of battleship
* What could be improved on
    * The basic client-server architecture, while functional, is a little convoluted and difficult to work with
    * Some code duplication
    * Use a graphics / UI API instead of command prompt for the game's UI
        * Current version is clunky, cannot update the player while waiting for their input
        * It's also plain, could benefit from color usage
        * Code is currently more difficult to work with because it has to maintain the terminal instead of using API calls
    * Server API could be refactored to be more clear / return values which are more meaningful
    * Players can only exit the game right now by hitting CTRL+C, should have an exit option always

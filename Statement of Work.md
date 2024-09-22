# ONLINE BATTLESHIP by Ethan Bottoms
### Project Objective:
Create an online version of the game <em>Battleship</em>, giving the user client and server program which allow them to easily play the game with friends (who have <em>Python</em> installed...)

### Scope:
* Inclusions:
  * Client-server architecture, with the server handling game state and communication
  * Multiplayer, ability for multiple clients to connect and play simultaneously
  * Game logic of <em>Battleship</em> with alternating turns between players and handling of win-loss conditions
  * Error handling which deals with common errors, such as network failures, invalid input, or unexpected game states
  * Quality code writing:
    * Readability: The code should be well-formatted, use meaningful variable names, and include comments to explain complex logic
    * Modularity: The code should be organized into well-defined functions and modules to improve maintainability
    * Efficiency: The game should avoid unnecessary computations, resource-intensive operations, or unnecessary network round trips
    * Error Handling: The code should include basic error handling for connections, and gameplay

* Exclusions:
  * No sleek UI with graphics beyond Command-Line Interface capabilities
  * No executable version of the client or server components, all done with Command-Line using the <em>Python</em> programming language

### Deliverables:
* Working <em>Python</em> scripts for the clients and server
* Working and clean code for all functionality mentioned in the inclusions, with...
* Documentation which clearly explains how to use the scripts and the structure of the code
* Command-Line Interface-style presentation for the game

### Timeline:
* Key Milestones and Task Breakdown / Time estimates:
  * Sprint 1: Socket Programming, TCP Client-Server (Sept 22-Oct 06)
    * Basic Server Setup, including server-side application, mechanism for handling multiple clients, and logging of connection and disconnection events (3 hours)
    * Client-Side Connection, including developing client-side application that connects to the server, handles failures, and logs connection and disconnection (2 hours)
    * Simple Message Exchange, including basic communication protocol between server and clients (2 hours)
    * Basic Network-Related Error Handling, including logging of messages for debugging purposes (1 hour)
    * Testing and Debugging (2 hours)
    * Update README (< 1 hour)
   
  * Sprint 2: Develop Game Message Protocol, Manage Client connections (Oct 06-Oct 20)
    * Game Message Protocol Specification, defining stucture and format of messages exchanged between server and clients, including message types, data fields, expected responses (3 hours)
    * Server-Side Message Handling, implementing functions to recieve, parse, and process incoming messages from clients and appropriate handling, as well as list of clients connected and their game states (3 hours)
    * Client-Side Message Handling, implementing functions to send messages to the server and handle responses, parse server responses and update client's game state accordingly, provide feedback to user (2 hours)
    * Connection Management, implementing mechanisms to handle client connections and disconnections, notify clients when other clients join or leave (2 hours)
    * Update README (< 1 hour)
      
  * Sprint 3: Multi-player functionality, Synchronize state across clients. (Oct 20-Nov 03)
    * Game State Synchronization, implementation of mechanism to synchronize game states across all clients, including handling network latency and use of central server to broadcast game state (3 hours)
    * Client-Side Game Rendering, client-side logic to render the gamestate based on updates from server and ensure that all clients display the same game state (2 hours)
    * Turn-Based Gameplay, implementation of system which manages player turns and that only the current player can make moves (1 hour)
    * Player Identification, assigning of unique identifiers to each player to distinguish them and track their game state, including allowing players to choose unique usernames or avatars (2 hours)
    * (OPTIONAL) Chat Functionality, implementation of basic chat system to allow players to communicate with each other (1 hour)
    * Update README (< 1 hour)
      
  * Sprint 4: Game play, Game State (Nov 03-Nov 17)
    * Game State Management (continued), updating game state based on player moves and winning conditions, game board, relevant game settings (2 hours)
    * Input Handling, translating user input into game actions and validating that input to ensure it is within game's boundaries and rules (2 hours)
    * Winning Conditions, define them and implement logic, notify players when winner is determined or game ends (2 hours)
    * Game Over Handling, implement mechanisms to handle winners, new rounds, providing players with option to start a new game or quit (3 hours)
    * Update README (< 1 hour)
      
  * Sprint 5: Implement Error Handling and Testing (Nov 17-Dec 6)
    * Error Handling, implementation of mechanisms to catch and gracefully handle potential exceptions or unexpected situations, as wells as network errors, invalid input, and other potential issues (2 hours)
    * Integration Testing, testing of entire game system to ensure all components work together as expected and simulation of scenarios and edge cases to identify issues and bugs (3+ hours)
    * Security / Risk Evaluation, written list of security issues the game may have and how they can be addressed (< 1 hour)
    * Update README (< 1 hour)
      
### Technical Requirements:
* Hardware:
  * Basic computer with a connection to the internet

* Software:
  * Installation of `Python 3.12`
  * Standard Python `socket` and `threading` libraries
  * An OS which can run <em>Python</em>, such as <em>MacOS</em>, <em>Linux</em>, or <em>Windows</em>
  * Some form of Command-Line Interface (exists on the above-mentioned operating systems)

### Assumptions:
* This project assumes you have reliable access to the internet when running it on your machine
* You must have certain ports (listed at a later date) available on your machine or the ability to open ports to allow connectivity to the server and clients

### Communication Plan:

* All public updates done through Issues and corresponding Pull Requests with appropriate titles, descriptions, and limited scope changes which must be tested to make sure the update works properly and does not break other features before being merged with `Main`
* Consistent Releases made for each sprint which detail the updates explicitly, including a change log

### Additional Notes:

* I do not own the rights to <em>Battleship</em>, if it is not public domain. This is a student project.

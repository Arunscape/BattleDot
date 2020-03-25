# BattleDot

running it should be as simple as

  python main.py

This script requires python 3.8

I chose python, since I wanted to use a forgiving language, while learning how
to do something new. If I had infinite time, I would have chosen C++ if I had
to pick from the list, or Rust if I could choose my own language 🦀.
However, given the time frame, I decided not to use a language where I needed
to manage my memory.

Setting up a ring structure is something we've learned
in class, but implementing one is different than studying about it for an exam..

Also, I have not messed around with sockets before, so this was a cool learning
experience. I'm tempted to use sockets in my next hackathon project...

## What works:

- TCP socket communication between processes
- Playing with N players.
- New players can be added. One player starts the script and self-identifies as
  being the first player. The second player will specify the IP and port of
  the person that is to the left and right of them. In this case, they would
  enter player 1's IP and port twice. 

  From there, the 3rd, 4th... players can join if they know who is to the left
  and right of them.
- There is no master node, it's all peer-to-peer

# What does not work:

- Currently, when any node either loses (bomb was hit by the previous player)
  or if any node quits/drops its connections, the system fails to recover
  and continue playing the game. 
- There's basically no error handling
- The game will not play by itself, it requires user input.

## Implementation:

I chose to have his challenge implemented using multiple processes, using TCP
sockets. This *should* allow for the script to be run on different computers,
although I only tested it locally running on different ports in different
terminal windows. The script prompts for user input and does not run
automatically, because the losing case is not handled properly.
There is spaghetti code trying to take care of it, but in its current state,
when a node drops its connections or a player loses, each node in the system
ends up waiting on each other.

Setting up the board was pretty trivial. It was implemented as a class
that keeps track of its board, which spaces the user has guessed, and where the
player's ship is. There are helper functions for user input, making a move,
checking if the player lost, etc.

The rest of the script is honestly pretty messy. 
It's mostly hacked together, and could have been organized better.

Overall, how this is how it works:

1) The first player creates a server socket, and listens for connections.

Whenever a server receives a new connection, it spawns a thread which runs
an infinite while loop which responds to different requests.

The requests are sent with a fixed-length header which lets us know how many
bytes are to be received, instead of just using a large value.

The pickle library is used to serialize and deserialize the python objects
sent and received through the sockets.

2) A second player joins, specifying their left and right to be both player 1

  The new node creates two client connections, and tells the server(s) which
  side they need to update to point to the new node

   The game is started when the second player joins by sending a message which
   I called 'announce_turn'. The idea is to send this message around the ring.
   That way, when a player joins or leaves, the nodes will have their player
   maps updated

   When the 'announce_turn' message reaches the same node that sent it, that
   player is then allowed to make a move. It then sends the move to the node
   on the right. 

3) 3rd, 4th...n players can join when they wish to by also specifying the left
   and right nodes (I only tested with up to 4 players though)
  
  When a new player joins, new connections are made, and some are dropped.
  When a connection is dropped, the thread running the infinite event handling
  loop will cancel, since a new one is spawned to replace it. 

  Each player has a player map. Whenever a new node joins, it obtains the player
  map from the node on its left during setup.

  The idea was to refer to this map when a player's
  connection drops or they lose, so the nodes would be able to figure out how
  to recover.
  (I planned to implement a player losing and a player quitting at the same time)

  There is code which upon connection drop, or loss of the game will tell 
  adjacent nodes to attempt re-setup their left or right connections based on 
  the player map. I probably just missed something trivial, like looking up the
  wrong value in the dictionary or something...


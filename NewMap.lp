#const number_of_moves=4.
#const number_of_players=2.
#const number_of_resources=1.
#const dist_blocks_squared= (width/2) ** 2 .

terrain(water; mountains; flatland).


dim(0..width-1).
map((X,Y)) :- dim(X), dim(Y).

number_of_players { color(green;red) } number_of_players.
empty(none, empty).
resource(C, resource) :- color(C).
player(C, player) :- color(C).

% maps have at most one non-floor type 
0 { tile(T, S, C) : resource(C, S) } 1 :- map(T).
0 { tile(T, S, C) : empty(C, S) } 1 :- map(T).
0 { tile(T, S, C) : player(C, S)} 1 :- map(T).

1 { at((X, Y), Land) : terrain(Land)} 1 :- dim(X), dim(Y).

% Have correct player and resource count
:- { tile(T, resource, C) } != number_of_resources.
:- { tile(T, player, C) } != number_of_players. 

% No Duplicate players
:- tile(T1, player, C1), tile(T2, player, C2), C1==C2, T1!=T2.

% No Duplicate resources
:- tile(T1, resource, C1), tile(T2, resource, C2), C1==C2, T1!=T2.

% emptys don't overlap resources and characters
:- tile(T, empty, C1), tile(T, player, C2).
:- tile(T, empty, C1), tile(T, resource, C2).

% players do not start on resources or water or mountains
:- tile(T, player, C1), tile(T, resource, C2).
:- tile(T, player, C1), at(T, water).
:- tile(T, player, C1), at(T, mountains).

%players have a minimum starting distance between them
:- dim(X1),dim(Y1),dim(X2),dim(Y2),tile((X1,Y1), player, C1),tile((X2,Y2), player, C2), X1!=X2;Y1!=Y2 , (X2- X1)*2 + (Y2- Y1)*2 > dist_blocks_squared. 

% Define
step(0,1).
step(0,-1).
step(1,0).
step(-1,0).
step(1,1).
step(-1,-1).
step(1,-1).
step(-1,1).



add((X, Y), (DX, DY), (X+DX, Y+DY))
  :- dim(X), dim(Y), step(DX, DY).



adjacent(T1, T2, (DX,DY))
  :- add(T1, (DX,DY), T2).


2 { at(R1, water) : adjacent(R1,R2,Direction)} 4:- at(R2,water).


%players have atleast 1 non water terrain around them at the start
:- tile(T1, player, C1), at(T2, water), 1{adjacent(T1,T2,Direction)}.

2 { at(R1, water) : adjacent(R1,R2,Direction)} 4:- at(R2,water).


%amount of each terrain
:- not width*width/4 { at(T, water) } width*width/3.
:- not width*width/10 { at(T1, mountains) } width*width/10.

move(C1,S,E) :- map(S),map(E),tile(S,player,C1),adjacent(S,E,Direction),not at(E,water).

0 { player : move(C1,S,E) }.

#show tile/3.
#show at/2.
#show move/3.

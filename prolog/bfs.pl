% Define neighboring cells
neighbor(cell(X, Y), cell(X1, Y)) :- 
    X1 is X + 1.  % Right
neighbor(cell(X, Y), cell(X1, Y)) :- 
    X1 is X - 1.  % Left
neighbor(cell(X, Y), cell(X, Y1)) :- 
    Y1 is Y + 1.  % Down
neighbor(cell(X, Y), cell(X, Y1)) :- 
    Y1 is Y - 1.  % Up

% Check if the current cell is the destination
is_destination(cell(CurrentX, CurrentY), cell(DestX, DestY)) :-
    CurrentX =:= DestX,
    CurrentY =:= DestY.

% Find unvisited neighbors of the current cell
unvisited_neighbors(Current, Visited, UnvisitedNeighbors) :-
    findall(Neighbor, (neighbor(Current, Neighbor), \+ member(Neighbor, Visited)), UnvisitedNeighbors).

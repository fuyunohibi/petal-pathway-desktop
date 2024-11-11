:- dynamic wall/2.
:- dynamic grid_size/2.

% Manhattan distance heuristic
manhattan(cell(X1, Y1), cell(X2, Y2), Dist) :-
    Dist is abs(X1 - X2) + abs(Y1 - Y2).

% Define neighboring cells
neighbor(cell(X, Y), cell(X1, Y)) :- X1 is X + 1.
neighbor(cell(X, Y), cell(X1, Y)) :- X1 is X - 1.
neighbor(cell(X, Y), cell(X, Y1)) :- Y1 is Y + 1.
neighbor(cell(X, Y), cell(X, Y1)) :- Y1 is Y - 1.

% Check if a cell is valid (within grid and not a wall)
valid_cell(cell(X, Y)) :-
    grid_size(MaxX, MaxY),
    X >= 0, X < MaxX,
    Y >= 0, Y < MaxY,
    \+ wall(X, Y).

% A* neighbor discovery with calculated g and f scores
a_star_neighbors(Current, Destination, Neighbors) :-
    findall([Neighbor, GNew, F],
            (neighbor(Current, Neighbor),
             valid_cell(Neighbor),
             manhattan(Current, Neighbor, GNew),
             manhattan(Neighbor, Destination, H),
             F is GNew + H),
            Neighbors).

% A* step: find the optimal path from Current to Destination
a_star_step(Current, Destination, Path, Distance) :-
    a_star(Current, Destination, [], Path, 0, Distance).

% Recursive A* algorithm
a_star(Current, Destination, Visited, [Current|Visited], G, G) :-
    Current = Destination.

a_star(Current, Destination, Visited, Path, G, Distance) :-
    a_star_neighbors(Current, Destination, Neighbors),
    % Select the neighbor with the lowest F score (tie-breaking by G)
    sort(2, @=<, Neighbors, SortedNeighbors),
    member([Next, GNew, _], SortedNeighbors),
    \+ member(Next, Visited),
    GAccumulated is G + GNew,
    a_star(Next, Destination, [Current|Visited], Path, GAccumulated, Distance).

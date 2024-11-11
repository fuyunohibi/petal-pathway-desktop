:- dynamic wall/2.
:- dynamic grid_size/2.

% Define neighboring cells
neighbor(cell(X, Y), cell(X1, Y)) :- X1 is X + 1.
neighbor(cell(X, Y), cell(X1, Y)) :- X1 is X - 1.
neighbor(cell(X, Y), cell(X, Y1)) :- Y1 is Y + 1.
neighbor(cell(X, Y), cell(X, Y1)) :- Y1 is Y - 1.

% Check if a cell is valid (within grid bounds and not a wall)
valid_cell(cell(X, Y)) :-
    grid_size(MaxX, MaxY),
    X >= 0, X < MaxX,
    Y >= 0, Y < MaxY,
    \+ wall(X, Y).

% Entry point for Iterative Deepening DFS
iddfs(Start, Destination, Path, VisitedCells) :-
    writeln('Starting IDDFS...'),
    between(1, 100, DepthLimit),  % Arbitrary high limit to ensure a complete search
    dfs_with_limit(Start, Destination, DepthLimit, Path, VisitedCells),
    Path \= [],  % Ensure a path was found
    writeln('IDDFS Completed'), !.

% Depth-limited DFS
dfs_with_limit(Start, Destination, Limit, Path, VisitedCells) :-
    dfs_recursive(Start, Destination, [Start], [], Path, Limit, VisitedCells).

% Base case: if we reach the destination
dfs_recursive(Destination, Destination, Visited, AccVisitedCells, Path, _, FinalVisitedCells) :-
    reverse(Visited, Path),
    reverse(AccVisitedCells, FinalVisitedCells),
    writeln('Destination reached.').

% Recursive DFS step with depth limit and randomized neighbors
dfs_recursive(Current, Destination, Visited, AccVisitedCells, Path, Limit, FinalVisitedCells) :-
    Limit > 0,
    Current \= Destination,
    findall(Neighbor, (neighbor(Current, Neighbor), valid_cell(Neighbor), \+ member(Neighbor, Visited)), Neighbors),
    random_permutation(Neighbors, ShuffledNeighbors),  % Randomize neighbor order
    NewLimit is Limit - 1,
    explore_neighbors(ShuffledNeighbors, Destination, [Current | Visited], [Current | AccVisitedCells], Path, NewLimit, FinalVisitedCells).

% Explore each neighbor recursively within the depth limit
explore_neighbors([], _, Visited, VisitedCells, [], _, VisitedCells) :-
    writeln('Backtracking: no solution found from current path.').

explore_neighbors([Neighbor | Rest], Destination, Visited, AccVisitedCells, Path, Limit, FinalVisitedCells) :-
    dfs_recursive(Neighbor, Destination, Visited, AccVisitedCells, Path, Limit, FinalVisitedCells), !;
    explore_neighbors(Rest, Destination, Visited, AccVisitedCells, Path, Limit, FinalVisitedCells).

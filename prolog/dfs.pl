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

% Depth-First Search entry point
dfs(Start, Destination, Path, VisitedCells) :-
    writeln('Starting DFS...'),  % Debug: Starting DFS
    dfs_recursive(Start, Destination, [Start], VisitedCells, Path),
    writeln('DFS Completed').     % Debug: Completed DFS

% Base case: if we reach the destination
dfs_recursive(Destination, Destination, Visited, Visited, Path) :-
    reverse([Destination | Visited], Path),
    writeln('Destination reached.').

% Recursive DFS step
dfs_recursive(Current, Destination, Visited, VisitedCells, Path) :-
    Current \= Destination,
    neighbor(Current, Neighbor),
    valid_cell(Neighbor),
    \+ member(Neighbor, Visited),  % Only visit unvisited cells
    writeln(['Current:', Current, 'Moving to:', Neighbor]),  % Debug: Neighbor to visit
    dfs_recursive(Neighbor, Destination, [Neighbor | Visited], VisitedCells, Path).

% Backtracking if no solution is found
dfs_recursive(_, _, Visited, Visited, []) :-
    writeln('Backtracking: no solution found from current path.').

:- dynamic wall/2.
:- dynamic grid_size/2.

% Define neighboring cells
dfs_neighbor(cell(X, Y), cell(X1, Y)) :- 
    X1 is X + 1.  % Right
dfs_neighbor(cell(X, Y), cell(X1, Y)) :- 
    X1 is X - 1.  % Left
dfs_neighbor(cell(X, Y), cell(X, Y1)) :- 
    Y1 is Y + 1.  % Down
dfs_neighbor(cell(X, Y), cell(X, Y1)) :- 
    Y1 is Y - 1.  % Up

% Check if a cell is valid (within grid and not a wall)
dfs_valid_cell(cell(X, Y)) :-
    grid_size(MaxX, MaxY),
    X >= 0, X < MaxX,
    Y >= 0, Y < MaxY,
    \+ wall(X, Y).

% DFS step-by-step function
dfs_step(Current, Destination, Path, Visited, ToVisit) :-
    dfs_helper([Current], Destination, [], [], Visited, ToVisit, SolutionPath),
    (SolutionPath \= [] -> reverse(SolutionPath, Path); Path = []).

% Base case: if the current cell is the destination, return the path
dfs_helper([Destination | Path], Destination, VisitedAcc, _, Visited, [], [Destination | Path]) :-
    append([Destination | Path], VisitedAcc, Visited).

% Recursive DFS search with step-by-step functionality
dfs_helper([Current | Stack], Destination, VisitedAcc, _, Visited, ToVisit, SolutionPath) :-
    % Find all valid, unvisited neighbors
    findall(Neighbor,
            (dfs_neighbor(Current, Neighbor),
             dfs_valid_cell(Neighbor),
             \+ member(Neighbor, VisitedAcc),
             \+ member(Neighbor, Stack)),
            Neighbors),
    % Update stack and visited cells
    append(Neighbors, Stack, UpdatedStack),
    append(VisitedAcc, [Current], UpdatedVisited),
    ToVisit = Neighbors,  % Return neighbors to visit in this step
    dfs_helper(UpdatedStack, Destination, UpdatedVisited, Neighbors, Visited, _, SolutionPath).

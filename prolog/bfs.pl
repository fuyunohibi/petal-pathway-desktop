:- dynamic wall/2.
:- dynamic grid_size/2.

% Define neighboring cells
neighbor(cell(X, Y), cell(X1, Y)) :- 
    X1 is X + 1.  % Right
neighbor(cell(X, Y), cell(X1, Y)) :- 
    X1 is X - 1.  % Left
neighbor(cell(X, Y), cell(X, Y1)) :- 
    Y1 is Y + 1.  % Down
neighbor(cell(X, Y), cell(X, Y1)) :- 
    Y1 is Y - 1.  % Up

% Check if a cell is valid (within grid and not a wall)
valid_cell(cell(X, Y)) :-
    grid_size(MaxX, MaxY),
    X >= 0, X < MaxX,
    Y >= 0, Y < MaxY,
    \+ wall(X, Y).

% BFS with step-by-step search, returns Path only when Destination is found
bfs_step(Start, Destination, Path, Visited, ToVisit) :-
    bfs_helper([[Start]], Destination, [Start], [], Visited, ToVisit, SolutionPath),
    (SolutionPath \= [] -> reverse(SolutionPath, Path); Path = []).

% If the first path in the queue reaches the destination
bfs_helper([[Destination | Rest] | _], Destination, _, VisitedAcc, VisitedAcc, [], [Destination | Rest]).

% Continue searching without returning the final path immediately
bfs_helper([CurrentPath | Queue], Destination, VisitedAcc, ToVisitAcc, Visited, ToVisit, SolutionPath) :-
    CurrentPath = [Current | _],
    findall([Neighbor, Current | CurrentPath],
            (neighbor(Current, Neighbor),
             valid_cell(Neighbor),
             \+ member(Neighbor, VisitedAcc),
             \+ member(Neighbor, ToVisitAcc)),
            NewPaths),
    maplist(head_of_path, NewPaths, NewNodes),
    append(VisitedAcc, [Current], UpdatedVisited),
    append(ToVisitAcc, NewNodes, UpdatedToVisit),
    append(Queue, NewPaths, UpdatedQueue),
    bfs_helper(UpdatedQueue, Destination, UpdatedVisited, UpdatedToVisit, Visited, ToVisit, SolutionPath).

% Helper predicate to get the head of a path
head_of_path([Node | _], Node).

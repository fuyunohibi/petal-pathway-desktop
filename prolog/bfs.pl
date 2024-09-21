:- dynamic wall/2.
:- dynamic grid_size/2.

% Base BFS definition
bfs(Start, End, Path) :-
    bfs([[Start]], End, [Start], ReversedPath),
    reverse(ReversedPath, Path).

% If the first path in the queue reaches the end, we have found our solution.
bfs([[End | RestOfPath] | _], End, _, [End | RestOfPath]).

% Continue searching
bfs([CurrentPath | Queue], End, Visited, Solution) :-
    CurrentPath = [CurrentNode | _],
    findall([NextNode, CurrentNode | RestOfPath],
            (neighbor(CurrentNode, NextNode),
             \+ member(NextNode, Visited),
             CurrentPath = [CurrentNode | RestOfPath]),
            NewPaths),
    maplist(head_of_path, NewPaths, NewNodes),
    append(Visited, NewNodes, UpdatedVisited),
    append(Queue, NewPaths, NewQueue),
    bfs(NewQueue, End, UpdatedVisited, Solution).

% Helper predicate to get the head of a path
head_of_path([Node | _], Node).

% Timeout wrapper for BFS
bfs_with_timeout(Start, End, Path, TimeLimit) :-
    call_with_time_limit(TimeLimit, bfs(Start, End, Path)).

% Neighbor predicate with wall and boundary checks
neighbor((X, Y), (NX, Y)) :-
    NX is X + 1,
    valid_cell(NX, Y).
neighbor((X, Y), (X, NY)) :-
    NY is Y + 1,
    valid_cell(X, NY).
neighbor((X, Y), (PX, Y)) :-
    PX is X - 1,
    valid_cell(PX, Y).
neighbor((X, Y), (X, PY)) :-
    PY is Y - 1,
    valid_cell(X, PY).

% Check if a cell is valid (inside grid and not a wall)
valid_cell(X, Y) :-
    X >= 0,
    Y >= 0,
    grid_size(MaxX, MaxY),
    X < MaxX,
    Y < MaxY,
    \+ wall(X, Y).

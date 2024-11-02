% Declare dynamic predicates for grid size, path, and wall cells
:- dynamic grid_size/2.
:- dynamic path/2.
:- dynamic wall/2.

% Check if a cell is within the grid boundaries
within_bounds(X, Y) :-
    grid_size(MaxX, MaxY),
    X >= 0, X < MaxX,
    Y >= 0, Y < MaxY.

% Mark a cell as part of the path
mark_path(X, Y) :-
    within_bounds(X, Y),
    \+ wall(X, Y),       % Ensure it is not a wall
    \+ path(X, Y),      % Ensure it is not already part of the path
    assert(path(X, Y)).

% Mark a cell as a wall
mark_wall(X, Y) :-
    within_bounds(X, Y),
    \+ path(X, Y),       % Ensure it is not part of the path
    assert(wall(X, Y)).

% Generate maze recursively, starting from (X, Y)
generate_maze(X, Y) :-
    mark_path(X, Y),             % Mark the current cell as part of the path
    findall((DX, DY),            % Generate possible directions (right, left, down, up)
            member((DX, DY), [(1, 0), (-1, 0), (0, 1), (0, -1)]),
            Directions),
    random_permutation(Directions, ShuffledDirections),  % Randomize the order of directions
    try_directions(X, Y, ShuffledDirections).            % Attempt to move in each direction

% Attempt to move in each direction from the list
try_directions(_, _, []).
try_directions(X, Y, [(DX, DY) | Rest]) :-
    NX is X + DX * 2,
    NY is Y + DY * 2,
    within_bounds(NX, NY),
    \+ path(NX, NY),              % Proceed only if the target cell is not already a path
    LinkX is X + DX,
    LinkY is Y + DY,
    mark_path(LinkX, LinkY),      % Mark the cell between as part of the path
    generate_maze(NX, NY),        % Recursively generate the maze from the new cell
    try_directions(X, Y, Rest).   % Continue with the remaining directions

% Initialize maze with all cells as walls before generating paths
initialize_maze :-
    grid_size(MaxX, MaxY),
    forall(between(0, MaxX, X),
           forall(between(0, MaxY, Y),
                  mark_wall(X, Y))).

% Entry point to generate a full maze
create_maze(StartX, StartY) :-
    initialize_maze,
    generate_maze(StartX, StartY).

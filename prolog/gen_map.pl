% Define grid size
:- dynamic(grid_size/2).
:- dynamic(path/2).
:- dynamic(visited/2).

% Define directions for maze movement
direction(1, 0).
direction(-1, 0).
direction(0, 1).
direction(0, -1).

% Randomly shuffle directions
shuffle_directions(Shuffled) :-
    findall((DX, DY), direction(DX, DY), Directions),
    random_permutation(Directions, Shuffled).

% Start maze generation from (X, Y)
generate_maze(X, Y) :-
    retractall(path(_, _)),
    retractall(visited(_, _)),
    assertz(visited(X, Y)),
    mark_path(X, Y), % Mark the starting point
    generate_maze_recursive(X, Y).

% Recursive maze generation
generate_maze_recursive(X, Y) :-
    % Shuffle directions each time we enter a new cell
    shuffle_directions(Directions),
    generate_paths(X, Y, Directions).

% Attempt to generate paths in shuffled directions
generate_paths(_, _, []) :- !.  % Stop if there are no more directions
generate_paths(X, Y, [(DX, DY) | Rest]) :-
    NewX is X + DX * 2,
    NewY is Y + DY * 2,
    grid_size(MaxX, MaxY),

    % Check if within bounds and not visited
    within_bounds(NewX, NewY, MaxX, MaxY),
    \+ visited(NewX, NewY),

    % Mark path cells and connecting cell
    LinkX is X + DX,
    LinkY is Y + DY,
    mark_path(LinkX, LinkY),
    mark_path(NewX, NewY),
    assertz(visited(NewX, NewY)),

    % Recursively generate paths from the new cell
    generate_maze_recursive(NewX, NewY);

    % If direction is not feasible, try the next one
    generate_paths(X, Y, Rest).

% Check if a position is within the grid bounds
within_bounds(X, Y, MaxX, MaxY) :-
    X >= 0, X < MaxX,
    Y >= 0, Y < MaxY.

% Mark a cell as part of the path
mark_path(X, Y) :-
    assertz(path(X, Y)).
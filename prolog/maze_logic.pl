% Define grid size
grid_size(X, Y).

% Define directions
direction(1, 0).
direction(-1, 0).
direction(0, 1).
direction(0, -1).

% Generate random directions
shuffle_directions(Shuffled) :-
    findall((DX, DY), direction(DX, DY), Directions),
    random_permutation(Directions, Shuffled).

% Maze generation logic
generate_maze(X, Y) :-
    shuffle_directions(Directions),
    generate_maze_recursive(X, Y, Directions).

generate_maze_recursive(X, Y, []).
generate_maze_recursive(X, Y, [(DX, DY) | Rest]) :-
    NewX is X + DX * 2,
    NewY is Y + DY * 2,
    % Add checks for boundaries and wall status here
    generate_maze_recursive(NewX, NewY, Rest).

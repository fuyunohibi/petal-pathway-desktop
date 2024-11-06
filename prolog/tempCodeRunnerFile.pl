% Dynamic predicates
:- dynamic wall/2, path/2, grid_size/2, visited/2.

% Initialize the maze by making all cells walls
initialize_maze :-
    writeln('Initializing all cells as walls...'),  % Debug
    retractall(wall(_, _)),
    retractall(path(_, _)),
    retractall(visited(_, _)),
    grid_size(Width, Height),
    initialize_walls(0, 0, Width, Height).

initialize_walls(X, Y, Width, Height) :-
    (X < Width, Y < Height ->
        assertz(wall(X, Y)),
        (X + 1 >= Width ->
            NewX is 0,
            NewY is Y + 1
        ;
            NewX is X + 1,
            NewY = Y
        ),
        initialize_walls(NewX, NewY, Width, Height)
    ; true).  % Finish when out of bounds

% Define possible directions (right, left, down, up)
direction(1, 0).
direction(-1, 0).
direction(0, 1).
direction(0, -1).

% Get all directions
get_directions(Directions) :-
    findall([DX, DY], direction(DX, DY), Dirs),
    random_permutation(Dirs, Directions).

% Check if position is within grid bounds
in_bounds(X, Y) :-
    grid_size(Width, Height),
    X >= 0, X < Width,
    Y >= 0, Y < Height.

% Mark a cell as visited
mark_visited(X, Y) :-
    assertz(visited(X, Y)).

% Check if a cell has been visited
is_visited(X, Y) :-
    visited(X, Y).

% Main maze generation predicate
generate_maze(X, Y) :-
    % Mark starting position as path and visited
    writeln(['Generating maze from starting point:', X, Y]),  % Debug
    retract(wall(X, Y)),
    assertz(path(X, Y)),
    mark_visited(X, Y),
    
    % Get shuffled directions and process them
    get_directions(Directions),
    writeln(['Processing directions from:', X, Y]),  % Debug
    process_directions(X, Y, Directions).

% Process directions for maze generation
process_directions(_, _, []).  % Base case - no more directions
process_directions(X, Y, [[DX, DY]|Rest]) :-
    % Calculate new position (2 steps away)
    NewX is X + (DX * 2),
    NewY is Y + (DY * 2),
    
    % Try to carve path in this direction
    (can_carve_path(NewX, NewY) ->
        carve_path(X, Y, DX, DY, NewX, NewY),
        writeln(['Carved path to:', NewX, NewY]),  % Debug message
        generate_maze(NewX, NewY)
    ; writeln(['Cannot carve path to:', NewX, NewY])),  % Debug message if carving fails
    
    % Continue with remaining directions even after success
    process_directions(X, Y, Rest).

% Check if we can carve a path to the target position
can_carve_path(X, Y) :-
    in_bounds(X, Y),
    wall(X, Y),
    \+ is_visited(X, Y).

% Carve a path by marking cells as path
carve_path(X, Y, DX, DY, NewX, NewY) :-
    % Calculate linking cell position
    LinkX is X + DX,
    LinkY is Y + DY,
    
    % Mark cells as path
    retract(wall(LinkX, LinkY)),
    assertz(path(LinkX, LinkY)),
    mark_visited(LinkX, LinkY),
    
    retract(wall(NewX, NewY)),
    assertz(path(NewX, NewY)),
    mark_visited(NewX, NewY).

% Helper predicate to check cells
is_path(X, Y) :- path(X, Y).
is_wall(X, Y) :- wall(X, Y).

% Cleanup predicate
cleanup_maze :-
    writeln('Cleaning up visited cells...'),  % Debug message
    retractall(visited(_, _)),
    writeln('Cleanup complete.').  % Debug message

% Main entry point with cleanup
generate_maze_with_cleanup(X, Y) :-
    cleanup_maze,
    generate_maze(X, Y).

:- dynamic distance/3.      % distance(X, Y, D)
:- dynamic previous/4.      % previous(X, Y, PrevX, PrevY)
:- dynamic in_queue/2.      % in_queue(X, Y)
:- dynamic visited/2.       % visited(X, Y)
:- dynamic to_visit/2.      % to_visit(X, Y)
:- dynamic grid_size/2.     % grid_size(Width, Height)
:- dynamic wall/2.          % wall(X, Y)

init_dijkstra(StartX, StartY) :-
    retractall(distance(_, _, _)),
    retractall(previous(_, _, _, _)),
    retractall(in_queue(_, _)),
    retractall(visited(_, _)),
    retractall(to_visit(_, _)),
    
    % Set initial distance for all cells to infinity (99999)
    grid_size(W, H),
    forall(
        (between(0, W, X), between(0, H, Y)),
        assertz(distance(X, Y, 99999))
    ),
    
    % Set start cell distance to 0
    retract(distance(StartX, StartY, _)),
    assertz(distance(StartX, StartY, 0)),
    assertz(in_queue(StartX, StartY)).

dijkstra_with_visualization((StartX, StartY), (EndX, EndY), Path, VisitedCells, Timeout) :-
    % Initialize the Dijkstra process
    init_dijkstra(StartX, StartY),
    
    % Run the algorithm with timeout
    catch(
        call_with_time_limit(Timeout, dijkstra_loop(StartX, StartY, EndX, EndY, Path, VisitedCells)),
        time_limit_exceeded,
        fail
    ).

dijkstra_loop(StartX, StartY, EndX, EndY, Path, VisitedCells) :-
    % Continue until the queue is empty or destination is reached
    findall((Dist, X, Y), (in_queue(X, Y), distance(X, Y, Dist)), Queue),
    Queue \= [],

    % Remove the current cell from the queue and mark it as visited
    retract(in_queue(CurrentX, CurrentY)),
    assertz(visited(CurrentX, CurrentY)),

    % Check if we have reached the destination
    (CurrentX = EndX, CurrentY = EndY ->
        construct_path(EndX, EndY, Path),
        findall((VX, VY), visited(VX, VY), VisitedCells)
    ;
        % Update neighbors and continue the loop
        forall(neighbor(CurrentX, CurrentY, NX, NY), process_neighbor(CurrentX, CurrentY, NX, NY)),
        dijkstra_loop(StartX, StartY, EndX, EndY, Path, VisitedCells)
    ).

% Find the cell with the minimum distance in the queue
min_distance_cell([(Dist, X, Y)|Queue], (MinDist, MinX, MinY)) :-
    min_distance_cell_helper(Queue, (Dist, X, Y), (MinDist, MinX, MinY)).

min_distance_cell_helper([], (Dist, X, Y), (Dist, X, Y)).
min_distance_cell_helper([(D, X, Y)|Queue], (MinD, MinX, MinY), Min) :-
    (D < MinD -> min_distance_cell_helper(Queue, (D, X, Y), Min)
    ; min_distance_cell_helper(Queue, (MinD, MinX, MinY), Min)
    ).

% Process each neighboring cell
process_neighbor(CurrentX, CurrentY, NX, NY) :-
    distance(CurrentX, CurrentY, CurrentDist),
    NewDist is CurrentDist + 1,  % Assuming uniform distance between cells
    (distance(NX, NY, NeighborDist), NewDist < NeighborDist ->
        retract(distance(NX, NY, _)),
        assertz(distance(NX, NY, NewDist)),
        retractall(previous(NX, NY, _, _)),
        assertz(previous(NX, NY, CurrentX, CurrentY)),
        (not(visited(NX, NY)), not(in_queue(NX, NY)) -> assertz(in_queue(NX, NY)), assertz(to_visit(NX, NY)) ; true)
    ; true).

% Define neighboring cells
neighbor(X, Y, NX, NY) :-
    grid_size(W, H),
    member([DX, DY], [[0, 1], [1, 0], [0, -1], [-1, 0]]),
    NX is X + DX,
    NY is Y + DY,
    NX >= 0, NX < W,
    NY >= 0, NY < H,
    \+ wall(NX, NY).

% Construct the path by backtracking from the destination
construct_path(X, Y, [(X, Y)|Path]) :-
    previous(X, Y, PrevX, PrevY),
    construct_path(PrevX, PrevY, Path).
construct_path(_, _, []).

% Define a default predicate to retrieve distances
get_distance(X, Y, D) :-
    (distance(X, Y, D) -> true ; D = 99999).
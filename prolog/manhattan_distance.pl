:- dynamic wall/2.
:- dynamic grid_size/2.

% Manhattan distance predicate between two cells
manhattan_distance(cell(X1, Y1), cell(X2, Y2), Distance) :-
    Distance is abs(X1 - X2) + abs(Y1 - Y2).

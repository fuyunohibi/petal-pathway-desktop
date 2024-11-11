from queue import PriorityQueue
from tkinter import ttk,StringVar,messagebox
import tkinter
from tkinter.constants import  N, RIGHT
from ttkthemes import ThemedTk
from collections import deque
import time
import random
from pyswip import Prolog
import pyswip
import threading
import re  # For regular expressions to parse the string
import os

class MainPage(ttk.Frame):
    
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)
        self.frame.pack(padx=2)

        self.menu = MenuBar(self.frame)
        self.menu.pack(side=RIGHT,anchor=N,pady=50)

        self.grid = CellGrid(self.frame, 30, 30, 30)
        self.grid.pack(padx=20,pady=20)
        

class MenuBar(ttk.LabelFrame):# buttons for startPoint,endPoint,wall
    def __init__(self,master):
        super().__init__(master, text = "Menu bar")
        self.master = master
        
        self.algorithmsList = ["A*(A-Star) Pathfinding","Dijkstra's Shortest path Algorithm","Depth First Search","Breadth First Search"]
        self.selected_algo = StringVar(self)
        self.selected_algo.set(self.algorithmsList[0])
        self.algorithmSelector = ttk.OptionMenu(self,self.selected_algo,"A*(A-Star) Pathfinding",*self.algorithmsList,command=self.get_selected_algo)
        self.algorithmSelector.config(width=50)
        self.algorithmSelector.pack(pady=20,padx=20)

        self.start_button = ttk.Button(self,text="Start",command=self.call_start_algo)
        self.start_button.pack(pady = 20)

        self.clear_button = ttk.Button(self,text="Clear",command = self.call_clear_grid)
        self.clear_button.pack(pady = 20)

        self.generate_maze_button = ttk.Button(self,text = "Generate Maze",command = self.call_generate_maze)
        self.generate_maze_button.pack(pady = 20)
    def get_selected_algo(self,choice):
        print(self.selected_algo.get())

    def call_start_algo(self):
        pathfinding_visaul.grid.start_algo(self.selected_algo.get())

    def call_clear_grid(self):
        pathfinding_visaul.grid.clear_grid()
    
    def call_generate_maze(self):
        pathfinding_visaul.grid.make_all_wall()
        pathfinding_visaul.grid.generate_maze(0,0)


class Cell():

    def __init__(self, master, x, y, size):
        """ Constructor of the object called by Cell(...) """
        self.master = master
        self.abs = x
        self.ord = y
        self.size= size
        self.g = float('inf') #number of steps from start for A*
        self.f = float('inf')      #f = g + hueristic(manhattan distance)
        self.d = float('inf') #distance from start point for Dijkstra algo
        self.color = 'white'
        self.neighbor = [] #keeps adjacent cells
        self.prev = None #for reconstructing path
        self.start = False
        self.dest =False


    def make_start(self):
        """"mark a cell as starting point"""
        self.color = "yellow"
        self.start = True
        self.draw()
    def is_start(self):
        return self.start
    def make_dest(self):
        """"mark a cell as destination point"""
        self.color = 'blue'
        self.dest = True
        self.draw()
    def is_dest(self):
        return self.dest
    def make_wall(self):
        """"mark as wall/obstacle(cannot pass)"""
        self.color = 'green'
        self.draw()
    def is_wall(self):
        return self.color == 'green'
    def make_empty(self):
        self.color = 'white'
        self.draw()
    def is_empty(self):
        return self.color == 'white'
    def make_visited(self):
        self.color = "orange"
        self.draw()
    def is_visited(self):
        return self.color == 'orange'
    def make_path(self):
        self.color = "red"
        self.draw()
    def is_path(self):
        return self.color == 'red'
    def make_to_visit(self):
        self.color = "magenta"
        self.draw()
    def is_to_visit(self):
        return self.color == 'magenta'

    def draw(self):
        """ order to the cell to draw its representation on the canvas """
        if self.master != None :
            fill = self.color
            outline = 'black'
            xmin = self.abs * self.size
            xmax = xmin + self.size
            ymin = self.ord * self.size
            ymax = ymin + self.size

            self.master.create_rectangle(xmin, ymin, xmax, ymax, fill = fill, outline = outline)


class CellGrid(tkinter.Canvas):
    def __init__(self,master, rowNumber, columnNumber, cellSize, *args, **kwargs):
        tkinter.Canvas.__init__(self, master, width = cellSize * columnNumber , height = cellSize * rowNumber, *args, **kwargs)
        self.rowNumber = rowNumber
        self.columnNumber = columnNumber
        self.cellSize = cellSize
        self.choose_start = False
        self.choose_dest = False
        self.grid = []
        self.start = []
        self.dest = []
        for row in range(rowNumber):

            line = []
            for column in range(columnNumber):
                line.append(Cell(self, column, row, cellSize))

            self.grid.append(line)

        #memorize the cells that have been modified to avoid many switching of state during mouse motion.
        self.switched = []

        #bind click action
        self.bind("<Button-1>", self.handleMouseClick)  
        #bind moving while clicking
        self.bind("<B1-Motion>", self.handleMouseMotion)
        #bind release button action - clear the memory of midified cells.
        self.bind("<ButtonRelease-1>", lambda event: self.switched.clear())

        self.draw()

                # Initialize Prolog engine and consult bfs.pl
        self.prolog = Prolog()
        try:
            manhattan_distance_path = os.path.join(os.path.dirname(__file__), '../prolog/manhattan_distance.pl')
            self.prolog.consult(manhattan_distance_path)
            # Consult bfs.pl
            bfs_path = os.path.join(os.path.dirname(__file__), '../prolog/bfs.pl')
            self.prolog.consult(bfs_path)
            # Consult dfs.pl
            dfs_path = os.path.join(os.path.dirname(__file__), '../prolog/dfs.pl')
            self.prolog.consult(dfs_path)
            dijkstra_path = os.path.join(os.path.dirname(__file__), '../prolog/dijkstra.pl')
            self.prolog.consult(dijkstra_path)
            a_star_path = os.path.join(os.path.dirname(__file__), '../prolog/a_star.pl')
            self.prolog.consult(a_star_path)
            gen_map = os.path.join(os.path.dirname(__file__), '../prolog/gen_map.pl')
            self.prolog.consult(gen_map)
            print("Prolog files consulted successfully.")
        except Exception as e:
            print(f"Error consulting Prolog files: {e}")

    def unbind_click(self):
        #unbind to disable clicking while running
        self.unbind("<Button-1>")  
        self.unbind("<B1-Motion>")
        self.unbind("<ButtonRelease-1>")

    def draw(self):
        for row in self.grid:
            for cell in row:
                cell.draw()

    def _eventCoords(self, event):
        row = int(event.y / self.cellSize)
        column = int(event.x / self.cellSize)
        return row, column

    def handleMouseClick(self, event):
        row, column = self._eventCoords(event)
        cell = self.grid[row][column]
        
        if not self.choose_start:
            cell.make_start()
            self.start = [cell.ord,cell.abs]
            self.choose_start = True
        elif not self.choose_dest:
            cell.make_dest()
            self.dest = [cell.ord,cell.abs]
            self.choose_dest = True

        if(self.choose_start and self.choose_dest ):
            if not (cell.is_wall() or cell.is_start() or cell.is_dest() ):
                cell.make_wall()
            #add the cell to the list of cell switched during the click
            elif cell.is_wall():
                cell.make_empty()
            self.switched.append(cell)
        cell.draw()

    def handleMouseMotion(self, event):
        row, column = self._eventCoords(event)
        if row > self.rowNumber or row < 0:
            raise IndexError
        if column > self.columnNumber or column < 0:
            raise IndexError
        cell = self.grid[row][column]
        if (not self.choose_dest) and not self.choose_start:
            return -1
        if cell not in self.switched:
            if cell.is_empty():
                cell.make_wall()
            elif not (cell.is_dest() or cell.is_start()):
                cell.make_empty()
            cell.draw()
            self.switched.append(cell)

    def make_all_wall(self):
        self.clear_grid()
        for row in self.grid:
            for cell in row:
                cell.make_wall()

    def generate_maze(self, start_x, start_y):
            self.clear_grid()  # Clear the grid to start with a blank slate

            try:
                # Set up Prolog by clearing existing facts
                self.prolog.retractall('grid_size(_, _)')
                self.prolog.retractall('wall(_, _)')
                self.prolog.retractall('path(_, _)')
                self.prolog.retractall('visited(_, _)')

                # Define grid dimensions in Prolog
                self.prolog.assertz(f"grid_size({self.columnNumber}, {self.rowNumber})")

                # Initialize maze generation in Prolog
                print("Initializing maze...")
                result = list(self.prolog.query(f"generate_maze({start_x}, {start_y})."))

                if not result:
                    print("Maze generation in Prolog did not return any result.")
                    messagebox.showerror("Error", "Maze generation failed.")
                    return

                print("Maze generation completed. Retrieving results...")

                # First mark all cells as walls for a clear visualization
                for row in self.grid:
                    for cell in row:
                        cell.make_wall()
                        app.update_idletasks()

                # Retrieve paths from Prolog to visualize in Python
                path_cells = list(self.prolog.query("path(X, Y)."))
                print(f"Total paths generated: {len(path_cells)}")

                # Display paths from Prolog results
                for path in path_cells:
                    x, y = path["X"], path["Y"]
                    if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[0]):
                        self.grid[y][x].make_empty()
                        app.update_idletasks()
                        time.sleep(0.00001)

                print("Maze generation visualization completed.")
                messagebox.showinfo("Success", "Maze generation completed successfully!")

            except Exception as e:
                print(f"Error during Prolog maze generation: {e}")
                messagebox.showerror("Error", f"Prolog maze generation failed: {str(e)}")

            finally:
                # Clean up Prolog database
                self.prolog.query("cleanup_maze.")

    def start_algo(self,algo):
        if self.choose_start and self.choose_dest:
            print("Started",algo)
            print("start = [{}][{}] end = [{}][{}]".format(self.start[0],self.start[1],self.dest[0],self.dest[1]))
            self.set_neighbors()
            if(algo == "Breadth First Search"):
                self.bfs()
            elif algo =="Depth First Search":
                self.dfs()
            elif algo == "A*(A-Star) Pathfinding":
                self.a_star()
            elif algo == "Dijkstra's Shortest path Algorithm":
                self.dijkstra()
        else:
            messagebox.showerror("Error","Please choose start and destination point first!")

    def clear_grid(self):
        
        for row in self.grid:
            for cell in row:
                cell.make_empty()
                cell.start = False
                cell.end = False
                cell.h = 0;
                cell.g = float('inf')
                cell.f = float('inf')
                cell.d = float('inf')

        self.choose_start = False
        self.choose_dest = False
        self.bind("<Button-1>", self.handleMouseClick)  
        #bind moving while clicking
        self.bind("<B1-Motion>", self.handleMouseMotion)
        #bind release button action - clear the memory of midified cells.
        self.bind("<ButtonRelease-1>", lambda event: self.switched.clear())
        self.draw()

    def clear_prev_algo(self):

        for row in self.grid:
            for cell in row:
                if cell.is_visited() or cell.is_to_visit() or cell.is_path():
                    cell.make_empty()
                    cell.start = False
                    cell.end = False
                cell.h = 0;
                cell.g = float('inf')
                cell.f = float('inf')
                cell.d = float('inf')

    def set_neighbors(self):
        for row in self.grid:
            for cell in row:
                cell.neighbors = []
                if cell.is_wall():
                    continue
                if cell.abs < self.columnNumber -1 and not(self.grid[cell.ord][cell.abs+1].is_wall()):
                    cell.neighbors.append(self.grid[cell.ord][cell.abs+1])
                
                if cell.abs > 0 and not (self.grid[cell.ord][cell.abs-1].is_wall()):
                    cell.neighbors.append(self.grid[cell.ord][cell.abs-1])
                
                if cell.ord < self.rowNumber -1 and not(self.grid[cell.ord+1][cell.abs].is_wall()):
                    cell.neighbors.append(self.grid[cell.ord+1][cell.abs])
                
                if cell.ord > 0 and not (self.grid[cell.ord-1][cell.abs].is_wall()):
                    cell.neighbors.append(self.grid[cell.ord -1][cell.abs])
    
    def show_path(self,cell):
        curr = cell
        count = 0
        while (not curr.is_start()):
            count += 1
            prev = curr.prev
            prev.make_path()
            curr = prev
        return count

    def bfs(self):
        self.clear_prev_algo()
        self.unbind_click()
        
        start = f"cell({self.start[1]}, {self.start[0]})"
        destination = f"cell({self.dest[1]}, {self.dest[0]})"

        # Ensure Prolog has the grid and wall data
        self.prolog.retractall('grid_size(_, _)')
        self.prolog.assertz(f"grid_size({self.columnNumber}, {self.rowNumber})")

        self.prolog.retractall('wall(_, _)')
        for row in self.grid:
            for cell in row:
                if cell.is_wall():
                    x, y = cell.abs, cell.ord
                    self.prolog.assertz(f"wall({x}, {y})")

        # Initialize BFS loop to process step-by-step visualization
        solution_found = False
        queue = [[start]]  # Start the queue with the starting cell

        while not solution_found:
            # Prolog query for each BFS step
            query = f"bfs_step({start}, {destination}, Path, Visited, ToVisit)"
            result = list(self.prolog.query(query))
            print(result)

            if result:
                result = result[0]

                # Display each cell in ToVisit
                to_visit = result.get('ToVisit', [])
                for cell_str in to_visit:
                    match = re.match(r"cell\((\d+),\s*(\d+)\)", cell_str)
                    if match:
                        x, y = int(match.group(1)), int(match.group(2))
                        cell = self.grid[y][x]
                        if not cell.is_start() and not cell.is_dest():
                            cell.make_to_visit()
                            app.update_idletasks()
                            time.sleep(0.001)  # Short delay for visualization

                # Display each cell in Visited
                visited = result.get('Visited', [])
                for cell_str in visited:
                    match = re.match(r"cell\((\d+),\s*(\d+)\)", cell_str)
                    if match:
                        x, y = int(match.group(1)), int(match.group(2))
                        cell = self.grid[y][x]
                        if not cell.is_start() and not cell.is_dest():
                            cell.make_visited()
                            app.update_idletasks()
                            time.sleep(0.001)  # Short delay for visualization

                # Check if the final Path is found (destination reached)
                path = result.get('Path', [])
                if path:
                    # Visualize the found path step-by-step
                    for cell_str in path:
                        match = re.match(r"cell\((\d+),\s*(\d+)\)", cell_str)
                        if match:
                            x, y = int(match.group(1)), int(match.group(2))
                            cell = self.grid[y][x]
                            if not cell.is_start() and not cell.is_dest():
                                cell.make_path()
                                app.update_idletasks()
                                time.sleep(0.001)  # Longer delay for path visualization
                    solution_found = True
                    messagebox.showinfo("Path Found", f"Cells Discovered: {len(visited)}\nDistance to destination: {len(path)-1}")
                    break
            else:
                messagebox.showinfo("Path Not Found", "No solution")
                break

    def dfs(self):
        self.clear_prev_algo()
        self.unbind_click()
        discovered = 0

        que = deque()
        que.append(self.grid[self.start[0]][self.start[1]])
        visited = {que[0]}
        while(len(que) > 0):
            cell = que.pop()
            discovered += 1
            cell.draw()
            if cell.ord == self.dest[0] and cell.abs == self.dest[1]:
                steps = self.show_path(cell)
                self.grid[self.start[0]][self.start[1]].make_start()
                self.grid[self.dest[0]][self.dest[1]].make_dest()
                messagebox.showinfo("path found","Cells Discoverd: {}\nDistance to destination: {}".format(discovered,steps))
                
                return

            for neighbor in cell.neighbors:
                if neighbor in visited:
                    continue
                else:
                    neighbor.prev = cell
                    que.append(neighbor)
                    visited.add(neighbor)
                    neighbor.make_to_visit()
            if(not cell.is_start()):
                cell.make_visited()
                app.update_idletasks()
                time.sleep(0.001)
        messagebox.showinfo("Path not found","No solution")

    def dfss(self):
        self.clear_prev_algo()
        self.unbind_click()

        start = f"cell({self.start[1]}, {self.start[0]})"
        destination = f"cell({self.dest[1]}, {self.dest[0]})"

        # Ensure Prolog has the grid and wall data
        self.prolog.retractall('grid_size(_, _)')
        self.prolog.assertz(f"grid_size({self.columnNumber}, {self.rowNumber})")

        self.prolog.retractall('wall(_, _)')
        for row in self.grid:
            for cell in row:
                if cell.is_wall():
                    x, y = cell.abs, cell.ord
                    self.prolog.assertz(f"wall({x}, {y})")

        # Initialize DFS in Prolog
        solution_found = False
        current = start

        while not solution_found:
            # Prolog query for the next DFS step
            query = f"dfs_step({current}, {destination}, Path, Visited, ToVisit)"
            result = list(self.prolog.query(query))

            if not result:
                messagebox.showinfo("Path Not Found", "No solution")
                return

            result = result[0]

            # Handle ToVisit cells for visualization
            to_visit = result.get('ToVisit', [])
            for cell_str in to_visit:
                match = re.match(r"cell\((\d+),\s*(\d+)\)", cell_str)
                if match:
                    x, y = int(match.group(1)), int(match.group(2))
                    cell = self.grid[y][x]
                    if not cell.is_start() and not cell.is_dest():
                        cell.make_to_visit()
                        app.update_idletasks()
                        time.sleep(0.001)  # Short delay for visualization

            # Handle Visited cells for visualization
            visited = result.get('Visited', [])
            for cell_str in visited:
                match = re.match(r"cell\((\d+),\s*(\d+)\)", cell_str)
                if match:
                    x, y = int(match.group(1)), int(match.group(2))
                    cell = self.grid[y][x]
                    if not cell.is_start() and not cell.is_dest():
                        cell.make_visited()
                        app.update_idletasks()
                        time.sleep(0.001)  # Short delay for visualization

            # Check if the destination has been reached
            path = result.get('Path', [])
            if path:
                for cell_str in path:
                    match = re.match(r"cell\((\d+),\s*(\d+)\)", cell_str)
                    if match:
                        x, y = int(match.group(1)), int(match.group(2))
                        cell = self.grid[y][x]
                        if not cell.is_start() and not cell.is_dest():
                            cell.make_path()
                            app.update_idletasks()
                            time.sleep(0.01)  # Slightly longer delay for path visualization
                solution_found = True
                messagebox.showinfo("Path Found", f"Cells Discovered: {len(visited)}\nDistance to destination: {len(path)-1}")
                break

            # Update the current cell to continue DFS from the stack’s top
            if to_visit:
                current = to_visit[0]

    # def a_star(self):
    #     self.unbind_click()
    #     self.clear_prev_algo()
    #     discovered = 0
    #     count = 0
    #     startCell = self.grid[self.start[0]][self.start[1]]
    #     destCell = self.grid[self.dest[0]][self.dest[1]]
    #     que = PriorityQueue()
    #     que.put((0,count,startCell))

    #     track = {startCell}#keep track of cells in que

    #     startCell.g = 0
    #     startCell.f = self.get_manhattan(startCell,destCell)

    #     while not que.empty():
    #         discovered += 1
    #         currentCell = que.get()[2]
    #         track.remove(currentCell)
    #         if currentCell == destCell:
    #             steps = self.show_path(destCell)
    #             destCell.make_dest()
    #             startCell.make_start()
    #             messagebox.showinfo("path found","Cells Discoverd: {}\nDistance to destination: {}".format(discovered,steps))
    #             return
            
    #         for neighbor in currentCell.neighbors:
    #             tmp = currentCell.g +1

    #             if tmp < neighbor.g:
    #                 neighbor.prev = currentCell
    #                 neighbor.g = tmp
    #                 neighbor.f = tmp + self.get_manhattan(neighbor,destCell)

    #                 if neighbor not in track:
    #                     count+=1
    #                     que.put((neighbor.f,count,neighbor))
    #                     track.add(neighbor)
    #                     neighbor.make_to_visit()
    #             app.update_idletasks()
    #             time.sleep(0.001)
    #         if currentCell != startCell:
    #             currentCell.make_visited()
    #     messagebox.showinfo("Path not found","No solution")

    def get_manhattan(self,cell1,cell2):
        x1,y1 = cell1.abs,cell1.ord
        x2,y2 = cell2.abs,cell2.ord
        return abs(x1-x2) + abs(y1-y2)

    def a_star(self):
        self.unbind_click()
        self.clear_prev_algo()
        discovered = 0
        count = 0

        start_cell = self.grid[self.start[0]][self.start[1]]
        dest_cell = self.grid[self.dest[0]][self.dest[1]]
        que = PriorityQueue()
        que.put((0, count, start_cell))

        track = {start_cell}  # Track cells in the queue
        start_cell.g = 0
        start_cell.f = self.get_manhattan(start_cell, dest_cell)

        # Set up grid and walls in Prolog
        self.prolog.retractall('grid_size(_, _)')
        self.prolog.assertz(f"grid_size({self.columnNumber}, {self.rowNumber})")
        self.prolog.retractall('wall(_, _)')
        for row in self.grid:
            for cell in row:
                if cell.is_wall():
                    x, y = cell.abs, cell.ord
                    self.prolog.assertz(f"wall({x}, {y})")

        # Start A* search
        while not que.empty():
            discovered += 1
            current_cell = que.get()[2]
            track.remove(current_cell)

            if current_cell == dest_cell:
                steps = self.show_path(dest_cell)
                dest_cell.make_dest()
                start_cell.make_start()
                messagebox.showinfo("Path found", f"Cells Discovered: {discovered}\nDistance to destination: {steps}")
                return

            # Query Prolog for neighbors with Manhattan distances
            query = f"a_star_neighbors(cell({current_cell.abs}, {current_cell.ord}), cell({dest_cell.abs}, {dest_cell.ord}), Neighbors)"
            result = list(self.prolog.query(query))
            print(result)

            if result:
                neighbors = result[0]['Neighbors']
                for neighbor_info in neighbors:
                    neighbor_str, g_new, f = neighbor_info
                    match = re.match(r"cell\((\d+),\s*(\d+)\)", neighbor_str)
                    if match:
                        x, y = int(match.group(1)), int(match.group(2))
                        neighbor = self.grid[y][x]

                        # Update neighbor data if this path is better
                        tmp = current_cell.g + 1
                        if tmp < neighbor.g:
                            neighbor.prev = current_cell
                            neighbor.g = tmp
                            neighbor.f = tmp + self.get_manhattan(neighbor, dest_cell)

                            if neighbor not in track:
                                count += 1
                                que.put((neighbor.f, count, neighbor))
                                track.add(neighbor)
                                neighbor.make_to_visit()

                        app.update_idletasks()
                        time.sleep(0.001)

                if current_cell != start_cell:
                    current_cell.make_visited()

        messagebox.showinfo("Path not found", "No solution")

    def dijkstra(self):
        self.unbind_click()
        self.clear_prev_algo()
        discovered = 0

        try:
            # Get start and destination cells
            start_cell = self.grid[self.start[0]][self.start[1]]
            dest_cell = self.grid[self.dest[0]][self.dest[1]]

            # Convert to Prolog coordinates
            start_pos = f"({start_cell.abs}, {start_cell.ord})"
            dest_pos = f"({dest_cell.abs}, {dest_cell.ord})"

            # Reset Prolog knowledge base
            self.prolog.retractall('grid_size(_, _)')
            self.prolog.retractall('wall(_, _)')
            self.prolog.retractall('visited(_, _)')
            self.prolog.retractall('to_visit(_, _)')

            # Set grid dimensions in Prolog
            self.prolog.assertz(f"grid_size({self.columnNumber}, {self.rowNumber})")

            # Add walls to Prolog database
            for row in self.grid:
                for cell in row:
                    if cell.is_wall():
                        self.prolog.assertz(f"wall({cell.abs}, {cell.ord})")

            # Run Dijkstra's algorithm in Prolog with visualization feedback
            query = f"dijkstra_with_visualization({start_pos}, {dest_pos}, Path, VisitedCells, 30)."
            
            # Execute query and retrieve results progressively
            results = list(self.prolog.query(query))
            
            if results:  # Path found
                result = results[0]
                path = result['Path']
                visited_cells = result['VisitedCells']

                # Process each cell in VisitedCells
                for cell_pos in visited_cells:
                    pos_str = str(cell_pos).strip("'\" ,")
                    coords = re.findall(r'\d+', pos_str)
                    if len(coords) >= 2:
                        x, y = int(coords[0]), int(coords[1])
                        cell = self.grid[y][x]

                        if not cell.is_start() and not cell.is_dest():
                            # Mark cell as to be visited (pink)
                            cell.make_to_visit()
                            app.update_idletasks()
                            time.sleep(0.01)
                            
                            # Mark cell as visited (orange)
                            cell.make_visited()
                        discovered += 1

                # Visualize final path
                prev_cell = start_cell
                for cell_pos in path:
                    pos_str = str(cell_pos).strip("'\" ,")
                    coords = re.findall(r'\d+', pos_str)
                    if len(coords) >= 2:
                        x, y = int(coords[0]), int(coords[1])
                        current_cell = self.grid[y][x]
                        current_cell.prev = prev_cell
                        if not current_cell.is_start() and not current_cell.is_dest():
                            current_cell.make_path()
                        prev_cell = current_cell
                        app.update_idletasks()
                        time.sleep(0.01)

                # Show completion message
                steps = len(path) - 1
                messagebox.showinfo(
                    "Path found",
                    f"Cells Discovered: {discovered}\nDistance to destination: {steps}"
                )

            else:  # No path found
                messagebox.showinfo("Path not found", "No solution exists")

        except Exception as e:
            print(f"Error during Dijkstra's algorithm: {e}")
            messagebox.showerror("Error", f"Algorithm failed: {str(e)}")

        finally:
            # Ensure start and end points are correctly marked
            self.grid[self.start[0]][self.start[1]].make_start()
            self.grid[self.dest[0]][self.dest[1]].make_dest()


    # def dijkstra(self):
    #     self.unbind_click()
    #     self.clear_prev_algo()
    #     discovered = 0

    #     que = PriorityQueue()
    #     count = 0 #used as tiebreaker for priority queue -> if distance is equal, whatever comes in the que first goes first
    #     startCell = self.grid[self.start[0]][self.start[1]]
    #     destCell = self.grid[self.dest[0]][self.dest[1]]
    #     startCell.d = 0 #distance from start to itself = 0
    #     track = {startCell} #keep track of cell in que
         
    #     que.put((0,0,startCell))

    #     while not que.empty():
    #         discovered +=1 
    #         currentCell = que.get()[2] #get closest cell
    #         track.remove(currentCell)
    #         if currentCell == destCell:
    #             steps = self.show_path(currentCell)
    #             destCell.make_dest()
    #             startCell.make_start()
    #             messagebox.showinfo("path found","Cells Discoverd: {}\nDistance to destination: {}".format(discovered,steps))
    #             return
    #         for neighbor in currentCell.neighbors:
    #             """"compare between current + 1 and neighbor's distance"""
    #             min_distance = min(neighbor.d,currentCell.d+1)
    #             if min_distance != neighbor.d:
    #                 neighbor.d = min_distance
    #                 neighbor.prev = currentCell

    #                 if neighbor not in track:
    #                     count += 1
    #                     que.put((neighbor.d,count,neighbor))
    #                     track.add(neighbor)
    #                     neighbor.make_to_visit()
    #             app.update_idletasks()
    #             time.sleep(0.001)
    #         if currentCell != startCell:
    #             currentCell.make_visited()
    #     messagebox.showinfo("Path not found","No solution")
start_time = time.time()

def run_time():
    print("time running : {:.2f} s".format(time.time()-start_time))
    app.after(5000,run_time)

if __name__ == "__main__" :
    app = ThemedTk(theme= 'arc')
    pathfinding_visaul = MainPage(app)
    app.title('Pathfinding Algorithm Visualizer')
    app.after(0,run_time)
    app.mainloop()
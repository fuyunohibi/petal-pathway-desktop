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
            print("adding start", cell.ord, cell.abs)
            cell.make_start()
            self.start = [cell.ord,cell.abs]
            self.choose_start = True
        elif not self.choose_dest:
            print("adding dest", cell.ord, cell.abs)
            cell.make_dest()
            self.dest = [cell.ord,cell.abs]
            self.choose_dest = True

        if(self.choose_start and self.choose_dest ):
            if not (cell.is_wall() or cell.is_start() or cell.is_dest() ):
                print("adding wall", cell.ord, cell.abs) # cellord is row, cellabs is column
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

    def generate_maze(self,x,y):
        self.grid[y][x].make_empty()
        directions = [[1,0],[-1,0],[0,1],[0,-1]]
        random.shuffle(directions)

        while len(directions) > 0:
            direction = directions.pop()
            newx = x + direction[0] *2
            newy = y + direction[1] *2

            if (newx<self.columnNumber and newx >= 0) and(newy >= 0 and newy <self.rowNumber) and self.grid[newy][newx].is_wall():
                link_x = direction[0] + x
                link_y = direction[1] + y
                self.grid[link_y][link_x].make_empty()
                app.update_idletasks()
                time.sleep(0.0005)
                self.generate_maze(newx,newy)
        
        return

    def start_algo(self, algo):
        if self.choose_start and self.choose_dest:
            print("Started", algo)
            print(f"start = [{self.start[0]}][{self.start[1]}] end = [{self.dest[0]}][{self.dest[1]}]")
            self.set_neighbors()
            if algo == "Breadth First Search":
                threading.Thread(target=self.bfs).start()
            elif algo == "Depth First Search":
                self.dfs()
            elif algo == "A*(A-Star) Pathfinding":
                self.a_star()
            elif algo == "Dijkstra's Shortest path Algorithm":
                self.dijkstra()
        else:
            messagebox.showerror("Error", "Please choose start and destination point first!")

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
        discovered = 0

        try:
            # Prolog interaction setup
            start_cell = self.grid[self.start[0]][self.start[1]]
            dest_cell = self.grid[self.dest[0]][self.dest[1]]

            start_pos = f"({start_cell.abs}, {start_cell.ord})"
            dest_pos = f"({dest_cell.abs}, {dest_cell.ord})"

            # Set grid size in Prolog
            prolog.retractall('grid_size(_, _)')
            prolog.assertz(f"grid_size({self.columnNumber}, {self.rowNumber})")

            # Remove any previous wall facts
            prolog.retractall('wall(_, _)')

            # Add walls to Prolog
            for row in self.grid:
                for cell in row:
                    if cell.is_wall():
                        x = cell.abs
                        y = cell.ord
                        prolog.assertz(f"wall({x}, {y})")

            print(f"Running Prolog query: bfs_with_timeout({start_pos}, {dest_pos}, Path, 20).")

            query = f"bfs_with_timeout({start_pos}, {dest_pos}, Path, 20)."  # Timeout of 20 seconds

            result = list(prolog.query(query))

            print(f"Prolog query result: {result}")

            if result:
                prolog_path = result[0]['Path']

                for step in prolog_path:
                    # Convert step to string and remove unwanted characters
                    step_str = str(step).strip("'\" ,")
                    print(f"Processing step: '{step_str}'")
                    # Extract all numbers from the step
                    nums = re.findall(r'\d+', step_str)
                    if len(nums) >= 2:
                        x = int(nums[0])
                        y = int(nums[1])
                        print(f"Extracted coordinates: x={x}, y={y}")
                    else:
                        print(f"Unexpected step format: '{step_str}'")
                        continue

                    cell = self.grid[y][x]
                    if not cell.is_start() and not cell.is_dest():
                        cell.make_path()
                        app.update_idletasks()
                        time.sleep(0.05)
                messagebox.showinfo("Path Found", "A path was found!")
            else:
                messagebox.showinfo("Path Not Found", "No solution")

        except Exception as e:
            print(f"Error during Prolog query: {e}")
            messagebox.showerror("Error", f"Prolog query failed: {e}")

        self.grid[self.start[0]][self.start[1]].make_start()
        self.grid[self.dest[0]][self.dest[1]].make_dest()




    def get_manhattan(self,cell1,cell2):
        x1,y1 = cell1.abs,cell1.ord
        x2,y2 = cell2.abs,cell2.ord
        return abs(x1-x2) + abs(y1-y2)

    def a_star(self):
        self.unbind_click()
        self.clear_prev_algo()
        discovered = 0
        count = 0
        startCell = self.grid[self.start[0]][self.start[1]]
        destCell = self.grid[self.dest[0]][self.dest[1]]
        que = PriorityQueue()
        que.put((0,count,startCell))

        track = {startCell}#keep track of cells in que

        startCell.g = 0
        startCell.f = self.get_manhattan(startCell,destCell)

        while not que.empty():
            discovered += 1
            currentCell = que.get()[2]
            track.remove(currentCell)
            if currentCell == destCell:
                steps = self.show_path(destCell)
                destCell.make_dest()
                startCell.make_start()
                messagebox.showinfo("path found","Cells Discoverd: {}\nDistance to destination: {}".format(discovered,steps))
                return
            
            for neighbor in currentCell.neighbors:
                tmp = currentCell.g +1

                if tmp < neighbor.g:
                    neighbor.prev = currentCell
                    neighbor.g = tmp
                    neighbor.f = tmp + self.get_manhattan(neighbor,destCell)

                    if neighbor not in track:
                        count+=1
                        que.put((neighbor.f,count,neighbor))
                        track.add(neighbor)
                        neighbor.make_to_visit()
                app.update_idletasks()
                time.sleep(0.001)
            if currentCell != startCell:
                currentCell.make_visited()
        messagebox.showinfo("Path not found","No solution")

    def dijkstra(self):
        self.unbind_click()
        self.clear_prev_algo()
        discovered = 0

        que = PriorityQueue()
        count = 0 #used as tiebreaker for priority queue -> if distance is equal, whatever comes in the que first goes first
        startCell = self.grid[self.start[0]][self.start[1]]
        destCell = self.grid[self.dest[0]][self.dest[1]]
        startCell.d = 0 #distance from start to itself = 0
        track = {startCell} #keep track of cell in que
         
        que.put((0,0,startCell))

        while not que.empty():
            discovered +=1 
            currentCell = que.get()[2] #get closest cell
            track.remove(currentCell)
            if currentCell == destCell:
                steps = self.show_path(currentCell)
                destCell.make_dest()
                startCell.make_start()
                messagebox.showinfo("path found","Cells Discoverd: {}\nDistance to destination: {}".format(discovered,steps))
                return
            for neighbor in currentCell.neighbors:
                """"compare between current + 1 and neighbor's distance"""
                min_distance = min(neighbor.d,currentCell.d+1)
                if min_distance != neighbor.d:
                    neighbor.d = min_distance
                    neighbor.prev = currentCell

                    if neighbor not in track:
                        count += 1
                        que.put((neighbor.d,count,neighbor))
                        track.add(neighbor)
                        neighbor.make_to_visit()
                app.update_idletasks()
                time.sleep(0.001)
            if currentCell != startCell:
                currentCell.make_visited()
        messagebox.showinfo("Path not found","No solution")
start_time = time.time()

def run_time():
    # print("time running : {:.2f} s".format(time.time()-start_time))
    app.after(5000,run_time)

if __name__ == "__main__" :
    # Initialize Prolog engine
    prolog = Prolog()
        # Get the current script directory and consult bfs.pl
    prolog_dir = os.path.join(os.path.dirname(__file__), '../prolog/bfs.pl')  # Adjust this path as needed
    try:
        # Consult the bfs.pl file
        prolog.consult(prolog_dir)
        print("Prolog file consulted successfully.")
    except Exception as e:
        print(f"Error consulting Prolog file: {e}")
    app = ThemedTk(theme= 'arc')
    pathfinding_visaul = MainPage(app)
    app.title('Pathfinding Algorithm Visualizer')
    app.after(0,run_time)
    app.mainloop()
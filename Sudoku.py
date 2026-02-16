import math
import random
import curses
import copy

class Sudoku:
    def __init__(self, size, difficulty):
        assert size in [4, 9], "Grid size not 4 or 9!"
        self.size = size
        self.sizeRoot = int(math.sqrt(self.size))
        self.difficulty = difficulty
        self.matrix = [[0 for _ in range(size)] for _ in range(size)]
        self.postRemove = []
        self.solution = []
    
    def isSolved(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.matrix[i][j] != self.solution[i][j]: 
                    return False
        return True

    # Courtesy of ChatGPT (checking unique solutions during removal of digits)
    def has_unique_solution(self):
        size = self.size
        root = self.sizeRoot
        matrix = self.matrix

        rows = [0] * size
        cols = [0] * size
        boxes = [0] * size
        empties = []

        for row in range(size):
            for col in range(size):
                val = matrix[row][col]
                if val == 0:
                    empties.append((row, col))
                bit = 1 << val
                box = (row // root) * root + (col // root)
                rows[row] |= bit
                cols[col] |= bit
                boxes[box] |= bit

        solution_count = 0

        # Courtesy of ChatGPT (checking unique solutions during removal of digits)
        def backtrack(idx=0):
            nonlocal solution_count

            if solution_count > 1:
                return

            if idx == len(empties):
                solution_count += 1
                return

            row, col = empties[idx]
            box = (row // root) * root + (col // root)

            for val in range(1, size + 1):
                bit = 1 << val
                if not (rows[row] & bit or cols[col] & bit or boxes[box] & bit):
                    matrix[row][col] = val
                    rows[row] |= bit
                    cols[col] |= bit
                    boxes[box] |= bit

                    backtrack(idx + 1)

                    matrix[row][col] = 0
                    rows[row] ^= bit
                    cols[col] ^= bit
                    boxes[box] ^= bit
                
                    if solution_count > 1:
                        return

        backtrack()
        return solution_count == 1

    # Courtesy of ChatGPT (Checking unique solutions during removal of digits)
    def remove_cells(self, attempts):
        cells = [(r, c) for r in range(self.size) for c in range(self.size)]
        random.shuffle(cells)

        removed = 0

        for r, c in cells:
            if removed >= attempts:
                break

            backup = self.matrix[r][c]
            self.matrix[r][c] = 0

            if not self.has_unique_solution():
                self.matrix[r][c] = backup
            else:
                removed += 1

    def fillMatrix(self):
        self.fillDiagonalBoxes()
        self.fillRemaining(0, 0)
        self.solution = copy.deepcopy(self.matrix)

    def generateNumber(self) -> int:
        return random.randint(1, self.size)

    def fillBox(self, row, column):
        for i in range(self.sizeRoot):
            for j in range(self.sizeRoot):
                while (True):
                    num = self.generateNumber()
                    if self.validInBox(row, column, num):
                        break
                self.matrix[row + i][column + j] = num

    def fillDiagonalBoxes(self):
        for i in range(0, self.size, self.sizeRoot):
            self.fillBox(i, i)

    def fillRemaining(self, row, column) -> bool:
        if column == self.size:
            row += 1
            column = 0

        if row == self.size:
            return True

        if self.matrix[row][column] != 0:
            return self.fillRemaining(row, column + 1)

        for number in range(1, self.size + 1):
            if self.checkIfValid(row, column, number):
                self.matrix[row][column] = number
                if self.fillRemaining(row, column + 1):
                    return True
                self.matrix[row][column] = 0

        return False

    def checkIfValid(self, row, column, number) -> bool:
        validRow = self.validInRow(row, number)
        validCol = self.validInCol(column, number)
        validBox = self.validInBox(row - (row % self.sizeRoot), column - (column % self.sizeRoot), number) 
        return validRow and validCol and validBox

    def validInBox(self, rowStart, columnStart, number) -> bool:
        for i in range(self.sizeRoot):
            for j in range(self.sizeRoot):
                if self.matrix[rowStart + i][columnStart + j] == number:
                    return False
        return True

    def validInRow(self, row, number) -> bool:
        for j in range(self.size):
            if self.matrix[row][j] == number:
                return False
        return True

    def validInCol(self, column, number) -> bool:
        for i in range(self.size):
            if self.matrix[i][column] == number:
                return False
        return True

def run(stdscr):
    
    curses.curs_set(0)
    stdscr.timeout(16)

    # Draw a box around the main scree
    stdscr.box(curses.ACS_VLINE, curses.ACS_HLINE)
    
    key = 0
    cursorX = 0
    cursorY = 0
    
    height, width = stdscr.getmaxyx()
    
    offsetCenterX = 3
    
    # Grid Constants
    spacingX = 4
    spacingY = 2

    difficulties = ["Debug", "Easy", "Medium", "Hard"]

    gridSize = 9
    difficulty = "Debug"
    
    attempts = 0
    
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

    while (True):

        stdscr.clear()
        
        if key == ord('q'):
            return
        elif key == curses.KEY_RIGHT:
            cursorX += 1
        elif key == curses.KEY_LEFT:
            cursorX -= 1
        elif key in (curses.KEY_ENTER, ord('\n'), ord('\r')):
            if cursorX == 0:
                gridSize = 9
            else:
                gridSize = 4
            break

        cursorX = max(0, cursorX)
        cursorX = min(1, cursorX)
    
        color = curses.color_pair(2)

        if cursorX == 0:
            stdscr.addstr(int(height // 2), int(width // 2) - offsetCenterX * 2, "9x9", curses.color_pair(1))
            stdscr.addstr(int(height // 2), int(width // 2) + offsetCenterX, "4x4", curses.color_pair(2))
        else:
            stdscr.addstr(int(height // 2), int(width // 2) - offsetCenterX * 2, "9x9", curses.color_pair(2))
            stdscr.addstr(int(height // 2), int(width // 2) + offsetCenterX, "4x4", curses.color_pair(1))
        
        stdscr.refresh()
        key = stdscr.getch()
   
    key = 0
    cursorX = 0
    cursorY = 0

    while (True):

        stdscr.clear()

        if key == ord('q'):
            return
        elif key == curses.KEY_DOWN:
            cursorY += 1
        elif key == curses.KEY_UP:
            cursorY -= 1
        elif key in (curses.KEY_ENTER, ord('\n'), ord('\r')):
            difficulty = difficulties[cursorY]
            break
        
        cursorY = max(0, cursorY)
        cursorY = min(3, cursorY)

        for i in range(4):
            color = curses.color_pair(2)
            if i == cursorY:
                color = curses.color_pair(1)
            stdscr.addstr(int(height // 2) + i, int(width // 2), difficulties[i], color)

        stdscr.refresh()
        key = stdscr.getch()

    sudoku = Sudoku(gridSize, difficulty)
    sudoku.fillMatrix()
    
    match (sudoku.difficulty):
        case "Debug":
            attempts = 1
        case "Easy":
            if sudoku.size == 4:
                attempts = 2
            else:
                attempts = 20
        case "Medium":
            if sudoku.size == 4:
                attempts = 4
            else:
                attempts = 30
        case "Hard":
            if sudoku.size == 4:
                attempts = 6
            else:
                attempts = 40

    sudoku.remove_cells(attempts=attempts)
    sudoku.postRemove = copy.deepcopy(sudoku.matrix)
    
    key = 0
    cursorX = 0
    cursorY = 0

    while (True):

        stdscr.clear()

        numPressed = -1

        if key == ord('q'):
            return
        elif key == curses.KEY_DOWN:
            cursorY += 1
        elif key == curses.KEY_UP:
            cursorY -= 1
        elif key == curses.KEY_RIGHT:
            cursorX += 1
        elif key == curses.KEY_LEFT:
            cursorX -= 1
        elif ord('1') <= key <= ord('9'):
            numPressed = key - ord('0')

        cursorX = max(0, cursorX)
        cursorX = min(sudoku.size - 1, cursorX)
        
        cursorY = max(0, cursorY)
        cursorY = min(sudoku.size - 1, cursorY)
        
        posX = int(width // 2 - spacingX * int(sudoku.size // 2))
        posY = int(height // 2 - spacingY * int(sudoku.size // 2))    
        
        if numPressed > -1:
            if sudoku.postRemove[cursorX][cursorY] == 0:
                sudoku.matrix[cursorX][cursorY] = numPressed

        # Draw Matrix, Curses-style
        for i in range(sudoku.size):
            for j in range(sudoku.size):
                cell = str(sudoku.matrix[i][j])
                color = curses.color_pair(2)
                originalCell = sudoku.postRemove[i][j] != 0
                if cell == "0":
                    cell = " "
                if cursorX == i and cursorY == j:
                    if originalCell:
                        color = curses.color_pair(3)
                    color = curses.color_pair(1)
                else:
                    if originalCell:
                        color = curses.color_pair(3)
                stdscr.addstr(posY + j * spacingY, posX + i * spacingX, cell, color)
        
        # Draw Matrix Grid, Vertical Bars
        for i in range(-1, sudoku.size, sudoku.sizeRoot):
            for j in range(-1, sudoku.size * spacingY):
                pY = posY + j
                pX = posX + i * spacingX + int(spacingX // 2)
                stdscr.addch(pY, pX, curses.ACS_VLINE, curses.color_pair(2))
        
        # Draw Matrix Grid, Horizontal Bars and Intersections
        for j in range(-1, sudoku.size, sudoku.sizeRoot):
            for i in range(-1, sudoku.size * spacingX - 2):
                pY = posY + j * spacingY + int(spacingY // 2)
                pX = posX + i
                ch = stdscr.inch(pY, pX)
                char = ch & curses.A_CHARTEXT
                if char == (curses.ACS_VLINE & curses.A_CHARTEXT):
                    stdscr.addch(pY, pX, curses.ACS_PLUS, curses.color_pair(2))
                else:
                    stdscr.addch(posY + j * spacingY + int(spacingY // 2), posX + i, curses.ACS_HLINE, curses.color_pair(2))
        
        if sudoku.isSolved():
            return

        stdscr.refresh()
        key = stdscr.getch()

def main():
    curses.wrapper(run)

if __name__ == "__main__":
    main()

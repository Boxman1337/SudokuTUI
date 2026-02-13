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
    
    # Draw a box around the main scree
    stdscr.box(curses.ACS_VLINE, curses.ACS_HLINE)
    
    sudoku = Sudoku(9, "H")
    sudoku.fillMatrix()

    attempts = 0

    match (sudoku.difficulty):
        case "D":
            if sudoku.size == 4:
                attempts = 1
            attempts = 1
        case "E":
            if sudoku.size == 4:
                attempts = 2
            attempts = 20
        case "M":
            if sudoku.size == 4:
                attempts = 4
            attempts = 30
        case "H":
            if sudoku.size == 4:
                attempts = 6
            attempts = 40

    sudoku.remove_cells(attempts=attempts)
    sudoku.postRemove = copy.deepcopy(sudoku.matrix)

    k = 0
    cursorX = 0
    cursorY = 0
    
    stdscr.clear()
    stdscr.refresh()

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

    while (k != ord('q')):
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        numPressed = -1

        if k == curses.KEY_DOWN:
            cursorY += 1
        elif k == curses.KEY_UP:
            cursorY -= 1
        elif k == curses.KEY_RIGHT:
            cursorX += 1
        elif k == curses.KEY_LEFT:
            cursorX -= 1
        elif ord('1') <= k <= ord('9'):
            numPressed = k - ord('0')

        cursorX = max(0, cursorX)
        cursorX = min(sudoku.size - 1, cursorX)
        
        cursorY = max(0, cursorY)
        cursorY = min(sudoku.size - 1, cursorY)
        
        if numPressed > -1:
            if sudoku.postRemove[cursorX][cursorY] == 0:
                sudoku.matrix[cursorX][cursorY] = numPressed

        # Drawing Constants
        spacingX = 4
        spacingY = 2
        posX = int(width // 2 - spacingX * int(sudoku.size // 2))
        posY = int(height // 2 - spacingY * int(sudoku.size // 2))
        
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
        k = stdscr.getch()

def main():
    curses.wrapper(run)

if __name__ == "__main__":
    main()

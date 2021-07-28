import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells) and self.count > 0:
            # num mines is same as cells = all cells mines unless empty set and 0
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            # all cells are safe if no mines
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            # take out mine
            self.cells = self.cells - {cell}
            # one less mine in count
            if self.count > 0:
                self.count -= 1
            else:
                raise Exception("Tried to mark a mine when all mines were already found in the sentence")
        else:
            # mine not in this sent
            return

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            # take out safe cell
            self.cells = self.cells - {cell}
        else:
            # cell not in this sent
            return

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        self.allMoves = set()

        for y in range(height):
            for x in range(width):
                self.allMoves.add((x, y))

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.safes.add(cell)

        neighbors = set()

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):  # add 2 because loops for one less than max when starting at not 0
            for j in range(cell[1] - 1, cell[1] + 2):  # y then x (i, j) is y, x

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # must be cell within board range
                if (i, j) in self.allMoves:
                    # if its a known mine we can simplify and not put it in
                    if (i, j) in self.mines:
                        count -= 1
                        continue
                    # the cell's state is not determined
                    if ((i, j) not in self.moves_made
                    and (i, j) not in self.safes):
                        # add cell to neighbors
                        neighbors.add((i, j))
        # make sentence relating neighbors to amount of mines nearby
        self.knowledge.append(Sentence(neighbors, count))
        def inferKnowledge(safes=set(), mines=set()):
            """ figure out new knowledge from knowledge base """

            change = False  # if we change something we know to call again to see if we can make more infers

            newSentences = []  # sentences we want to add after iterating

            # we might be able to keep inferring if find new mines or safes
            newMines = set()
            newSafes = set()

            for i in range(len(self.knowledge)):
                # mark cells safe
                for cell in safes:
                    self.knowledge[i].mark_safe(cell)

                # mark cells as mines
                for cell in mines:
                    self.knowledge[i].mark_mine(cell)

                # add any mines or safes that can be found based off that
                known_mines = self.knowledge[i].known_mines()

                # new mines figured out
                if known_mines and not known_mines <= self.mines:
                    # add mines to new mines found
                    newMines.union(known_mines - self.mines)
                    change = True
                    self.mines = self.mines.union(known_mines)

                known_safes = self.knowledge[i].known_safes()
                # new safes figured out
                if known_safes and not known_safes <= self.safes:
                    # add to new safes found
                    newSafes.union(known_safes - self.safes)
                    change = True
                    self.safes = self.safes.union(known_safes)
                # don't run for last element
                if i < len(self.knowledge):
                    # compare every sentence with each other (not including ones already compared)
                    for n in range(i + 1, len(self.knowledge)):
                        # we don't need to infer if the tile is 0, any new sentences won't help
                        if self.knowledge[i].count == 0 or self.knowledge[n].count == 0:
                            continue
                        # if one is a subset of the other
                        if self.knowledge[i].cells < self.knowledge[n].cells:
                            # construct new sentence with subset
                            subsetCells = self.knowledge[n].cells - self.knowledge[i].cells
                            subsetCount = self.knowledge[n].count - self.knowledge[i].count
                            subSent = Sentence(subsetCells, subsetCount)
                            # ensure the subset is not already made
                            if subSent in self.knowledge:
                                break
                            else:  # no subset, make it
                                newSentences.append(subSent)
                                # we might be able to infer from this new sent
                                change = True
                        # subset could be the other way around
                        elif self.knowledge[n].cells < self.knowledge[i].cells:
                            subsetCells = self.knowledge[i].cells - self.knowledge[n].cells
                            subsetCount = self.knowledge[i].count - self.knowledge[n].count
                            subSent = Sentence(subsetCells, subsetCount)
                            if subSent in self.knowledge:
                                break
                            else:
                                newSentences.append(subSent)
                                change = True
            self.knowledge = self.knowledge + newSentences
            if change:
                inferKnowledge(newMines, newSafes)

        inferKnowledge({cell})

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # finds safe moves that aren't already made
        safeMoves = self.safes - self.moves_made
        if len(safeMoves):
            # return a safe move
            return next(iter(safeMoves))
        else:
            # no safe moves
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        randomMoves = self.allMoves - self.moves_made - self.mines
        if len(randomMoves):
            # turns set into list in order to get a random index/move
            return list(randomMoves)[random.randrange(len(randomMoves))]
        else:
            return None

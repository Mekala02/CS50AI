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
        # If set of (board cells count = count of the number of those cells which are mines) we can conclude all of them are mines
        if len(self.cells) == self.count:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If (the number of cells which are mines = 0)  we can conclude all of board cells are safes
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # If cell is a mine then we have to remove it from board cells and reduce count of the number of cells which are mines
        # (becouse we removed that mine from our board cells)
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # If that cell is safe then we have to remove it from our board cells
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

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

    def neighborsofcell(self, cell):
        # Returns all neighbors of that cell
        neighbors = set()
        x, y = cell
        for a in [-1, 0, 1]:
            for b in [-1, 0, 1]:
                neighbors.add((x+a, y+b))
        neighbors.remove((x, y))
        # Removing the cells which are not in gameboard
        # Copied becouse we changing the neighbors set doing iteration:
        for impossible in neighbors.copy():
            if impossible[0] < 0 or impossible[0] > self.height-1 or impossible[1] < 0 or impossible[1] > self.width-1:
                neighbors.remove(impossible)
        return neighbors

    def unknwnneighbors(self, cell, count):
        # Returns ((neighbors of that cell which we dont know if those cells are mine or safe) and (count of the number of those cells which are mines))
        unknown_neighbors = set(self.neighborsofcell(cell))
        concluded_count = count
        for known in unknown_neighbors.copy():
            # Same logic as sentence class's mark_safe function
            if known in self.safes:
                unknown_neighbors.remove(known)
            if known in self.mines:
                # Same logic as sentence class's mark_mine function
                unknown_neighbors.remove(known)
                concluded_count -= 1
        return (unknown_neighbors, concluded_count)

    def updateknowledge(self):
        '''
        Iterating over sentences in the knowledge base checking if there is new detected mines or safes in that perticular sentence
        If we detected mines or safes in that particular sentence, we are updating all sentences
        (We are using Sentence class's mark_mine or mark_safe functions on all sentences (in knowledge base) for updating the sentences contents)
        '''
        for sentence in self.knowledge.copy():
            if sentence.known_mines() != None:
                # If we are there that means we produceded empty sentence we have to delete it for faster program otherwise it will iterate over empty sentence in inferance function for nothing
                # We have to check if it's in knowledge becouse maybe sentence is not in knowledge. Becouse other if statement can delete it also
                if sentence in self.knowledge:
                    # It won't effect that loop becouse we copied the self.knowledge in the begenning
                    self.knowledge.remove(sentence)
                    # Copied becouse self.mark_safe(safe) is changing the sentence.known_safes() doing iteration:
                for mine in sentence.known_mines().copy():
                    self.mark_mine(mine)

            # Same as above if statement except this is for safes
            if sentence.known_safes() != None:
                if sentence in self.knowledge:
                    self.knowledge.remove(sentence)
                for safe in sentence.known_safes().copy():
                    self.mark_safe(safe)

    def inferance(self):
        '''
        Checking if we can make new sentences from previous ones (inferanceing)
        Adding new sentences to the knowledge base
        How we checking if we infer new sentences ?
            Taking 2 sentences and checking if one of them is subseting other
            If there is a subset, substracting subset from set. Also we substracting the count value of subset from our set's count value
            The concleded set and concluded count value becomes our new sentence.

        '''
        for sentence1 in self.knowledge.copy():
            for sentence2 in self.knowledge.copy():
                if sentence1.cells.issubset(sentence2.cells):
                    subcells = sentence2.cells - sentence1.cells
                    subcount = sentence2.count - sentence1.count
                    new_sentence = Sentence(subcells, subcount)
                    if new_sentence not in self.knowledge:
                        self.knowledge.append(new_sentence)
                elif sentence2.cells.issubset(sentence1.cells):
                    subcells = sentence1.cells - sentence2.cells
                    subcount = sentence1.count - sentence2.count
                    new_sentence = Sentence(subcells, subcount)
                    if new_sentence not in self.knowledge:
                        self.knowledge.append(new_sentence)
        # We have to update knowledge becouse we added new sentences and maybe those sentences contains new mines and safes(It updates all sentences in the knowledge base)
        self.updateknowledge()

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Marking the cell as a move that has been made
        self.moves_made.add(cell)

        # Marking the cell as safe
        self.mark_safe(cell)

        # Adding a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        unknown_neighbors, concluded_count = self.unknwnneighbors(cell, count)
        self.knowledge.append(Sentence(unknown_neighbors, concluded_count))

        '''
        Making inferance until no inferance possible. (if previus knowledge = last knowledge it means we cant make any inferance)
        It also calls updateknowledg function inside inferance so we are updating our knowledge at the same time
        '''
        while True:
            currentbase = self.knowledge.copy()
            self.inferance()
            if currentbase == self.knowledge:
                break

        # For debugging
        # print("----------------------------------------------------------------------------------")
        # print(f"Moves me make: {self.moves_made}")
        # print(f"Founded mines are {self.mines}")
        # print(f"Safes are {self.safes}")
        # print(f"Our knowledges are:")
        # for sentence in self.knowledge:
        #     print(sentence, end=", ")
        # print()
        # print("----------------------------------------------------------------------------------")
        # for _ in range(3): print()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if self.safes == set():
            return None
        for safemove in self.safes:
            if not safemove in self.moves_made:
                return safemove

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
            Selects random x and y if its not suitable then tries traditional methot
            Not: It is faster to just iterating over all celss and returning if it is not bomb or not in moves_made
        """
        x = random.randrange(self.height)
        y = random.randrange(self.width)
        if not (x, y) in self.moves_made and not (x, y) in self.mines:
            return (x, y)

        for x in range(self.height):
            for y in range(self.width):
                if not (x, y) in self.moves_made and not (x, y) in self.mines:
                    return (x, y)

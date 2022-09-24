import sys
import copy

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Iteratin over all variables
        for variable in self.crossword.variables:
            # Iterating over all words inside the variable
            for word in self.crossword.words:
                # If variable doesnt fit the containter remove it from varibles domain
                if variable.length != len(word):
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        # Overlap contains relative coordinates to each variables overlaping location
        # We don't have to check if there is overlap becouse
        # we already know it's overlaps since ac3 only sending variable and its neighbors
        a, b = self.crossword.overlaps[x, y]
        # Selecting every combinations of words inside x's domain and y's domain
        for word_x in self.domains[x].copy():
            delete = 1
            for word_y in self.domains[y]:
                # If letters from words relative coordinates matching then we can
                # conculude there is at least one valid option if I choose that word
                if word_x[a] == word_y[b]:
                    delete = 0
                    continue
            # If we cant find any valid option for given word we are removing it from domain
            if delete:
                self.domains[x].remove(word_x)
                revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If arcs is empty we are adding this (variables, all neighbors of that variable) for all variables.
        # Reson why we are not adding all combinations of 2 variables is we already know if 2 variable is not
        # neighbors they can't conflict.
        if arcs == None:
            arcs = []
            for variable1 in self.crossword.variables:
                for variable2 in self.crossword.variables:
                    # If var1 and var2 are different and if they are overlaps we adding to frontier
                    if variable1 != variable2 and self.crossword.overlaps[variable1, variable2]:
                        arcs.append((variable1, variable2))

        # Arcs is our frontier. We are keep solving until the frontier become empty.
        while arcs:
            # Pops default value is -1, which returns the last item.
            # So we made a Stack frontier(last in first out)
            x, y = arcs.pop()
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for neighbor in self.crossword.neighbors(x) - {y}:
                    arcs.append((neighbor, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Look for each variable if that variable is inside assignment
        for variable in self.crossword.variables:
            if variable not in assignment.keys():
                return False
        # If all variables is in assignment then we can conclude assignment is completed
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # We dont have to check if two variable is assigned same word because
        # we selected these assignments variables with select_unassigned_variable
        # which only outputs unassigned variables
        # So we only checking if overlaping values are correct or not

        # We need to check all data integrity so we selecting
        # all combinations of 2 variables in assignment
        for variable1 in assignment:
            for variable2 in assignment:
                # If var1 and var2 are different and if they are overlaps we checking correctness
                if variable1 != variable2 and (overlap := self.crossword.overlaps[variable1, variable2]):
                    word1 = assignment[variable1]
                    word2 = assignment[variable2]
                    a, b = overlap
                    # If letters from words relative coordinates not matching
                    # it means this assignment is not consistent
                    if word1[a] != word2[b]:
                        return False
        return True

    def ifsatisfied(self, variable1, variable2, word1, word2):
        '''
        Functinon for order_domain_values function
        '''
        # If selected var(var1) and var2 not overlaping it can't conflict
        if not (overlap := self.crossword.overlaps[variable1, variable2]):
            return True
        x, y = overlap
        # If words1's relative coordinate and word2's relative coordinate are matching then we can
        # conculude there is no confliction
        if word1[x] == word2[y]:
            return True
        # if non of them true than there is confliction
        return False

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        variable1 = var
        # Counter for counting each words number of values that they rule out for neighboring variables
        # Initially all values are 0
        ruleout_count = {value: 0 for value in self.domains[variable1]}
        # Selecting words from variable for looking how many rules it can role out
        for word1 in self.domains[variable1]:
            # Looking to all variables neighbors domains
            for variable2 in self.crossword.neighbors(var):
                for word2 in self.domains[variable2]:
                    # If that particular word combination conflicts we adding one to word1's ruleout counter
                    if not self.ifsatisfied(variable1, variable2, word1, word2):
                        ruleout_count[word1] += 1
        # Returns sorted list according to rulout count (ascending order)
        return sorted([x for x in ruleout_count], key=lambda x: ruleout_count[x])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Substracting assigned variables from all variables for finding all unassigbed variables
        unassigned = set(self.crossword.variables) - set(assignment.keys())
        # Sorting unassigned variables according to minimum domain count, if domain counts are equal looking which one have maximum neighbor count
        result = sorted(unassigned, key=lambda variable: (len(self.domains[variable]), -len(self.crossword.neighbors(variable))))
        return result[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.
        `assignment` is a mapping from variables (keys) to words (values).
        If no assignment is possible, return None.
        """
        # If we find a solution return it
        if self.assignment_complete(assignment):
            return assignment

        # Cappying all variables domains
        domains_coppy = copy.deepcopy(self.domains)
        # Selecting variable
        variable = self.select_unassigned_variable(assignment)
        # Iterating over all values for that variable
        for value in self.order_domain_values(variable, assignment):
            # Assigning selected value to variable
            assignment[variable] = value
            # Checking if that value in this variable is consistent with orhers variables
            if self.consistent(assignment):
                # Assign this varlue to that variable
                self.domains[variable] = {value}
                # Upgrade knowledge base and check if this assignment is conflicting or not
                if self.ac3([(variable, neighbor) for neighbor in self.crossword.neighbors(variable)]):
                    # Recursively solve other assignments
                    if result := self.backtrack(assignment):
                        # If we find assignment in that path return it
                        return result
            # If we are here that means we cound't find ant solutions on that path
            # So we have to undo what we done in that path
            # We removing inferances from assignment
            self.domains = copy.deepcopy(domains_coppy)
            # Then we removing var = value
            self.domains[variable].remove(value)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

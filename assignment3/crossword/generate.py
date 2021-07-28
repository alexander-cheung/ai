import sys

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
        # iterate over each var in cross
        for var in self.crossword.variables:
            # make var's domain only words that are the right length
            self.domains[var] = {word for word in self.domains[var]
                                 if var.length == len(word)}

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # if the two words intersect
        intersect = self.crossword.overlaps[x, y]
        # words to keep in x after iterating
        newX = set()

        # only check if intersecting
        if intersect:
            # look through each word in x domain
            for xWord in self.domains[x]:
                # ensure x word has same letter intersect with y
                for yWord in self.domains[y]:
                    if xWord[intersect[0]] == yWord[intersect[1]]:
                        # else take the word out of domain
                        newX.add(xWord)
                        # don't need to keep checking this word
                        break

        # diff set then there was change
        if newX != self.domains[x]:
            # only keep working words            
            self.domains[x] = newX
            return True
        else:  # no change then return false
            return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # init arcs if not already done (only intersects are binary cond)
        if not arcs:

            # only arcs for vars that actually intersect
            arcs = [arc for arc in list(self.crossword.overlaps.keys())
                    if self.crossword.overlaps[arc]]

        # loop until all arcs consistent
        while arcs:
            # take an arc
            currentArc = arcs.pop()

            # make arc consistent
            revised = self.revise(currentArc[0], currentArc[1])

            if revised:
                # nothing left in domain = can't solve
                if not self.domains[currentArc[0]]:
                    return False

                """ might cause problems with other arcs intersecting with x
                    so append those to make them consistent"""
                arcs += [arc for arc in self.crossword.overlaps.keys()
                         if arc and self.crossword.overlaps[arc]
                         and currentArc[0] in arc
                         and arc[1] != currentArc[1]]

        # after looping: all consistent and still domains = can solve
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # not every var assigned/in dict = not done yet
        if set(assignment.keys()) != set(self.crossword.variables):
            return False

        # check each var has word for answer
        for word in assignment.values():
            # assuming var is just a string or None
            if not word:
                return False

        # made to end = all vars have a string
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        assignedVars = list(assignment.keys())
        # each solution to var
        for var, word in assignment.items():

            # if words don't fit in crossword puzzle
            if var.length != len(word):
                return False

            # if intersections conflict
            overlaps = {key: position for key, position in self.crossword.overlaps.items()
                if var in key and position}
            for key, intersectWord in overlaps.items():

                # two letters not matching up
                if key[0] in assignedVars and key[1] in assignedVars:
                    if assignment[key[0]][intersectWord[0]] != assignment[key[1]][intersectWord[1]]:
                        return False

        # if same word mult times
        if len(set(assignment.values())) != len(assignment):
            return False
        else:  # else true
            return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # domain with values n of each var
        newDomain = {}
        # loop through each word var's domain
        for word in self.domains[var]:
            # find out how other variables' answers are limited by this word
            n = 0
            # each var
            for key, words in self.domains.items():
                # dont compare the same var to itself
                if key == var:
                    continue

                intersect = self.crossword.overlaps[var, key]
                # vars intersect
                if intersect:
                    # count answers for other vars that work with this word assigned
                    for possibleAnswer in words:
                        if word[intersect[0]] == possibleAnswer[intersect[1]]:
                            n += 1
            # assign n to word
            newDomain[word] = n            
        # sort words by n then return
        return sorted(newDomain, key=lambda getNum: newDomain[getNum])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # best var to assign
        bestVar = None
        # each unassigned var
        for var in self.crossword.variables - set(assignment.keys()):
            # keep track of lowest
            if not bestVar or len(self.domains[var]) < len(self.domains[bestVar]):
                bestVar = var

            # same domain = whichever intersect with more
            elif len(self.domains[bestVar]) == len(self.domains[bestVar]):

                # how many intersects for current best var
                bestVarDegree = len([intersect for key, intersect in self.crossword.overlaps.items()
                    if intersect and bestVar in key])

                # how many intersects for compared var
                varDegree = len([intersect for key, intersect in self.crossword.overlaps.items()
                    if intersect and var in key])
                # take one with highest degree (equal then keep first one)
                if varDegree > bestVarDegree:
                    bestVar = var
        return bestVar

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        # next var to assign
        unassignedVar = self.select_unassigned_variable(assignment)
        # from best to worst options for unassignedVar's domain
        domainOptions = self.order_domain_values(unassignedVar, assignment)

        for option in domainOptions:
            # try an answer for var
            newAssignment = assignment.copy()
            newAssignment[unassignedVar] = option
            # if answer works:
            if self.consistent(newAssignment):
                # things that intersect with var answer
                checkArcs = {key for key in self.crossword.overlaps.keys()
                    if key and unassignedVar in key}
                # inferring process
                inferred = self.inference(newAssignment, checkArcs)
                if inferred:
                    newAssignment = inferred
                # continue search for answer
                result = self.backtrack(newAssignment)
                # found an answer for all vars
                if result is not None:
                    return result
        # no answers worked, no solution
        return None

    def inference(self, assignment, checkArcs):
        """inferring process while backtracking"""

        # copy of domains
        domainsCopy = self.domains.copy()

        # maintain arc consistency
        consistent = self.ac3(checkArcs)

        # didn't fail
        if consistent:
            # assignment with infers
            inferredAnswer = assignment.copy()

            # every var not assigned yet
            for unassigned in self.crossword.variables - assignment:

                # if only one answer can infer that must be the answer
                possibleWords = self.domains[unassigned]

                if len(possibleWords) == 1:
                    inferredAnswer[unassigned] = possibleWords[0]

            return inferredAnswers
        else:  # failed then revert domains            
            self.domains = domainsCopy
            return False

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

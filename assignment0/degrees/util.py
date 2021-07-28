class Node():
    def __init__(self, actor, parent, movie):
        # current actor id
        self.actor = actor
        # what actor they did the movie with (parent)
        self.parent = parent
        # the movie they were in
        self.movie = movie


class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, actor):
        return any(node.actor == actor for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

    def changeNodes(self, newNodes):
        if (type(newNodes) is list):
            self.frontier = newNodes
        else:
            raise Exception("Not of type list")

class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

    def firstNode(self):
        if self.frontier:
            return self.frontier[0]
        else:
            return None

# checks if node is the target
def isTarget(targetID, node):

    if node.actor == targetID:
        return True

# returns steps (movie and actor in it) from source to goal
def retraceSteps(node):

    steps = []
    while node is not None:
        steps.append((node.movie, node.actor))
        node = node.parent
    steps.reverse()
    return steps

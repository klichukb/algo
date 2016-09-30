"""
Red-Black Tree implementation.

Sources:
    Introduction to algorithms. Cormen, Leiserson, Rivest, Stein.
    Algorithms, #4 edition. Sedgewick, Wayne.
"""

BLACK = 0
RED = 1


LEFT = 0
RIGHT = 1

class Node(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.parent = None
        self.color = BLACK

    def set_left(self, node):
        self.left = node
        if node is not None: # null, nil
            node.parent = self

    def set_right(self, node):
        self.right = node
        if node is not None:
            node.parent = self

    def __repr__(self):
        return 'Node[{}]'.format(self.key)


class Tree(object):
    def __init__(self):
        self.root = None

    def insert(self, key, value):
        node = Node(key, value)
        current = self.root

        if self.root is None:
            self.root = node
            return node

        parent = None
        move = None
        while current is not None:
            parent = current
            if key < current.key:
                move = LEFT
                current = current.left
            else:
                move = RIGHT
                current = current.right

        if move == LEFT:
            parent.set_left(node)
        else:
            parent.set_right(node)

        return node

    def search(self, key):
        current = self.root

        while current is not None and key != current.key:
            if key < current.key:
                current = current.left
            elif key > current.key:
                current = current.right

        return current

    def change_parent(self, from_node, to_node):
        if from_node.parent is None:
            # set new root
            self.root = to_node
            if to_node:
                to_node.parent = None
        elif from_node.parent.left == from_node:
            from_node.parent.set_left(to_node)
        elif from_node.parent.right == from_node:
            from_node.parent.set_right(to_node)

    def find_min(self, in_node=None):
        # find_min() -> find minimum key in root
        # find_min(node) -> find minimum in `node`.
        current = in_node or self.root
        while current.left is not None:
            current = current.left
        return current


    def delete(self, node):
        if node is None:
            return False

        if node.left is None:
            # transplant right child.
            self.change_parent(node, node.right)
        elif node.right is None:
            # transplant left child.
            self.change_parent(node, node.left)
        else:
            right_min = self.find_min(node.right)

            if right_min.parent != node:
                self.change_parent(right_min, right_min.right)
                right_min.set_right(node.right)

            # restore
            self.change_parent(node, right_min)
            right_min.set_left(node.left)

        return True


def is_black(node):
    return node is None or node.color == BLACK


def is_red(node):
    return not is_black(node)


class RBTree(Tree):
    def insert(self, key, value):
        node = super().insert(key, value)
        node.color = RED
        self.insert_fixup(node)

    def rotate_left(self, node):
        if node.right is None:
            return
        #   |
        # (node)
        #   |
        #    |
        #    (top)
        # -------->
        #      |
        #    (top)
        #    |
        #   |
        # (node)
        top = node.right
        self.change_parent(node, top)
        node.set_right(top.left)
        top.set_left(node)

    def rotate_right(self, node):
        if node.left is None:
            return
        top = node.left
        self.change_parent(node, top)
        node.set_left(top.right)
        top.set_right(node)

    def insert_fixup(self, node):
        while is_red(node.parent):
            if node.parent == node.parent.parent.left:
                uncle = node.parent.parent.right
                if is_red(uncle):
                    # Case 1 (parent and uncle = RED)
                    uncle.color = BLACK
                    node.parent.color = BLACK
                    node.parent.parent.color = RED
                    node = node.parent.parent
                else:
                    if node == node.parent.right:
                        # right-leaning 2 red nodes
                        # Case 3
                        node = node.parent
                        self.rotate_left(node)

                    # Case 2 (uncle = RED, we are in left branch)
                    # left-leaning 2 red nodes
                    node.parent.color = BLACK
                    node.parent.parent.color = RED
                    self.rotate_right(node.parent.parent)
            else:
                uncle = node.parent.parent.left
                if is_red(uncle):
                    # Case 1 (parent and uncle = RED)
                    uncle.color = BLACK
                    node.parent.color = BLACK
                    node.parent.parent.color = RED
                    node = node.parent.parent
                else:
                    if node == node.parent.left:
                        # Case 3
                        node = node.parent
                        self.rotate_right(node)

                    # Case 2 (uncle = RED, we are in left branch)
                    node.parent.color = BLACK
                    node.parent.parent.color = RED
                    self.rotate_left(node.parent.parent)
        self.root.color = BLACK

    def delete(self, node):
        if node is None:
            return False

        moved_color = node.color

        if node.left is None:
            # transplant right child.
            culprit_node = node.right
            culprit_parent = node.parent
            self.change_parent(node, node.right)
        elif node.right is None:
            # transplant left child.
            culprit_node = node.left
            culprit_parent = node.parent
            self.change_parent(node, node.left)
        else:
            right_min = self.find_min(node.right)
            moved_color = right_min.color
            culprit_node = right_min.right

            if right_min.parent != node:
                self.change_parent(right_min, right_min.right)
                right_min.set_right(node.right)
                culprit_parent = right_min.parent
            else:
                culprit_parent = right_min

            # restore
            self.change_parent(node, right_min)
            right_min.set_left(node.left)
            right_min.color = node.color

        if moved_color == BLACK:
            self.delete_fixup(culprit_node, culprit_parent)

        return True

    def delete_fixup(self, node, parent):
        while node != self.root and is_black(node):
            if node:
                parent = node.parent
            if parent.left == node:
                w = parent.right
                if w is None:
                    node = parent
                    continue

                if is_red(w):
                    # Case 4
                    parent.color = RED
                    w.color = BLACK
                    self.rotate_left(parent)
                    w = parent.right

                if is_black(w.left) and is_black(w.right):
                    # Case 1
                    w.color = RED
                    node = parent
                else:
                    if is_black(w.right):
                        self.rotate_right(w)
                        w = parent.right
                    # Case 2
                    w.color = parent.color
                    parent.color = BLACK
                    if w.right is not None:
                        w.right.color = BLACK
                    self.rotate_left(parent)
                    break
            else:
                w = parent.left
                if w is None:
                    node = parent
                    continue

                if is_red(w):
                    # Case 4
                    parent.color = RED
                    w.color = BLACK
                    self.rotate_right(parent)
                    w = parent.left

                if is_black(w.left) and is_black(w.right):
                    # Case 1
                    w.color = RED
                    node = parent
                else:
                    if is_black(w.left):
                        self.rotate_left(w)
                        w = parent.left

                    # Case 2
                    if w.left is not None:
                        w.left.color = BLACK
                    w.color = parent.color
                    parent.color = BLACK
                    self.rotate_right(parent)
                    break
        if node is not None:
            node.color = BLACK



def main(size=100):
    # from visualize import plot_tree
    import random
    random.seed(8)

    keys = [random.randint(0, 1000) for i in range(size)]

    rb_tree = RBTree()
    tree = Tree()

    # Insertion:
    #
    # Regular Tree
    for i in keys:
        tree.insert(i, i)

    for i in keys:
        rb_tree.insert(i, i)

    # Deletion
    for i in reversed(keys):
        tree.delete(tree.search(i))

    for i in reversed(keys):
        rb_tree.delete(rb_tree.search(i))


main(size=1000)

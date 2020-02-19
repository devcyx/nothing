"""
Description:
Author: Alvin yx
Action      Date        Content
------------------------------------
Create      2019-
"""


class Node(object):

    def __init__(self, item):
        self.item = item
        self.lbranch = None
        self.rbranch = None
        # self.item.lbranch = None
        # self.item.rbranch = None


class Tree(object):
    def __init__(self):
        self.root = None

    def add(self, val):
        node = Node(val)
        if self.root is None:
            self.root = node
            return
        queue = [self.root]
        while queue:
            root = queue.pop(0)
            if root.lbranch is None:
                root.lbranch = node
                return
            else:
                queue.append(root.lbranch)

            if root.rbranch is None:
                root.rbranch = node
                return
            else:
                queue.append(root.rbranch)

    def priority(self, item):
        if item is None:
            return
        print(item.item, end=" ")
        self.priority(item.lbranch)
        self.priority(item.rbranch)

    def inorder(self, item):
        if item is None:
            return
        self.inorder(item.lbranch)
        print(item.item, end=" ")
        self.inorder(item.rbranch)

    def postorder(self, item):
        if item is None:
            return
        self.postorder(item.lbranch)
        self.postorder(item.rbranch)
        print(item.item, end=" ")


if __name__ == '__main__':
    tree = Tree()
    tree.add(0)
    tree.add(1)
    tree.add(2)
    tree.add(3)
    tree.add(4)
    tree.add(5)
    tree.add(6)
    tree.add(7)
    tree.add(8)
    tree.add(9)
    print("前序：", end="  ")
    tree.priority(tree.root)
    print("")
    print("中序：", end="  ")
    tree.inorder(tree.root)
    print("")
    print("后序：", end="  ")
    tree.postorder(tree.root)

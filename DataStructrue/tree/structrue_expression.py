"""
Description:树结构的表示法
Author: Alvin yx
Action      Date        Content
------------------------------------
Create      2020-02-24
"""


class Parents(object):
    """
    双亲表示法
    每一个节点都有一个指针指向双亲节点
    如果想找到孩子节点  得遍历才行  可以设置一个长子域指向该节点的第一个子节点  若无为-1
    """

    def __init__(self, val, parent, firstChild = -1):
        self.val = val
        self.parent = parent
        self.firstChild = firstChild


class Children(object):
    """
    孩子表示法
    每一个节点都有一个指针指向双亲节点
    如果想找到孩子节点  得遍历才行  可以设置一个长子域指向该节点的第一个子节点  若无为-1
    """

    def __init__(self, val, parent, firstChild = -1):
        self.val = val
        self.parent = parent
        self.firstChild = firstChild


class Brother(object):
    """
    兄弟表示法  这个方法将一个复杂树转换成了一个二叉树
    1.每一个节点都有一个指针指向第一个子节点
    2.每一个节点都有一个指针指向右边的兄弟节点（如果有兄弟节点）
    """

    def __init__(self, val, first_child, right_bro=-1):
        self.val = val
        self.first_child = first_child
        self.right_bro = right_bro

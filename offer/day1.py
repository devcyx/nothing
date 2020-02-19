"""
Description:
Author: Alvin yx
Action      Date        Content
------------------------------------
Create      2019-11-07  Add
"""

# 如题
# -*- coding:utf-8 -*-


class TreeNode:
    def __init__(self, x):
        self.val = x
        self.left = None
        self.right = None


class Solution:
    # 返回构造的TreeNode根节点
    def reConstructBinaryTree(self, pre, tin):
        # write code here
        if not pre or not tin:
            return None
        else:
            self.a(pre)

    def a(self):
        pass


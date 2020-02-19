"""
Description:栈
Author: Alvin yx
Action      Date        Content
------------------------------------
Create      2019-10-29  Add
"""
import re


class Stack(object):
    """栈"""
    def __init__(self):
        self.stack_list = []

    def push(self, item):
        self.stack_list.append(item)

    def pop(self):
        return self.stack_list.pop() if self.stack_list else ""

    def peek(self):
        return self.stack_list[-1] if not self.isEmpty() else None

    def isEmpty(self):
        return True if self.stack_list == [] else False

    def size(self):
        return len(self.stack_list)


def postfix(expression):
    """
    :description 转换中缀表达式为后缀表达式
    :param expression: 中缀表达式
    :return: 后缀表达式
    """
    priority = {
        "*": 3
        , "/": 3
        , "-": 2
        , "+": 2
        , "(": 1
        , ")": 1
    }
    # expression "A+B+C*(A+V+D)"
    nifix_expression = expression.split(" ")
    stack = Stack()
    postfix_expression = []
    # 循环中缀表达式
    for tag in nifix_expression:
        if re.match(r'[a-zA-z0-9]', tag):
            postfix_expression.append(tag)
        elif tag == "(":
            stack.push(tag)
        elif tag == ")":
            while stack.peek() != "(":
                postfix_expression.append(stack.pop())
            stack.pop()
        else:
            while not stack.isEmpty() and priority.get(tag) < priority.get(stack.peek(), 0):
                postfix_expression.append(stack.pop())
            else:
                stack.push(tag)
    while not stack.isEmpty():
        postfix_expression.append(stack.pop())

    return " ".join(postfix_expression)


def calculator(expression):
    params = expression.split(" ")
    stack = Stack()
    for tag in params:
        if re.match(r'\d+', tag):
            stack.push(tag)
        else:
            two = stack.pop()
            one = stack.pop()
            stack.push(eval(f"{one}{tag}{two}"))
    return stack.pop()


if __name__ == '__main__':
    print(eval("400 + 600 / 3 + 4 - ( 2 * 5 + 4 + 6 )"))
    print(calculator(postfix("400 + 600 / 3 + 4 - ( 2 * 5 + 4 + 6 )")))


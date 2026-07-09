from contextlib import contextmanager


class OutputBuffer:
    __INDENTATION_INCREMENT = 4

    def __init__(self):
        self.__indentation = 0
        self.__indentation_enabled = True
        self.__buffer: str = ""

    def reset(self) -> None:
        self.__indentation = 0
        self.__indentation_enabled = True
        self.__buffer: str = ""

    def print(self) -> None:
        print(self.__buffer)
        self.__buffer = ""

    def push(self, data: str) -> None:
        self.__buffer += data

    def indented_push(self, data: str) -> None:
        if self.__indentation_enabled:
            self.__buffer += ' ' * self.__indentation
        self.push(data)

    def push_indent(self) -> None:
        self.__indentation += self.__INDENTATION_INCREMENT

    def pop_indent(self) -> None:
        if self.__indentation > 0:
            self.__indentation -= self.__INDENTATION_INCREMENT

    def disable_indentation(self) -> None:
        self.__indentation_enabled = False

    def enable_indentation(self) -> None:
        self.__indentation_enabled = True

    @contextmanager
    def disabled_indentation(self):
        self.disable_indentation()
        yield
        self.enable_indentation()

    @contextmanager
    def scoped_indent(self):
        self.push_indent()
        yield
        self.pop_indent()

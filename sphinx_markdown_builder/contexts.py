"""
Context handlers.
"""
from tabulate import tabulate


class SubContext:
    def __init__(self, node):
        self.node = node
        self.body = []

    def add(self, value: str):
        self.body.append(value)

    def make(self):
        return "".join(self.body)


class AnnotationContext(SubContext):
    def make(self):
        content = super().make()
        # We want to make the text italic. We need to make sure the _ mark is near a non-space char,
        # but we want to preserve the existing spaces.
        prefix_spaces = len(content) - len(content.lstrip())
        suffix_spaces = len(content) - len(content.rstrip())
        annotation_mark = "_"
        content = (
            f"{annotation_mark:>{prefix_spaces + 1}}"
            f"{content[prefix_spaces:len(content) - suffix_spaces]}"
            f"{annotation_mark:<{suffix_spaces + 1}}"
        )
        return content


class TableContext(SubContext):
    def __init__(self, node):
        super().__init__(node)
        self.headers = []

        self.is_head = False
        self.is_body = False
        self.is_row = False
        self.is_entry = False

    @property
    def active_output(self):
        if self.is_head:
            return self.headers
        else:
            assert self.is_body
            return self.body

    def enter_head(self):
        assert not self.is_body
        self.is_head = True

    def exit_head(self):
        assert self.is_head
        self.is_head = False

    def enter_body(self):
        assert not self.is_head
        self.is_body = True

    def exit_body(self):
        assert self.is_body
        self.is_body = False

    def enter_row(self):
        assert self.is_head or self.is_body
        self.is_row = True
        self.active_output.append([])

    def exit_row(self):
        assert self.is_row
        self.is_row = False

    def enter_entry(self):
        assert self.is_row
        self.is_entry = True
        self.active_output[-1].append([])

    def exit_entry(self):
        assert self.is_entry
        self.is_entry = False

    def add(self, value: str):
        assert self.is_entry
        self.active_output[-1][-1].append(value)

    @staticmethod
    def make_row(row):
        return ["".join(entries) for entries in row]

    def make(self):
        if len(self.headers) == 0 and len(self.body) == 0:
            return ""

        if len(self.headers) == 0:
            headers = [""]
        else:
            assert len(self.headers) == 1
            headers = self.make_row(self.headers[0])

        body = list(map(self.make_row, self.body))
        return tabulate(body, headers=headers, tablefmt="github")

class Depth:
    depth = 0

    sub_depth = {}

    def get(self, name=None):
        if name:
            return self.sub_depth[name] if name in self.sub_depth else 0
        return depth

    def descend(self, name=None):
        self.depth = self.depth + 1
        if name:
            sub_depth = (
                self.sub_depth[name] if name in self.sub_depth else 0
            ) + 1
            self.sub_depth[name] = sub_depth
        return self.get(name)

    def ascend(self, name=None):
        self.depth = max(0, self.depth - 1)
        if name:
            sub_depth = max(
                0, (self.sub_depth[name] if name in self.sub_depth else 0) - 1
            )
            self.sub_depth[name] = sub_depth
        return self.get(name)

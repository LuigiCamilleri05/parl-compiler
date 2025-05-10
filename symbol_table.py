class SymbolTable:
    def __init__(self):
        # Each scope is a dict of variable name -> (type, index)
        self.scopes = [{}]  # Stack of scopes
        self.scope_levels = [0]  # Tracks base level of each scope
        self.current_level = 0
        self.index_stack = [0]  # Tracks the current index within each frame

    def enter_scope(self):
        self.scopes.append({})
        self.scope_levels.append(self.current_level)
        self.index_stack.append(0)
        self.current_level += 1

    def exit_scope(self):
        self.scopes.pop()
        self.scope_levels.pop()
        self.index_stack.pop()
        self.current_level -= 1

    def declare(self, name, typ):
        if name in self.scopes[-1]:
            raise Exception(f"Semantic Error: Variable '{name}' already declared in this scope.")
        index = self.index_stack[-1]
        self.scopes[-1][name] = (typ, index, self.current_level - 1)
        self.index_stack[-1] += 1

    def lookup(self, name):
        for level in range(len(self.scopes) - 1, -1, -1):
            if name in self.scopes[level]:
                return self.scopes[level][name]  # returns (type, index, level)
        raise Exception(f"Semantic Error: Variable '{name}' used before declaration.")
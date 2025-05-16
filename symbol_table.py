class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # Stack of scopes
        self.scope_levels = [0]
        self.current_level = 0
        self.index_stack = [0]

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

    def declare(self, name, typ, *, kind=None, size=None, values=None):
        if name in self.scopes[-1]:
            raise Exception(f"Semantic Error: Variable '{name}' already declared in this scope.")

        index = self.index_stack[-1]
        is_array = isinstance(typ, str) and typ.endswith("[]")
        slots = size if is_array else 1 
        self.scopes[-1][name] = {
            "type": typ,
            "index": index,
            "level": self.current_level - 1,
            "kind": kind or ("array" if is_array else "var"),
            "size": size,
            "values": values,
        }
        self.index_stack[-1] += slots

    def lookup(self, name):
        for level in range(len(self.scopes) - 1, -1, -1):
            if name in self.scopes[level]:
                entry = self.scopes[level][name]
                return entry["type"], entry["index"], entry["level"]
        raise Exception(f"Semantic Error: Variable '{name}' used before declaration.")

    def lookup_full(self, name):
        for level in range(len(self.scopes) - 1, -1, -1):
            if name in self.scopes[level]:
                return self.scopes[level][name]
        raise Exception(f"Semantic Error: Variable '{name}' used before declaration.")

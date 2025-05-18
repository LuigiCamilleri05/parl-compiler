class SymbolTable:

    # This class implements a symbol table for managing variable declarations
    def __init__(self):
        self.scopes = [{}]  # Stack of scopes
        self.scope_levels = [0] # Stack of scope levels
        self.index_stack = [0] # Stack of indices for each scope
        self.current_level = 0 # Number of current scope level

    # This method is called when entering a new scope
    def enter_scope(self):
        self.scopes.append({}) # Creates a new scope
        self.scope_levels.append(self.current_level) # Stores number of the current level
        self.index_stack.append(0) # Initialize index for the new scope
        self.current_level += 1 # Increments the current level

    # This method is called when exiting a scope
    def exit_scope(self):
        self.scopes.pop() # Removes the current scope
        self.scope_levels.pop() # Removes the number of previous level
        self.index_stack.pop() # Removes the index of the previous scope
        self.current_level -= 1 # Decrements the current level

    # This method is called to declare a variable or function in the current scope
    def declare(self, name, typ, *, kind=None, size=None, values=None):

        # Checks if the name has already been declared in the current scope
        if name in self.scopes[-1]:
            raise Exception(f"Semantic Error: Variable '{name}' already declared in this scope.")

        # Gets the last index of the current scope
        index = self.index_stack[-1]

        # Flag to check if the type is an array
        is_array = isinstance(typ, str) and typ.endswith("[]")

        # Allocated the amount of slots based on the type
        slots = size if is_array else 1

        # Assigns all details about the variable to the symbol table 
        self.scopes[-1][name] = {
            "type": typ,
            "index": index,
            "level": self.current_level - 1,
            "kind": kind or ("array" if is_array else "var"),
            "size": size,
            "values": values,
        }

        # Updates the index after the allocated slot/s
        self.index_stack[-1] += slots

    # This method is called to look up where a variable or function has been declared in the symbol table
    def lookup(self, name):

        # Checks if the name has been used before declaration
        # It checks by starting from the last scope (global) and goes backwards
        for level in range(len(self.scopes) - 1, -1, -1):
            if name in self.scopes[level]:
                return self.scopes[level][name]
        raise Exception(f"Semantic Error: Variable '{name}' used before declaration.")

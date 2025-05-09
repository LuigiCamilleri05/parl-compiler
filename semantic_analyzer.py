class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # list of dictionaries, one per scope

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        self.scopes.pop()

    def declare(self, name, typ):
        if name in self.scopes[-1]:
            raise Exception(f"Semantic Error: Variable '{name}' already declared in this scope.")
        self.scopes[-1][name] = typ

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Semantic Error: Variable '{name}' used before declaration.")


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_return_type = None

    def visit_block_node(self, node):
        self.symbol_table.enter_scope()
        for stmt in node.stmts:
            stmt.accept(self)
        self.symbol_table.exit_scope()

    def visit_variable_decl_node(self, node):
        var_type = node.vartype
        self.symbol_table.declare(node.identifier, var_type)

        expr_type = node.expr.accept(self)
        if expr_type != var_type:
            raise Exception(f"Type Error: Cannot assign {expr_type} to variable of type {var_type}")

    def visit_variable_node(self, node):
        return self.symbol_table.lookup(node.lexeme)

    def visit_integer_node(self, node):
        return "int"

    def visit_float_node(self, node):
        return "float"

    def visit_boolean_node(self, node):
        return "bool"

    def visit_colour_node(self, node):
        return "colour"

    def visit_assignment_node(self, node):
        var_type = node.id.accept(self)
        expr_type = node.expr.accept(self)
        if var_type != expr_type:
            raise Exception(f"Type Error: Cannot assign {expr_type} to variable of type {var_type}")

    def visit_binary_op_node(self, node):
        left_type = node.left.accept(self)
        right_type = node.right.accept(self)

        if left_type != right_type:
            raise Exception(f"Type Error: Mismatched operands: {left_type} and {right_type}")

        if node.op in ["+", "-", "*", "/"]:
            if left_type not in ["int", "float"]:
                raise Exception(f"Type Error: Arithmetic operator '{node.op}' requires int or float operands")
            return left_type

        elif node.op in ["<", ">", "<=", ">=", "==", "!="]:
            return "bool"  # Comparison always returns bool

        elif node.op in ["and", "or"]:
            if left_type != "bool":
                raise Exception(f"Type Error: Logical operator '{node.op}' requires bool operands")
            return "bool"

        else:
            raise Exception(f"Semantic Error: Unknown binary operator '{node.op}'")

    def visit_unary_op_node(self, node):
        operand_type = node.operand.accept(self)

        if node.op == "not":
            if operand_type != "bool":
                raise Exception("Type Error: 'not' operator requires a boolean operand")
            return "bool"

        elif node.op == "-":
            if operand_type not in {"int", "float"}:
                raise Exception("Type Error: Unary '-' operator requires int or float operand")
            return operand_type

        else:
            raise Exception(f"Semantic Error: Unknown unary operator '{node.op}'")

    def visit_if_node(self, node):
        cond_type = node.condition_expr.accept(self)
        if cond_type != "bool":
            raise Exception("Type Error: Condition of 'if' must be boolean")
        node.then_block.accept(self)
        if node.else_block:
            node.else_block.accept(self)

    def visit_rtrn_node(self, node):
        expr_type = node.expr.accept(self)
        if expr_type != self.current_return_type:
            raise Exception(f"Type Error: Return type {expr_type} does not match function return type {self.current_return_type}")

    def visit_function_decl_node(self, node):
        # Store function signature in the global scope
        self.symbol_table.declare(node.name, {
            'type': node.return_type,
            'kind': 'function',
            'params': node.params,  # list of (name, type, size)
            'return_type': node.return_type
        })

        self.symbol_table.enter_scope()

        # Declare each parameter in the function's scope
        for name, typ, _ in node.params:
            self.symbol_table.declare(name, typ)

        self.current_return_type = node.return_type
        node.body.accept(self)

        self.symbol_table.exit_scope()

    def visit_function_call_node(self, node):
        # Check if function is declared
        func_entry = self.symbol_table.lookup(node.func_name)
        if func_entry is None:
            self.error(f"Function '{node.func_name}' not declared before use.")
            return None

        # Check that it is a function
        if func_entry['kind'] != 'function':
            self.error(f"Identifier '{node.func_name}' is not a function.")
            return None

        # Check argument count
        expected_params = func_entry['params']
        if len(expected_params) != len(node.args):
            self.error(f"Function '{node.func_name}' expects {len(expected_params)} argument(s), got {len(node.args)}.")
            return func_entry['return_type']

        # Check each argument's type
        for (arg_node, (param_name, param_type, _)) in zip(node.args, expected_params):
            arg_type = arg_node.accept(self)
            if arg_type != param_type:
                self.error(f"In call to '{node.func_name}', expected type '{param_type}' for argument '{param_name}', got '{arg_type}'.")

        return func_entry['return_type']
    
    def visit_while_node(self, node):
        # Check condition expression type
        condition_type = node.condition.accept(self)
        if condition_type != "bool":
            self.error(f"Type Error: While loop condition must be 'bool', got '{condition_type}'")

        # Enter loop body scope and analyze contents
        self.symbol_table.enter_scope()
        node.body.accept(self)
        self.symbol_table.exit_scope()

    def visit_for_node(self, node):
        self.symbol_table.enter_scope()

        # Check optional initializer (must be a variable declaration)
        if node.init:
            node.init.accept(self)

        # Check condition (must return bool)
        if node.condition:
            cond_type = node.condition.accept(self)
            if cond_type != "bool":
                raise Exception(f"Type Error: for-loop condition must be 'bool', got '{cond_type}'")

        # Check optional update (e.g., assignment)
        if node.update:
            node.update.accept(self)

        # Visit loop body
        node.body.accept(self)

        self.symbol_table.exit_scope()

    def visit_print_node(self, node):
        # No specific type requirement for print — any type is fine
        node.expr.accept(self)

    def visit_delay_node(self, node):
        delay_type = node.expr.accept(self)
        if delay_type != "int":
            raise Exception(f"Type Error: __delay expects 'int', got '{delay_type}'")

    def visit_write_node(self, node):
        x_type = node.x_expr.accept(self)
        y_type = node.y_expr.accept(self)
        val_type = node.val_expr.accept(self)

        if x_type != "int":
            raise Exception(f"Type Error: __write expects int for x, got '{x_type}'")
        if y_type != "int":
            raise Exception(f"Type Error: __write expects int for y, got '{y_type}'")
        if val_type != "colour":
            raise Exception(f"Type Error: __write expects colour value, got '{val_type}'")
        
    def visit_write_box_node(self, node):
        x_type = node.x_expr.accept(self)
        y_type = node.y_expr.accept(self)
        w_type = node.w_expr.accept(self)
        h_type = node.h_expr.accept(self)
        val_type = node.val_expr.accept(self)

        for label, typ in zip(["x", "y", "width", "height"], [x_type, y_type, w_type, h_type]):
            if typ != "int":
                raise Exception(f"Type Error: __write_box expects int for {label}, got '{typ}'")

        if val_type != "colour":
            raise Exception(f"Type Error: __write_box expects colour value, got '{val_type}'")


    def error(self, message):
        raise Exception(f"Semantic Error: {message}")
    
    

    # You would also implement other node visit methods as needed, like for loops, while, cast, etc.

    # Helper: for all `accept()` calls, the return value should be the inferred type where relevant

from astnodes import ASTIfNode, ASTRtrnNode, ASTWhileNode, ASTBlockNode, ASTVariableDeclNode, ASTFunctionDeclNode, ASTArrayDeclNode, ASTIntegerNode, ASTForNode
from symbol_table import SymbolTable

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
        entry = self.symbol_table.lookup_full(node.lexeme)
        var_type = entry["type"]

        if node.index_expr is not None:
            if not var_type.endswith("[]"):
                raise Exception(f"Type Error: Variable '{node.lexeme}' is not an array")
            idx_type = node.index_expr.accept(self)
            if idx_type != "int":
                raise Exception("Type Error: Array index must be an integer")
            return var_type[:-2]



        return var_type
    def visit_pad_width_node(self, node):
        # PAD width is always an integer
        return "int"

    def visit_pad_height_node(self, node):
        # PAD height is always an integer
        return "int"

    def visit_pad_read_node(self, node):
        # Both x and y coordinates must be int
        y_type = node.expr2.accept(self)
        x_type = node.expr1.accept(self)

        if x_type != "int":
            raise Exception(f"Type Error: __read expects int for x, got {x_type}")
        if y_type != "int":
            raise Exception(f"Type Error: __read expects int for y, got {y_type}")

        return "colour"  # __read returns a colour value

    def visit_pad_rand_int_node(self, node):
        bound_type = node.expr.accept(self)
        if bound_type != "int":
            raise Exception(f"Type Error: __random_int expects an int, got {bound_type}")
        return "int"


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
        right_type = node.right.accept(self)
        left_type = node.left.accept(self)
        
        if left_type != right_type:
            raise Exception(f"Type Error: Mismatched operands: {left_type} and {right_type}")

        if node.op in ["+", "-", "*", "/"]:
            if left_type not in ["int", "float"]:
                raise Exception(f"Type Error: Arithmetic operator '{node.op}' requires int or float operands")
            return left_type

        elif node.op in ["<", ">", "<=", ">=", "==", "!="]:
            return "bool"

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
        
    def visit_cast_node(self, node):
        expr_type = node.expr.accept(self)
        target_type = node.target_type

        valid_types = {"int", "float", "bool", "colour"}
        if target_type not in valid_types:
            raise Exception(f"Type Error: Unknown cast target type '{target_type}'")

        # Disallow only nonsense conversions (like colour <-> bool)
        disallowed_casts = {
            ("bool", "colour"), ("colour", "bool")
        }

        if (expr_type, target_type) in disallowed_casts:
            raise Exception(f"Type Error: Cannot cast from {expr_type} to {target_type}")

        return target_type
    
    def visit_array_decl_node(self, node):
        # Must end in []
        if not node.vartype.endswith("[]"):
            raise Exception(f"Type Error: Array declaration must use an array type, got '{node.vartype}'")

        base_type = node.vartype[:-2]  # e.g., "int" from "int[]"

        # Declare the variable in the symbol table
        self.symbol_table.declare(
                node.identifier,
                node.vartype,
                size=len(node.values),
                values=node.values
            )

        # Check the type of the size expression
        if node.size_expr:
            size_type = node.size_expr.accept(self)
            if size_type != "int":
                raise Exception("Type Error: Array size must be of type 'int'")

        # Check each value's type
        for val in reversed(node.values):
            val_type = val.accept(self)
            if val_type != base_type:
                raise Exception(
                    f"Type Error: Array '{node.identifier}' expects elements of type '{base_type}', got '{val_type}'"
                )


    def visit_if_node(self, node):
        cond_type = node.condition_expr.accept(self)
        if cond_type != "bool":
            raise Exception("Type Error: Condition in 'if' must be boolean")
        if node.else_block:
            node.else_block.accept(self)

            node.then_block.accept(self)
        else:
            node.then_block.accept(self)
    def visit_function_decl_node(self, node):
        if len(self.symbol_table.scopes) != 2:
            raise Exception("Semantic Error: Functions must be declared in the global scope.")
        self.symbol_table.declare(node.name, {
                'type': node.return_type,
                'kind': 'function',
                'params': node.params,
                'return_type': node.return_type
            })

        self.symbol_table.enter_scope()

        for name, typ, size_expr in node.params:
            if isinstance(typ, str) and typ.endswith("[]"):
                # Determine size from literal size expression (assumes ASTIntegerNode)
                if isinstance(size_expr, ASTIntegerNode):
                    size = int(size_expr.value)
                else:
                    raise Exception(f"Semantic Error: Array parameter '{name}' must have a constant size.")
                self.symbol_table.declare(name, typ, size=size)
            else:
                self.symbol_table.declare(name, typ)

        self.current_return_type = node.return_type
        num_locals = self.count_local_vars(node.body)
        for name, typ, size_expr in node.params:
            if isinstance(typ, str) and typ.endswith("[]"):
                if isinstance(size_expr, ASTIntegerNode):
                    num_locals += int(size_expr.value)
            else:
                num_locals += 1

        for stmt in node.body.stmts:
            stmt.accept(self)
        self.symbol_table.exit_scope()

        if not self.does_block_always_return(node.body):
            raise Exception(f"Semantic Error: Function '{node.name}' may not return a value on all paths.")


    def visit_function_call_node(self, node):
        # Check if function is declared
        entry = self.symbol_table.lookup_full(node.func_name)
        func_entry = entry["type"]
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

        for (arg_node, (param_name, param_type, _)) in zip(node.args, expected_params):
            if param_type.endswith("[]"):
                # This is an array parameter
                entry = self.symbol_table.lookup_full(arg_node.lexeme)
            else:
                arg_type = arg_node.accept(self)
                if arg_type != param_type:
                    self.error(f"In call to '{node.func_name}', expected type '{param_type}' for argument '{param_name}', got '{arg_type}'.")

        return func_entry['return_type']
    
    def visit_while_node(self, node):
        cond_type = node.condition.accept(self)
        if cond_type != "bool":
            raise Exception("Type Error: Condition in 'while' must be boolean")

        node.body.accept(self)

    def visit_for_node(self, node):
        self.symbol_table.enter_scope()

        if node.init:
            node.init.accept(self)

        if node.condition:
            cond_type = node.condition.accept(self)
            if cond_type != "bool":
                raise Exception(f"Type Error: for-loop condition must be 'bool', got '{cond_type}'")
        else:
            raise Exception("Syntax Error: for-loop requires a condition")
        node.body.accept(self)

        # 7. Emit update (e.g., i = i + 1)
        if node.update:
            node.update.accept(self)



        self.symbol_table.exit_scope()

    def visit_print_node(self, node):
        node.expr.accept(self)

    def visit_delay_node(self, node):
        delay_type = node.expr.accept(self)
        if delay_type != "int":
            raise Exception(f"Type Error: __delay expects 'int', got '{delay_type}'")
        
    def visit_clear_node(self, node):
        clear_type = node.expr.accept(self)
        if clear_type != "colour":
            raise Exception(f"Type Error: __clear expects 'colour', got '{clear_type}'")

    def visit_write_node(self, node):
        val_type = node.val_expr.accept(self)
        y_type = node.y_expr.accept(self)
        x_type = node.x_expr.accept(self)

        if x_type != "int":
            raise Exception(f"Type Error: __write expects int for x, got '{x_type}'")
        if y_type != "int":
            raise Exception(f"Type Error: __write expects int for y, got '{y_type}'")
        if val_type != "colour":
            raise Exception(f"Type Error: __write expects colour value, got '{val_type}'")
        
    def visit_write_box_node(self, node):
        val_type = node.val_expr.accept(self)
        h_type = node.h_expr.accept(self)
        w_type = node.w_expr.accept(self)
        y_type = node.y_expr.accept(self)
        x_type = node.x_expr.accept(self)

        for label, typ in zip(["x", "y", "width", "height"], [x_type, y_type, w_type, h_type]):
            if typ != "int":
                raise Exception(f"Type Error: __write_box expects int for {label}, got '{typ}'")

        if val_type != "colour":
            raise Exception(f"Type Error: __write_box expects colour value, got '{val_type}'")

    def visit_rtrn_node(self, node):
        if self.current_return_type is None:
            raise Exception("Semantic Error: 'return' statement outside of function.")

        expr_type = node.expr.accept(self)
        if expr_type != self.current_return_type:
            raise Exception(
                f"Type Error: Return type '{expr_type}' does not match expected function return type '{self.current_return_type}'"
            )

    def visit_program_node(self, node):

        # Emit code for .main logic
        self.symbol_table.enter_scope()
        # Emit stack frame setup for main block
        num_main_vars = 0
        for stmt in node.stmts:
            if isinstance(stmt, ASTVariableDeclNode) or isinstance(stmt, ASTFunctionDeclNode):
                num_main_vars += 1
            elif isinstance(stmt, ASTArrayDeclNode):
                # account for array reference slot
                if stmt.size_expr:
                    if isinstance(stmt.size_expr, ASTIntegerNode):
                        num_main_vars += int(stmt.size_expr.value)
                    else:
                        raise Exception("Semantic Error: Array size must be a constant integer in global scope.")
                else:
                    num_main_vars += len(stmt.values)

        for stmt in node.stmts:
            stmt.accept(self)

        self.symbol_table.exit_scope()
    def does_block_always_return(self, block_node):
        """
        Determines whether all control paths in this block lead to a return.
        """
        for stmt in block_node.stmts:
            if isinstance(stmt, ASTRtrnNode):
                return True
            elif isinstance(stmt, ASTIfNode):
                then_returns = self.does_block_always_return(stmt.then_block)
                else_returns = self.does_block_always_return(stmt.else_block) if stmt.else_block else False
                if then_returns and else_returns:
                    return True
            elif isinstance(stmt, ASTWhileNode):
                # Loops might not run, so we can't guarantee a return
                continue
            elif isinstance(stmt, ASTBlockNode):
                if self.does_block_always_return(stmt):
                    return True
        return False
    
    def count_local_vars(self, block):
        count = 0
        for stmt in block.stmts:
            if isinstance(stmt, ASTVariableDeclNode):
                count += 1
            elif isinstance(stmt, ASTArrayDeclNode):
                if stmt.size_expr and isinstance(stmt.size_expr, ASTIntegerNode):
                    count += int(stmt.size_expr.value)
                else:
                    count += len(stmt.values)
            elif isinstance(stmt, ASTBlockNode):
                count += self.count_local_vars(stmt)
            elif isinstance(stmt, ASTIfNode):
                count += self.count_local_vars(stmt.then_block)
                if stmt.else_block:
                    count += self.count_local_vars(stmt.else_block)
            elif isinstance(stmt, ASTWhileNode) or isinstance(stmt, ASTForNode):
                count += self.count_local_vars(stmt.body)
        return count

    def error(self, message):
        raise Exception(f"Semantic Error: {message}")
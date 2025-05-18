# astnodes used in various places to check types
from astnodes import ASTIfNode, ASTRtrnNode, ASTWhileNode, ASTBlockNode, ASTVariableDeclNode, ASTFunctionDeclNode, ASTArrayDeclNode, ASTIntegerNode, ASTForNode
# Used for declarations, lookups, and scope management
from symbol_table import SymbolTable

# This class implements a semantic analyzer for PARl
class SemanticAnalyzer:

    # Initializes the semantic analyzer with a symbol table and current return type
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_return_type = None

    # This method is called to check if a block always returns a value
    def does_block_always_return(self, block_node):

        for stmt in block_node.stmts:

            # If a return statement is found, checking stops
            if isinstance(stmt, ASTRtrnNode):
                return True
            
            # Checks recursively for return statements in blocks in if statements
            elif isinstance(stmt, ASTIfNode):
                then_returns = self.does_block_always_return(stmt.then_block)
                else_returns = self.does_block_always_return(stmt.else_block) if stmt.else_block else False
                if then_returns and else_returns:
                    return True
                
            # Loops might not run, so we can't guarantee a return
            elif isinstance(stmt, ASTWhileNode) or isinstance(stmt, ASTForNode):
                continue

            # Checks for blocks within blocks
            elif isinstance(stmt, ASTBlockNode):
                if self.does_block_always_return(stmt):
                    return True
                
        # If loop finishes and nothing is returned, return False        
        return False
    
    # This method counts the number of local variables in a block by declarations
    # It goes recursively through the block's statements into nested blocks if needed
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
    
    # Visitor methods below implement type-checking rules for AST node types

    def visit_boolean_node(self, node):
        return "bool"

    def visit_integer_node(self, node):
        return "int"

    def visit_float_node(self, node):
        return "float"

    def visit_colour_node(self, node):
        return "colour"
    
    # __width, __height, and __random_int nodes always evaluate to integers
    def visit_pad_width_node(self, node):
        return "int"
 
    def visit_pad_height_node(self, node):
        return "int"

    def visit_pad_read_node(self, node):
        
        # Checks if the expressions are integers
        y_type = node.expr2.accept(self)
        x_type = node.expr1.accept(self)
        if x_type != "int":
            raise Exception(f"Type Error: __read expects int for x, got {x_type}")
        if y_type != "int":
            raise Exception(f"Type Error: __read expects int for y, got {y_type}")

        return "colour"  # returns a colour type

    def visit_pad_rand_int_node(self, node):
        bound_type = node.expr.accept(self)
        if bound_type != "int":
            raise Exception(f"Type Error: __random_int expects an int, got {bound_type}")
        return "int"

    def visit_binary_op_node(self, node):

        # Checks if right and left are the same type
        right_type = node.right.accept(self)
        left_type = node.left.accept(self)
        if left_type != right_type:
            raise Exception(f"Type Error: Mismatched operands: {left_type} and {right_type}")

        # Checks if the operator is valid and returns the correct type
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
        
    def visit_function_call_node(self, node):

        # Checks if function was declared and gets type
        entry = self.symbol_table.lookup(node.func_name)
        func_entry = entry["type"]
        if func_entry is None:
            raise Exception(f"Function '{node.func_name}' not declared before use.")

        # Checks that it is a function
        if func_entry['kind'] != 'function':
            raise Exception(f"Identifier '{node.func_name}' is not a function.")

        # Checks if the argument count is correct
        expected_params = func_entry['params']
        if len(expected_params) != len(node.args):
            raise Exception(f"Function '{node.func_name}' expects {len(expected_params)} argument(s), got {len(node.args)}.")

        # Loop which check if the arguments are arrays and if the types are correct
        for (arg_node, (param_name, param_type, _)) in zip(node.args, expected_params):
            if param_type.endswith("[]"):
                # This is an array parameter
                self.symbol_table.lookup(arg_node.lexeme)
            else:
                arg_type = arg_node.accept(self)
                if arg_type != param_type:
                    raise Exception(f"In call to '{node.func_name}', expected type '{param_type}' for argument '{param_name}', got '{arg_type}'.")

        # Returns the function's return type
        return func_entry['return_type']
    
    # Type checking for unary operations
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

    # Type checking for assignment nodes
    def visit_assignment_node(self, node):
        var_type = node.id.accept(self)
        expr_type = node.expr.accept(self)
        if var_type != expr_type:
            raise Exception(f"Type Error: Cannot assign {expr_type} to variable of type {var_type}")
        
    # Type checking for cast nodes    
    def visit_cast_node(self, node):
        expr_type = node.expr.accept(self)
        target_type = node.target_type

        valid_types = {"int", "float", "bool", "colour"}
        if target_type not in valid_types:
            raise Exception(f"Type Error: Unknown cast target type '{target_type}'")

        # Does not allow casting between incompatible types
        disallowed_casts = {
            ("bool", "colour"), ("colour", "bool")
        }

        if (expr_type, target_type) in disallowed_casts:
            raise Exception(f"Type Error: Cannot cast from {expr_type} to {target_type}")

        return target_type

    # Declares a variable in the symbol table and checks if the type of the expression 
    # is the same as the type of the variable
    def visit_variable_decl_node(self, node):
        var_type = node.vartype
        self.symbol_table.declare(node.identifier, var_type)

        expr_type = node.expr.accept(self)
        if expr_type != var_type:
            raise Exception(f"Type Error: Cannot assign {expr_type} to variable of type {var_type}")

    # Gets the type of the variable
    def visit_variable_node(self, node):
        entry = self.symbol_table.lookup(node.lexeme)
        var_type = entry["type"]

        # index_expr is used for arrays
        if node.index_expr is not None:
            if not var_type.endswith("[]"):
                raise Exception(f"Type Error: Variable '{node.lexeme}' is not an array")
            
            # Gets the type of the index expression
            idx_type = node.index_expr.accept(self)
            if idx_type != "int":
                raise Exception("Type Error: Array index must be an integer")
            
            # Returns the base type of the array without the []
            return var_type[:-2]

        return var_type
    
    # Checks the type of the array declaration
    def visit_array_decl_node(self, node):
        # Arrays must end in []
        if not node.vartype.endswith("[]"):
            raise Exception(f"Type Error: Array declaration must use an array type, got '{node.vartype}'")

        # Check if the base type is valid (without [])
        base_type = node.vartype[:-2]  # e.g., "int" from "int[]"

        # Declares the array in the symbol table
        self.symbol_table.declare(
                node.identifier,
                node.vartype,
                size=len(node.values), # size is the size of the array
                values=node.values
            )

        # Checks the type of the size expression
        if node.size_expr:
            size_type = node.size_expr.accept(self)
            if size_type != "int":
                raise Exception("Type Error: Array size must be of type 'int'")

        # Checks each value's type by iterating through the values
        # Reversed because of the way stack frames are created
        for val in reversed(node.values):
            val_type = val.accept(self)
            if val_type != base_type:
                raise Exception(
                    f"Type Error: Array '{node.identifier}' expects elements of type '{base_type}', got '{val_type}'"
                )

    # Goes to next expression
    def visit_print_node(self, node):
        node.expr.accept(self)

    # Checks the type of the delay node 
    def visit_delay_node(self, node):
        delay_type = node.expr.accept(self)
        if delay_type != "int":
            raise Exception(f"Type Error: __delay expects 'int', got '{delay_type}'")
        
    # Checks the type of the clear node    
    def visit_clear_node(self, node):
        clear_type = node.expr.accept(self)
        if clear_type != "colour":
            raise Exception(f"Type Error: __clear expects 'colour', got '{clear_type}'")

    # Checks the type of the write node
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

    # Checks the type of the write box node    
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

    # Checks the type of the return node
    def visit_rtrn_node(self, node):
        if self.current_return_type is None:
            raise Exception("Semantic Error: 'return' statement outside of function.")

        expr_type = node.expr.accept(self)
        if expr_type != self.current_return_type:
            raise Exception(
                f"Type Error: Return type '{expr_type}' does not match expected function return type '{self.current_return_type}'"
            )

    # Checks the type of the condition and goes into specific blocks
    def visit_if_node(self, node):
        cond_type = node.condition_expr.accept(self)
        if cond_type != "bool":
            raise Exception("Type Error: Condition in 'if' must be boolean")
        if node.else_block:
            node.else_block.accept(self)

            node.then_block.accept(self)
        else:
            node.then_block.accept(self)

    # Checks the type of the condition and starts an initalization, and updates accordingly 
    def visit_for_node(self, node):

        # (e.g. let u:int = 0;)
        if node.init:
            node.init.accept(self)

        # (e.g. i < 10;)
        if node.condition:
            cond_type = node.condition.accept(self)
            if cond_type != "bool":
                raise Exception(f"Type Error: for-loop condition must be 'bool', got '{cond_type}'")
        else:
            raise Exception("Syntax Error: for-loop requires a condition")
        node.body.accept(self)

        # (e.g. i = i + 1)
        if node.update:
            node.update.accept(self)

    # Checks the type of the condition and goes into specific blocks
    def visit_while_node(self, node):

        cond_type = node.condition.accept(self)
        if cond_type != "bool":
            raise Exception("Type Error: Condition in 'while' must be boolean")

        node.body.accept(self)

    
    def visit_function_decl_node(self, node):

        # Check if the function is declared in the global scope
        if len(self.symbol_table.scopes) != 1:
            raise Exception("Semantic Error: Functions must be declared in the global scope.")
        
        # Declares the function in the symbol table with the parameters
        self.symbol_table.declare(node.name, {
                'type': node.return_type,
                'kind': 'function',
                'params': node.params,
                'return_type': node.return_type
            })

        # Enters a new scope for the function body
        self.symbol_table.enter_scope()

        # If the parameter is an array, extract its declared size for validation.
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

        # Assigns the current return type from the function
        self.current_return_type = node.return_type

        # Checks the types in the functions body
        for stmt in node.body.stmts:
            stmt.accept(self)
        self.symbol_table.exit_scope()

        # Checks if the function always returns a value
        if not self.does_block_always_return(node.body):
            raise Exception(f"Semantic Error: Function '{node.name}' may not return a value on all paths.")

    # Goes through the statements in the block creating and closing a new scope
    def visit_block_node(self, node):
        self.symbol_table.enter_scope()
        for stmt in node.stmts:
            stmt.accept(self)
        self.symbol_table.exit_scope()

    # Entry point for semantic analysis; visits all top-level program statements
    def visit_program_node(self, node):

        # Loop checking if the array size is an integer
        for stmt in node.stmts:
            if isinstance(stmt, ASTArrayDeclNode) and stmt.size_expr and not isinstance(stmt.size_expr, ASTIntegerNode):
                raise Exception("Semantic Error: Array size must be a constant integer in global scope.")

        # Loops through the statements in the program
        for stmt in node.stmts:
            stmt.accept(self)

from astnodes import ASTIfNode, ASTRtrnNode, ASTWhileNode, ASTBlockNode, ASTVariableDeclNode, ASTFunctionDeclNode
from symbol_table import SymbolTable

class CodeGenerator:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_return_type = None
        self.instructions = []

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
        _, index, level = self.symbol_table.lookup(node.identifier)
        self.emit(f"push {index}")
        self.emit(f"push {level}")
        self.emit("st")

    def visit_variable_node(self, node):
        var_type, index, level = self.symbol_table.lookup(node.lexeme)
        if not getattr(self, "suppress_emit", False):
            self.emit(f"push [{index}:{level}]")
        return var_type
    
    def visit_pad_width_node(self, node):
        # PAD width is always an integer
        self.emit("width")
        return "int"

    def visit_pad_height_node(self, node):
        # PAD height is always an integer
        self.emit("height")
        return "int"

    def visit_pad_read_node(self, node):
        # Both x and y coordinates must be int
        y_type = node.expr2.accept(self)
        x_type = node.expr1.accept(self)
    
        if x_type != "int":
            raise Exception(f"Type Error: __read expects int for x, got {x_type}")
        if y_type != "int":
            raise Exception(f"Type Error: __read expects int for y, got {y_type}")
        self.emit("read")

        return "colour"  # __read returns a colour value

    def visit_pad_rand_int_node(self, node):
        bound_type = node.expr.accept(self)
        if bound_type != "int":
            raise Exception(f"Type Error: __random_int expects an int, got {bound_type}")
        self.emit("irnd")
        return "int"


    def visit_integer_node(self, node):
        self.emit(f"push {node.value}")
        return "int"

    def visit_float_node(self, node):
        self.emit(f"push {node.value}")
        return "float"

    def visit_boolean_node(self, node):
        if node.value:
            self.emit("push 1")
        else:
            self.emit("push 0")
        return "bool"

    def visit_colour_node(self, node):
        # Strip "#" and convert hex to int
        colour_int = int(node.value.lstrip("#"), 16)
        self.emit(f"push {colour_int}")
        return "colour"

    def visit_assignment_node(self, node):
        self.suppress_emit = True # Used to not emit the variable's value when assigning
        var_type = node.id.accept(self)
        self.suppress_emit = False

        expr_type = node.expr.accept(self)
        if var_type != expr_type:
            raise Exception(f"Type Error: Cannot assign {expr_type} to variable of type {var_type}")
        
            # Get index and level manually for the store
        _, index, level = self.symbol_table.lookup(node.id.lexeme)
        self.emit(f"push {index}")
        self.emit(f"push {level}")
        self.emit("st")

    def visit_binary_op_node(self, node):
        right_type = node.right.accept(self)
        left_type = node.left.accept(self)
        
        if left_type != right_type:
            raise Exception(f"Type Error: Mismatched operands: {left_type} and {right_type}")

        if node.op in ["+", "-", "*", "/"]:
            if left_type not in ["int", "float"]:
                raise Exception(f"Type Error: Arithmetic operator '{node.op}' requires int or float operands")
            if node.op == "+":
                self.emit("add")
            elif node.op == "-":
                self.emit("sub")
            elif node.op == "*":
                self.emit("mul")
            elif node.op == "/":
                self.emit("div")
            
            return left_type

        elif node.op in ["<", ">", "<=", ">=", "==", "!="]:
            if node.op == "<":
                self.emit("lt")
            elif node.op == "<=":
                self.emit("le")
            elif node.op == "==":
                self.emit("eq")
            elif node.op == "!=":
                self.emit("eq")
                self.emit("not")
            elif node.op == ">":
                self.emit("gt")
            elif node.op == ">=":
                self.emit("ge")
            return "bool"

        elif node.op in ["and", "or"]:
            if left_type != "bool":
                raise Exception(f"Type Error: Logical operator '{node.op}' requires bool operands")
            if node.op == "and":
                self.emit("and")
            elif node.op == "or":
                self.emit("or")
            return "bool"

        else:
            raise Exception(f"Semantic Error: Unknown binary operator '{node.op}'")

    def visit_unary_op_node(self, node):
        operand_type = node.operand.accept(self)

        if node.op == "not":
            if operand_type != "bool":
                raise Exception("Type Error: 'not' operator requires a boolean operand")
            self.emit("not")
            return "bool"

        elif node.op == "-":
            if operand_type not in {"int", "float"}:
                raise Exception("Type Error: Unary '-' operator requires int or float operand")
            # Simulate 0 - operand by:
            # 1. Evaluating operand (already done above)
            # 2. Pushing 0 after operand is on stack
            # 3. Calling `sub`, which pops b then a → computes a - b
            self.emit("push -1")
            self.emit("mul")
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


    def visit_if_node(self, node):
        cond_type = node.condition_expr.accept(self)
        if cond_type != "bool":
            raise Exception("Type Error: Condition of 'if' must be boolean")
        node.then_block.accept(self)
        if node.else_block:
            node.else_block.accept(self)

    def visit_function_decl_node(self, node):
        # Ensure function is declared at top level (global scope)
        if len(self.symbol_table.scopes) != 2: # 2 scopes: global and function
            raise Exception("Semantic Error: Functions must be declared in the global scope.")

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

        if not self.does_block_always_return(node.body):
            raise Exception(f"Semantic Error: Function '{node.name}' may not return a value on all paths.")

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
        # No specific type requirement for print
        node.expr.accept(self)
        self.emit("print")

    def visit_delay_node(self, node):
        delay_type = node.expr.accept(self)
        if delay_type != "int":
            raise Exception(f"Type Error: __delay expects 'int', got '{delay_type}'")
        self.emit("delay")
        
    def visit_clear_node(self, node):
        clear_type = node.expr.accept(self)
        if clear_type != "colour":
            raise Exception(f"Type Error: __clear expects 'colour', got '{clear_type}'")
        self.emit("clear")

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
        
        self.emit("write")
        
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
        
        self.emit("writebox")

    def visit_rtrn_node(self, node):
        if self.current_return_type is None:
            raise Exception("Semantic Error: 'return' statement outside of function.")

        expr_type = node.expr.accept(self)
        if expr_type != self.current_return_type:
            raise Exception(
                f"Type Error: Return type '{expr_type}' does not match expected function return type '{self.current_return_type}'"
            )
        
    def visit_program_node(self, node):
        

        func_decls = []
        main_stmts = []

        for stmt in node.stmts:
            if isinstance(stmt, ASTFunctionDeclNode):
                func_decls.append(stmt)
            else:
                main_stmts.append(stmt) 

        # Emit PArIR .main entry
        self.emit(".main")
        self.emit("push 4")
        self.emit("jmp")
        self.emit("halt")

        # Emit code for .main logic
        self.symbol_table.enter_scope()
        # Emit stack frame setup for main block
        num_main_vars = sum(isinstance(s, ASTVariableDeclNode) for s in main_stmts)
        self.emit(f"push {num_main_vars}")
        self.emit("oframe")

        for stmt in main_stmts:
            stmt.accept(self)

        self.emit("cframe")
        self.symbol_table.exit_scope()
        self.emit("halt")

        # Emit code for function declarations
        for func in func_decls:
            self.emit(f".{func.name}")
            func.accept(self)


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
    
    def emit(self, instr):
        self.instructions.append(instr)

    def error(self, message):
        raise Exception(f"Semantic Error: {message}")
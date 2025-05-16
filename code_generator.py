from astnodes import ASTIfNode, ASTRtrnNode, ASTWhileNode, ASTBlockNode, ASTVariableDeclNode, ASTFunctionDeclNode, ASTArrayDeclNode, ASTVariableNode, ASTBinaryOpNode, ASTUnaryOpNode, ASTIntegerNode, ASTForNode
from symbol_table import SymbolTable

class CodeGenerator:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_return_type = None
        self.instructions = []

    def visit_block_node(self, node):
        self.symbol_table.enter_scope()

        num_vars = sum(isinstance(stmt, ASTVariableDeclNode) for stmt in node.stmts)
        self.emit(f"push {num_vars}")
        self.emit("oframe")

        for stmt in node.stmts:
            stmt.accept(self)

        self.emit("cframe")
        self.symbol_table.exit_scope()

    def visit_variable_decl_node(self, node):
        var_type = node.vartype
        self.symbol_table.declare(node.identifier, var_type)

        expr_type = node.expr.accept(self)
        if expr_type != var_type:
            raise Exception(f"Type Error: Cannot assign {expr_type} to variable of type {var_type}")
        entry  = self.symbol_table.lookup_full(node.identifier)
        index = entry["index"]
        level = entry["level"]
        access_level = self.symbol_table.scope_levels[-1] - level
        self.emit(f"push {index}")
        self.emit(f"push {access_level}")
        self.emit("st")

    def visit_variable_node(self, node):
        entry = self.symbol_table.lookup_full(node.lexeme)
        var_type = entry["type"]
        index = entry["index"]
        declevel = entry["level"]
        access_level = self.symbol_table.scope_levels[-1] - declevel
        if node.index_expr is not None:
            idx_type = node.index_expr.accept(self)
            if idx_type != "int":
                raise Exception("Type Error: Array index must be an integer")
            if not getattr(self, "suppress_emit", False): 
                self.emit(f"push +[{index}:{access_level}]")           
            return var_type[:-2]          

        if not getattr(self, "suppress_emit", False):
            self.emit(f"push [{index}:{access_level}]")

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
        if node.value == "true":
            self.emit("push 1")
        elif node.value == "false":
            self.emit("push 0")
        else:
            raise Exception(f"Type Error: Unknown boolean value '{node.value}'")
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
        entry = self.symbol_table.lookup_full(node.id.lexeme)
        index = entry["index"]
        level = entry["level"]
        access_level = self.symbol_table.scope_levels[-1] - level
        self.emit(f"push {index}")
        self.emit(f"push {access_level}")
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

        self.emit(f"push {len(node.values)}")  # number of values

        entry = self.symbol_table.lookup_full(node.identifier)
        index = entry["index"]
        level = entry["level"]
        access_level = self.symbol_table.scope_levels[-1] - level
        self.emit(f"push {index}")
        self.emit(f"push {access_level}")

        self.emit("sta")  # store array to stack


    def visit_if_node(self, node):
        cond_type = node.condition_expr.accept(self)
        if cond_type != "bool":
            raise Exception("Type Error: Condition in 'if' must be boolean")

        

        
        if node.else_block:

            self.emit("push #PC+1")  # Placeholder for jump target
            self.emit("cjmp")
            cjmp_index = len(self.instructions) - 1

            node.else_block.accept(self)

            # Jump over else block
            self.emit("push #PC+1")  # Placeholder
            self.emit("jmp")
            jmp_index = len(self.instructions) - 1

            # Patch cjmp
            self.instructions[cjmp_index - 1] = f"push #PC+{len(self.instructions) - cjmp_index + 1}"
            
            node.then_block.accept(self)

            # Patch jump over else
            self.instructions[jmp_index - 1] = f"push #PC+{len(self.instructions) - jmp_index + 1}"
        else:
            self.emit("push #PC+4")  # Always +4
            self.emit("cjmp")

            cjmp_index = len(self.instructions) - 1

            self.emit("push #PC+1")  # Placeholder for jump target
            self.emit("jmp")

            jmp_index = len(self.instructions) - 1
            node.then_block.accept(self)
            self.instructions[jmp_index - 1] = f"push #PC+{len(self.instructions) - jmp_index + 1}"



    def visit_function_decl_node(self, node):
        if len(self.symbol_table.scopes) != 2:
            raise Exception("Semantic Error: Functions must be declared in the global scope.")
        
        self.symbol_table.declare(node.name, {
                'type': node.return_type,
                'kind': 'function',
                'params': node.params,
                'return_type': node.return_type
            })

        self.emit("push #PC+1")
        self.emit("jmp")
        jmp_index = len(self.instructions) - 1
        self.emit(f".{node.name}")

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
        self.emit(f"push {num_locals}")
        self.emit("alloc")

        # ✅ Avoid visit_block_node here to skip oframe/cframe
        for stmt in node.body.stmts:
            stmt.accept(self)

        self.symbol_table.exit_scope()

        self.instructions[jmp_index - 1] = f"push #PC+{len(self.instructions) - jmp_index + 1}"

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
                index = entry["index"]
                level = entry["level"]
                size = entry["size"]
                access_level = self.symbol_table.scope_levels[-1] - level

                # Push size of array
                self.emit(f"push {size}")
                # Push offset and frame level of array
                self.emit(f"pusha [{index}:{access_level}]")
                self.emit(f"push {size}")
                is_array = True
            else:
                is_array = False
                arg_type = arg_node.accept(self)
                if arg_type != param_type:
                    self.error(f"In call to '{node.func_name}', expected type '{param_type}' for argument '{param_name}', got '{arg_type}'.")
                    # 2. Push number of arguments

        if not is_array:
            self.emit(f"push {len(node.args)}")            
        

        # 3. Push function label
        self.emit(f"push .{node.func_name}")

        # 4. Emit call
        self.emit("call")

        return func_entry['return_type']
    
    def visit_while_node(self, node):
        loop_start_index = len(self.instructions)  # mark the start of the condition check

        # 1. Evaluate the condition
        cond_type = node.condition.accept(self)
        if cond_type != "bool":
            raise Exception("Type Error: Condition in 'while' must be boolean")

        # 2. Emit placeholder for conditional jump if false (exit loop)
        self.emit("push #PC+4") 
        self.emit("cjmp")
        cjmp_index = len(self.instructions) - 1
        self.emit("push #PC+1")  # Placeholder for jump target
        self.emit("jmp")
        jmp_index = len(self.instructions) - 1

        # 3. Emit loop body
        node.body.accept(self)

        # 4. Jump back to start of condition
        self.emit(f"push #PC-{len(self.instructions) - loop_start_index}")
        self.emit("jmp")
        self.instructions[jmp_index - 1] = f"push #PC+{len(self.instructions) - jmp_index + 1}"



    def visit_for_node(self, node):
        self.symbol_table.enter_scope()
        
        
       # Handle init (could be one or more variable declarations)
        if node.init:
            if isinstance(node.init, list):
                count = sum(isinstance(decl, ASTVariableDeclNode) for decl in node.init)
            else:
                count = 1  # assume one declaration
            self.emit(f"push {count}")
            self.emit("oframe")
            node.init.accept(self)
        else:
            self.emit("push 0")
            self.emit("oframe")
        

            

        # 2. Remember start of condition
        cond_index = len(self.instructions)

        # 3. Emit condition (e.g., i < 64)
        if node.condition:
            cond_type = node.condition.accept(self)
            if cond_type != "bool":
                raise Exception(f"Type Error: for-loop condition must be 'bool', got '{cond_type}'")
        else:
            raise Exception("Syntax Error: for-loop requires a condition")

        # 4. Emit conditional jump to stay in loop if true
        self.emit("push #PC+4")  # jump forward to stay in loop
        self.emit("cjmp")

        # 5. Emit unconditional jump to exit loop if condition is false
        self.emit("push #PC+1")  # placeholder to jump after body
        self.emit("jmp")
        jmp_to_end_index = len(self.instructions) - 1

        # 6. Emit body (open block scope)
        node.body.accept(self)

        # 7. Emit update (e.g., i = i + 1)
        if node.update:
            node.update.accept(self)

        # 8. Jump back to condition
        self.emit(f"push #PC-{len(self.instructions) - cond_index}")
        self.emit("jmp")

        # 9. Patch jump that exits the loop
        self.instructions[jmp_to_end_index - 1] = f"push #PC+{len(self.instructions) - jmp_to_end_index + 1}"
        self.emit("cframe")
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
        self.emit("ret")
        
    def visit_program_node(self, node):
        # Emit PArIR .main entry
        self.emit(".main")
        self.emit("push 4")
        self.emit("jmp")
        self.emit("halt")


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
        self.emit(f"push {num_main_vars}")
        self.emit("oframe")

        for stmt in node.stmts:
            stmt.accept(self)

        self.emit("cframe")
        self.symbol_table.exit_scope()
        self.emit("halt")

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
    
    def emit(self, instr):
        self.instructions.append(instr)

    def error(self, message):
        raise Exception(f"Semantic Error: {message}")
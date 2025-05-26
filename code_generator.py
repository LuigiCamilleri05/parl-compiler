# File which was initially copied from semantic_analyzer.py and modified to generate code
# To understand the semantics, check the comments in semantic_analyzer.py

from astnodes import ASTIfNode, ASTRtrnNode, ASTWhileNode, ASTBlockNode, ASTVariableDeclNode, ASTFunctionDeclNode, ASTArrayDeclNode, ASTVariableNode, ASTBinaryOpNode, ASTUnaryOpNode, ASTIntegerNode, ASTForNode
from symbol_table import SymbolTable

# Class used to generate code
class CodeGenerator:

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_return_type = None
        self.instructions = [] # List to store generated instructions

    def does_block_always_return(self, block_node):

        for stmt in block_node.stmts:

            if isinstance(stmt, ASTRtrnNode):
                return True
            
            elif isinstance(stmt, ASTIfNode):
                then_returns = self.does_block_always_return(stmt.then_block)
                else_returns = self.does_block_always_return(stmt.else_block) if stmt.else_block else False
                if then_returns and else_returns:
                    return True
                
            elif isinstance(stmt, ASTWhileNode):
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
    
    # Function used to emit instructions and store them in the instructions list
    def emit(self, instr):
        self.instructions.append(instr)

# Visitor methods below implement type-checking 
# rules and code generation for each AST node type

    def visit_boolean_node(self, node):
            # Emits code for boolean literals based on
            # the value of the node, (true = 1, false = 0)
            if node.value == "true":
                self.emit("push 1")
            elif node.value == "false":
                self.emit("push 0")
            else:
                raise Exception(f"Type Error: Unknown boolean value '{node.value}'")
            return "bool"

    def visit_integer_node(self, node):
        # Emits the integer value of the node
        self.emit(f"push {node.value}")
        return "int"

    def visit_float_node(self, node):
        self.emit(f"push {node.value}")
        return "float"

    def visit_colour_node(self, node):
        # Converts the colour string to an integer
        # and emits the value 
        colour_int = int(node.value.lstrip("#"), 16)
        self.emit(f"push {colour_int}")
        return "colour"
    
    def visit_pad_width_node(self, node):
        self.emit("width")
        return "int"

    def visit_pad_height_node(self, node):
        self.emit("height")
        return "int"

    def visit_pad_read_node(self, node):

        # Switched the order of x and y 
        # to match the stack frame appoach
        y_type = node.expr2.accept(self)
        x_type = node.expr1.accept(self)
    
        if x_type != "int":
            raise Exception(f"Type Error: __read expects int for x, got {x_type}")
        if y_type != "int":
            raise Exception(f"Type Error: __read expects int for y, got {y_type}")
        self.emit("read")

        return "colour"

    def visit_pad_rand_int_node(self, node):
        bound_type = node.expr.accept(self)
        if bound_type != "int":
            raise Exception(f"Type Error: __random_int expects an int, got {bound_type}")
        self.emit("irnd")
        return "int"
    
    def visit_binary_op_node(self, node):

        # Switch the order due to stack frame approach
        right_type = node.right.accept(self)
        left_type = node.left.accept(self)
        if left_type != right_type:
            raise Exception(f"Type Error: Mismatched operands: {left_type} and {right_type}")
        
        # Emits code based on the operator
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

    def visit_function_call_node(self, node):
        
        entry = self.symbol_table.lookup(node.func_name)
        func_entry = entry["type"]
        if func_entry is None:
            raise Exception(f"Function '{node.func_name}' not declared before use.")

        if func_entry['kind'] != 'function':
            raise Exception(f"Identifier '{node.func_name}' is not a function.")

        expected_params = func_entry['params']
        if len(expected_params) != len(node.args):
            raise Exception(f"Function '{node.func_name}' expects {len(expected_params)} argument(s), got {len(node.args)}.")

        for (arg_node, (param_name, param_type, _)) in zip(node.args, expected_params):
            if param_type.endswith("[]"):
                
                # Looks up the the function's array entry and gets
                # the size of the array, index of last element and level
                entry = self.symbol_table.lookup(arg_node.lexeme)
                index = entry["index"]
                level = entry["level"]
                size = entry["size"]

                # Calculate the access level 
                # (The level currently - the level of the array entry)
                access_level = self.symbol_table.scope_levels[-1] - level

                # Pushes size of array
                self.emit(f"push {size}")
                # Pushes offset and frame level of array
                self.emit(f"pusha [{index}:{access_level}]")
                # Pushes the length of the number 
                # of arguments == size of the array
                self.emit(f"push {size}")

                # Flag to indicate that the argument is an array
                is_array = True
            else:
                # Argument is not an array
                is_array = False
                arg_type = arg_node.accept(self)
                if arg_type != param_type:
                    raise Exception(f"In call to '{node.func_name}', expected type '{param_type}' for argument '{param_name}', got '{arg_type}'.")

        # If the argument is not an array, push the number of arguments
        if not is_array:
            self.emit(f"push {len(node.args)}")            
        
        # Pushes the function label
        self.emit(f"push .{node.func_name}")

        # Emits call as the structure of PArIR
        self.emit("call")

        return func_entry['return_type']
    
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
            # Simulates the - operand by:
            # pushing -1 and multiplying
            self.emit("push -1")
            self.emit("mul")
            return operand_type

        else:
            raise Exception(f"Semantic Error: Unknown unary operator '{node.op}'")

    def visit_assignment_node(self, node):
        self.suppress_emit = True # Used to not emit the variable's value when assigning
        var_type = node.id.accept(self)
        self.suppress_emit = False

        expr_type = node.expr.accept(self)
        if var_type != expr_type:
            raise Exception(f"Type Error: Cannot assign {expr_type} to variable of type {var_type}")
        
        # Get index and level from lookup to push
        # and store the variable's index and access level
        entry = self.symbol_table.lookup(node.id.lexeme)
        index = entry["index"]
        level = entry["level"]
        access_level = self.symbol_table.scope_levels[-1] - level
        self.emit(f"push {index}")
        self.emit(f"push {access_level}")
        self.emit("st")
        
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
    
    def visit_variable_decl_node(self, node):
        var_type = node.vartype
        self.symbol_table.declare(node.identifier, var_type)

        expr_type = node.expr.accept(self)
        if expr_type != var_type:
            raise Exception(f"Type Error: Cannot assign {expr_type} to variable of type {var_type}")
        
        # Get index and level from lookup to push 
        # and store after declaring the variable
        entry  = self.symbol_table.lookup(node.identifier)
        index = entry["index"]
        level = entry["level"]
        access_level = self.symbol_table.scope_levels[-1] - level
        self.emit(f"push {index}")
        self.emit(f"push {access_level}")
        self.emit("st")

    def visit_variable_node(self, node):

        # Finds the entry in the symbol table
        # and gets the type, index and level
        entry = self.symbol_table.lookup(node.lexeme)
        var_type = entry["type"]
        index = entry["index"]
        level = entry["level"]
        access_level = self.symbol_table.scope_levels[-1] - level

        # Checks if the variable is an array
        if node.index_expr is not None:
            # Gets the index type from the index expression
            idx_type = node.index_expr.accept(self)
            # Index expression must be an integer
            if idx_type != "int":
                raise Exception("Type Error: Array index must be an integer")
            # Pushes the index expression if suppresss_emit is not set
            if not getattr(self, "suppress_emit", False): 
                self.emit(f"push +[{index}:{access_level}]")           
            return var_type[:-2]          

        # If the variable is not an array, push the index and access level
        # as long as suppress_emit is not set
        if not getattr(self, "suppress_emit", False):
            self.emit(f"push [{index}:{access_level}]")

        return var_type
    
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

        if node.size_expr:
            size_type = node.size_expr.accept(self)
            if size_type != "int":
                raise Exception("Type Error: Array size must be of type 'int'")

        # Reversed to match the stack frame approach
        for val in reversed(node.values):
            val_type = val.accept(self)
            if val_type != base_type:
                raise Exception(
                    f"Type Error: Array '{node.identifier}' expects elements of type '{base_type}', got '{val_type}'"
                )

        # Emit code to push the number values onto the stack
        self.emit(f"push {len(node.values)}")

        # Looks up the array entry in the symbol table
        # and gets the index and level and stores the array
        entry = self.symbol_table.lookup(node.identifier)
        index = entry["index"]
        level = entry["level"]
        access_level = self.symbol_table.scope_levels[-1] - level
        self.emit(f"push {index}")
        self.emit(f"push {access_level}")
        self.emit("sta")

    def visit_print_node(self, node):
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

    def visit_if_node(self, node):
        cond_type = node.condition_expr.accept(self)
        if cond_type != "bool":
            raise Exception("Type Error: Condition in 'if' must be boolean")

        if node.else_block:

            self.emit("push #PC+1")  # Placeholder for jump target
            # Puses conditional jump, activates if condition is true
            self.emit("cjmp") 
            # Gets the index of push #PC+1 before cjmp
            cjmp_index = len(self.instructions) - 1

            # Starts with the else block
            # due to the stack frame approach
            node.else_block.accept(self)

            # Jump over else block
            self.emit("push #PC+1")  # Placeholder
            self.emit("jmp")
            # Gets the index of push #PC+1 before jmp
            jmp_index = len(self.instructions) - 1

            # Gets the number of instructions that
            # need to be skipped after conditional jump
            self.instructions[cjmp_index - 1] = f"push #PC+{len(self.instructions) - cjmp_index + 1}"
            
            # Emits the then block (first block in PARl)
            node.then_block.accept(self)

            # Gets the number of instructions that
            # need to be skipped after unconditional jump
            self.instructions[jmp_index - 1] = f"push #PC+{len(self.instructions) - jmp_index + 1}"
        else:
            # Always +4 to jmp over the jmp and cjmps
            self.emit("push #PC+4")

            # Same logic as above, but without the else block  
            self.emit("cjmp")
            cjmp_index = len(self.instructions) - 1

            self.emit("push #PC+1")  # Placeholder for jump target
            self.emit("jmp")
            jmp_index = len(self.instructions) - 1
            node.then_block.accept(self)
            self.instructions[jmp_index - 1] = f"push #PC+{len(self.instructions) - jmp_index + 1}"

    # Used similar logic to if node
    # but with a different order of the blocks
    def visit_for_node(self, node):

        # Used to match oframe/cframe in PArIR
        self.symbol_table.enter_scope()
    
        if node.init:
            # Checks for multiple declarations
            if isinstance(node.init, list):
                count = sum(isinstance(decl, ASTVariableDeclNode) for decl in node.init)
            else:
                count = 1  # assume one declaration
            # Emits the number of variables and oframe
            self.emit(f"push {count}")
            self.emit("oframe")
            node.init.accept(self)
        else:
            # No declarations and opens a frame
            self.emit("push 0")
            self.emit("oframe")
    
        # Keeps track of the line number of the start of the condition
        cond_index = len(self.instructions)

        if node.condition:
            cond_type = node.condition.accept(self)
            if cond_type != "bool":
                raise Exception(f"Type Error: for-loop condition must be 'bool', got '{cond_type}'")
        else:
            raise Exception("Syntax Error: for-loop requires a condition")

        # Emits conditional jump to stay in loop if true
        self.emit("push #PC+4")  # skips over the jmp and cjmp
        self.emit("cjmp")

        # Emits unconditional jump to exit loop if condition is false
        self.emit("push #PC+1")  # placeholder
        self.emit("jmp")
        jmp_to_end_index = len(self.instructions) - 1

        node.body.accept(self)

        if node.update:
            node.update.accept(self)

        # Jumps back to condition
        self.emit(f"push #PC-{len(self.instructions) - cond_index}")
        self.emit("jmp")

        # Gets the number of instructions that goes to the end of the block
        self.instructions[jmp_to_end_index - 1] = f"push #PC+{len(self.instructions) - jmp_to_end_index + 1}"
        self.emit("cframe")
        self.symbol_table.exit_scope()

    def visit_while_node(self, node):
        # Marks the start of the loop
        loop_start_index = len(self.instructions)  

        cond_type = node.condition.accept(self)
        if cond_type != "bool":
            raise Exception("Type Error: Condition in 'while' must be boolean")

        # Skips over the jmp and cjmp if cjmp is true
        self.emit("push #PC+4") 
        self.emit("cjmp")

        self.emit("push #PC+1")  # Placeholder for jump target
        self.emit("jmp")
        jmp_index = len(self.instructions) - 1

        # Emits the body of the loop
        node.body.accept(self)

        # Find instruction number to jump back to the condition
        self.emit(f"push #PC-{len(self.instructions) - loop_start_index}")
        self.emit("jmp")
        self.instructions[jmp_index - 1] = f"push #PC+{len(self.instructions) - jmp_index + 1}"
        
    def visit_function_decl_node(self, node):

        # Check if the function is declared in the global scope
        if len(self.symbol_table.scopes) != 2:
            raise Exception("Semantic Error: Functions must be declared in the global scope.")
        
        self.symbol_table.declare(node.name, {
                'type': node.return_type,
                'kind': 'function',
                'params': node.params,
                'return_type': node.return_type
            })


        self.emit("push #PC+1") # Placeholder for jump target
        self.emit("jmp")
        jmp_index = len(self.instructions) - 1
        # Emits the function label
        self.emit(f".{node.name}")

        # Enters a new scope for the function
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

        # Used to count the number of local variables in the function
        num_locals = self.count_local_vars(node.body)
        # Gets the number of local variables in an array
        for name, typ, size_expr in node.params:
            if isinstance(typ, str) and typ.endswith("[]"):
                if isinstance(size_expr, ASTIntegerNode):
                    num_locals += int(size_expr.value)
            else:
                # If the parameter is not an array, just count it
                num_locals += 1
        self.emit(f"push {num_locals}")
        # alloc is used to allocate space for local variables
        self.emit("alloc")

        # Avoid visit_block_node here to skip oframe/cframe
        # Uses alloc instead due to how it is seen in PArIR
        for stmt in node.body.stmts:
            stmt.accept(self)

        # Closes the function scope
        self.symbol_table.exit_scope()

        # Gets the instruction number to jump back to the start of function
        self.instructions[jmp_index - 1] = f"push #PC+{len(self.instructions) - jmp_index + 1}"

        if not self.does_block_always_return(node.body):
            raise Exception(f"Semantic Error: Function '{node.name}' may not return a value on all paths.")
    
    def visit_block_node(self, node):
        self.symbol_table.enter_scope()

        # Gets the number of local variables in the block
        # and emits the number of variables
        num_vars = sum(isinstance(stmt, ASTVariableDeclNode) for stmt in node.stmts)
        self.emit(f"push {num_vars}")
        # Opens and closes frame for the block
        self.emit("oframe")

        for stmt in node.stmts:
            stmt.accept(self)

        self.emit("cframe")
        self.symbol_table.exit_scope()

    def visit_program_node(self, node):
        # Emit PArIR .main entry
        self.emit(".main")
        self.emit("push 4")
        self.emit("jmp")
        # Jumps over halt
        self.emit("halt")

        # Emits code for .main logic
        self.symbol_table.enter_scope()
        # Emits stack frame setup for main block
        num_main_vars = 0
        # Gets the number of global variables in the main block
        for stmt in node.stmts:
            if isinstance(stmt, ASTVariableDeclNode) or isinstance(stmt, ASTFunctionDeclNode):
                num_main_vars += 1
            elif isinstance(stmt, ASTArrayDeclNode):
                # Accounts for array reference slot
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
        # Finishes the program
        self.emit("halt")

    
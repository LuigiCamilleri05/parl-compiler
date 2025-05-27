# This module defines all AST node classes used by the parser and other components.
# These nodes supports operations such as structure visualization, semantic checks,
# EBNF validation, and code generation via the visitor pattern.

# Each AST node includs an `accept` method, which delegates to the visitor’s corresponding `visit_` method.
# This enables flexibility allowing different visitor classes in separate files
# Each node's constructor (__init__) may store relevant information specific to that node's role in the AST.

class ASTBooleanNode():
    def __init__(self, v):
        self.name = "ASTBooleanNode"
        self.value = v

    def accept(self, visitor):
        return visitor.visit_boolean_node(self)


class ASTIntegerNode():
    def __init__(self, v):
        self.name = "ASTIntegerNode"
        self.value = v

    def accept(self, visitor):
        return visitor.visit_integer_node(self)  

class ASTFloatNode():
    def __init__(self, v):
        self.name = "ASTFloatNode"
        self.value = v

    def accept(self, visitor):
        return visitor.visit_float_node(self)

class ASTColourNode():
    def __init__(self, v):
        self.name = "ASTColourNode"
        self.value = v

    def accept(self, visitor):
        return visitor.visit_colour_node(self)

class ASTPadWidthNode():
    def __init__(self):
        self.name = "ASTPadWidthNode"

    def accept(self, visitor):
        return visitor.visit_pad_width_node(self)

class ASTPadHeightNode():
    def __init__(self):
        self.name = "ASTPadHeightNode"

    def accept(self, visitor):
        return visitor.visit_pad_height_node(self)

class ASTPadReadNode():
    def __init__(self, expr1, expr2):
        self.name = "ASTPadReadNode"
        self.expr1 = expr1
        self.expr2 = expr2

    def accept(self, visitor):
        return visitor.visit_pad_read_node(self)

class ASTPadRandINode():
    def __init__(self, expr):
        self.name = "ASTPadRandINode"
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_pad_rand_int_node(self)

class ASTBinaryOpNode():
    def __init__(self, op, left, right):
        self.name = "ASTBinaryOpNode"
        self.op = op              
        self.left = left          
        self.right = right        

    def accept(self, visitor):
        return visitor.visit_binary_op_node(self)
    

class ASTFunctionCallNode():
    def __init__(self, func_name, args):
        self.name = "ASTFunctionCallNode"
        self.func_name = func_name
        self.args = args  

    def accept(self, visitor):
        return visitor.visit_function_call_node(self)


class ASTUnaryOpNode():
    def __init__(self, op, operand):
        self.name = "ASTUnaryOpNode"
        self.op = op              
        self.operand = operand    

    def accept(self, visitor):
        return visitor.visit_unary_op_node(self)
    
class ASTAssignmentNode():
    def __init__(self, ast_var_node, ast_expression_node):
        self.name = "ASTAssignmentNode"        
        self.id   = ast_var_node
        self.expr = ast_expression_node

    def accept(self, visitor):
        visitor.visit_assignment_node(self)

class ASTCastNode():
    def __init__(self, expr, target_type):
        self.name = "ASTCastNode"
        self.expr = expr             
        self.target_type = target_type  

    def accept(self, visitor):
        return visitor.visit_cast_node(self)

class ASTVariableDeclNode():
    def __init__(self, identifier, vartype, expr):
        self.name = "ASTVariableDeclNode"
        self.identifier = identifier  
        self.vartype = vartype        
        self.expr = expr              

    def accept(self, visitor):
        visitor.visit_variable_decl_node(self)

class ASTVariableNode():
    def __init__(self, lexeme, index_expr=None):
        self.name = "ASTVariableNode"
        self.lexeme = lexeme
        self.index_expr = index_expr

    def accept(self, visitor):
        return visitor.visit_variable_node(self)

class ASTArrayDeclNode():
    def __init__(self, identifier, vartype, size_expr, values):
        self.name = "ASTArrayDeclNode"
        self.identifier = identifier      
        self.vartype = vartype            
        self.size_expr = size_expr       
        self.values = values              

    def accept(self, visitor):
        visitor.visit_array_decl_node(self)

class ASTPrintNode():
    def __init__(self, expr):
        self.name = "ASTPrintNode"
        self.expr = expr  

    def accept(self, visitor):
        visitor.visit_print_node(self)

class ASTDelayNode():
    def __init__(self, expr):
        self.name = "ASTDelayNode"
        self.expr = expr  

    def accept(self, visitor):
        visitor.visit_delay_node(self)

class ASTClearNode():
    def __init__(self, expr):
        self.name = "ASTClearNode"
        self.expr = expr  

    def accept(self, visitor):
        visitor.visit_clear_node(self)

class ASTWriteNode():
    def __init__(self, x_expr, y_expr, val_expr):
        self.name = "ASTWriteNode"
        self.x_expr = x_expr
        self.y_expr = y_expr
        self.val_expr = val_expr

    def accept(self, visitor):
        visitor.visit_write_node(self)

class ASTWriteBoxNode():
    def __init__(self, x_expr, y_expr, w_expr, h_expr, val_expr):
        self.name = "ASTWriteBoxNode"
        self.x_expr = x_expr
        self.y_expr = y_expr
        self.w_expr = w_expr
        self.h_expr = h_expr
        self.val_expr = val_expr

    def accept(self, visitor):
        visitor.visit_write_box_node(self)

class ASTRtrnNode():
    def __init__(self, expr):
        self.name = "ASTRtrnNode"
        self.expr = expr  

    def accept(self, visitor):
        visitor.visit_rtrn_node(self)

class ASTIfNode():
    def __init__(self, condition_expr, then_block, else_block=None):
        self.name = "ASTIfNode"
        self.condition_expr = condition_expr        
        self.then_block = then_block                
        self.else_block = else_block                

    def accept(self, visitor):
        visitor.visit_if_node(self)

class ASTForNode():
    def __init__(self, init, condition, update, body):
        self.name = "ASTForNode"
        self.init = init        
        self.condition = condition  
        self.update = update    
        self.body = body        

    def accept(self, visitor):
        return visitor.visit_for_node(self)
    
class ASTWhileNode():
    def __init__(self, condition, body):
        self.name = "ASTWhileNode"
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while_node(self)

class ASTFunctionDeclNode():
    def __init__(self, name, params, return_type, return_size, body):
        self.name = name
        self.params = params  
        self.return_type = return_type
        self.return_size = return_size  
        self.body = body

    def accept(self, visitor):
        return visitor.visit_function_decl_node(self)

class ASTBlockNode():
    def __init__(self):
        self.name = "ASTBlockNode"
        self.stmts = []

    def add_statement(self, node):
        self.stmts.append(node)

    def accept(self, visitor):
        visitor.visit_block_node(self)        

class ASTProgramNode():
    def __init__(self):
        self.name = "ASTProgramNode"
        self.stmts = []

    def add_statement(self, stmt):
        self.stmts.append(stmt)

    def accept(self, visitor):
        visitor.visit_program_node(self)

# Visitor class that traverses the AST and prints the structure
# Uses accepts, visit methods and tabs to show the structure of the tree
class PrintNodesVisitor():
    def __init__(self):
        self.name = "Print Tree Visitor"
        self.node_count = 0
        self.tab_count = 0

    def inc_tab_count(self):
        self.tab_count += 1

    def dec_tab_count(self):
        self.tab_count -= 1

    def visit_boolean_node(self, bool_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Boolean value::", bool_node.value)    
        
    def visit_integer_node(self, int_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Integer value::", int_node.value)

    def visit_float_node(self, float_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Float value::", float_node.value)   

    def visit_colour_node(self, colour_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Colour value::", colour_node.value)

    def visit_pad_width_node(self, pad_width_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Pad Width")

    def visit_pad_height_node(self, pad_height_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Pad Height")

    def visit_pad_read_node(self, node):
        self.node_count += 1
        print('\t' * self.tab_count, "PadRead =>")
        self.tab_count += 1
        node.expr1.accept(self)
        node.expr2.accept(self)
        self.tab_count -= 1

    def visit_pad_rand_int_node(self, node):
        self.node_count += 1
        print('\t' * self.tab_count, "PadRandInt =>")
        self.tab_count += 1
        node.expr.accept(self)
        self.tab_count -= 1

    def visit_binary_op_node(self, node):
        print('\t' * self.tab_count, f"Binary Op: {node.op}")
        self.tab_count += 1
        node.left.accept(self)
        node.right.accept(self)
        self.tab_count -= 1

    def visit_function_call_node(self, node):
        print('\t' * self.tab_count, f"Function Call: {node.func_name}()")
        self.tab_count += 1
        for arg in node.args:
            arg.accept(self)
        self.tab_count -= 1

    def visit_unary_op_node(self, node):
        print('\t' * self.tab_count, f"Unary Op: {node.op}")
        self.tab_count += 1
        node.operand.accept(self)
        self.tab_count -= 1

    def visit_assignment_node(self, ass_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Assignment node => ")
        self.inc_tab_count()        
        ass_node.id.accept(self)
        ass_node.expr.accept(self)
        self.dec_tab_count()

    def visit_cast_node(self, node):
            print('\t' * self.tab_count, f"Cast to: {node.target_type}")
            self.tab_count += 1
            node.expr.accept(self)
    
    def visit_variable_decl_node(self, var_decl_node):
        self.node_count += 1
        print('\t' * self.tab_count, f"Variable Declaration => {var_decl_node.identifier} : {var_decl_node.vartype}")
        self.tab_count += 1
        var_decl_node.expr.accept(self)
        self.tab_count -= 1

        self.tab_count -= 1
    

    def visit_variable_node(self, var_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Variable => ", var_node.lexeme)
        if var_node.index_expr:
            self.tab_count += 1
            print('\t' * self.tab_count, "Index Expression =>")
            var_node.index_expr.accept(self)
            self.tab_count -= 1

    def visit_array_decl_node(self, node):
        print('\t' * self.tab_count, f"Array Declaration => {node.identifier} : {node.vartype}")
        self.inc_tab_count()

        if node.size_expr:
            print('\t' * self.tab_count, "Declared Size:")
            self.inc_tab_count()
            node.size_expr.accept(self)
            self.dec_tab_count()

        print('\t' * self.tab_count, "Initial Values:")
        self.inc_tab_count()
        for val in node.values:
            val.accept(self)
        self.dec_tab_count()

        self.dec_tab_count()

    def visit_print_node(self, node):
        print('\t' * self.tab_count, "Print Statement =>")
        self.inc_tab_count()
        node.expr.accept(self)
        self.dec_tab_count()

    def visit_delay_node(self, node):
        print('\t' * self.tab_count, "Delay Statement =>")
        self.inc_tab_count()
        node.expr.accept(self)
        self.dec_tab_count()

    def visit_clear_node(self, node):
        print('\t' * self.tab_count, "Clear Statement =>")
        self.inc_tab_count()
        node.expr.accept(self)
        self.dec_tab_count()

    def visit_write_node(self, node):
        print('\t' * self.tab_count, "Write Statement =>")
        self.inc_tab_count()
        node.x_expr.accept(self)
        node.y_expr.accept(self)
        node.val_expr.accept(self)
        self.dec_tab_count()

    def visit_write_box_node(self, node):
        print('\t' * self.tab_count, "Write Box Statement =>")
        self.inc_tab_count()
        node.x_expr.accept(self)
        node.y_expr.accept(self)
        node.w_expr.accept(self)
        node.h_expr.accept(self)
        node.val_expr.accept(self)
        self.dec_tab_count()

    def visit_rtrn_node(self, node):
        print('\t' * self.tab_count, "Return Statement =>")
        self.inc_tab_count()
        node.expr.accept(self)
        self.dec_tab_count()
    
    def visit_if_node(self, node):
        print('\t' * self.tab_count, "If Statement =>")
        self.inc_tab_count()

        print('\t' * self.tab_count, "Condition:")
        self.inc_tab_count()
        node.condition_expr.accept(self)
        self.dec_tab_count()

        print('\t' * self.tab_count, "Then Block:")
        node.then_block.accept(self)

        if node.else_block:
            print('\t' * self.tab_count, "Else Block:")
            node.else_block.accept(self)

        self.dec_tab_count()

    def visit_for_node(self, node):
        print("\t" * self.tab_count + "FOR Statement =>")
        self.inc_tab_count()
        
        if node.init:
            print("\t" * self.tab_count + "Initializer:")
            self.inc_tab_count()
            node.init.accept(self)
            self.dec_tab_count()

        print("\t" * self.tab_count + "Condition:")
        self.inc_tab_count()
        node.condition.accept(self)
        self.dec_tab_count()

        if node.update:
            print("\t" * self.tab_count + "Update:")
            self.inc_tab_count()
            node.update.accept(self)
            self.dec_tab_count()

        print("\t" * self.tab_count + "Body:")
        self.inc_tab_count()
        node.body.accept(self)
        self.dec_tab_count()

        self.dec_tab_count()

    def visit_while_node(self, node):
        print("\t" * self.tab_count + "WHILE Statement =>")
        self.inc_tab_count()

        print("\t" * self.tab_count + "Condition:")
        self.inc_tab_count()
        node.condition.accept(self)
        self.dec_tab_count()

        print("\t" * self.tab_count + "Body:")
        self.inc_tab_count()
        node.body.accept(self)
        self.dec_tab_count()

        self.dec_tab_count()

    def visit_function_decl_node(self, node):
        print('\t' * self.tab_count + "Function Declaration =>")
        self.inc_tab_count()

        print('\t' * self.tab_count + f"Name: {node.name}")

        print('\t' * self.tab_count + "Parameters:")
        self.inc_tab_count()
        for name, typ, size in node.params:
            if size:
                print('\t' * self.tab_count + f"{name} : {typ} [", end="")
                self.inc_tab_count()
                size.accept(self)
                self.dec_tab_count()
                print('\t' * self.tab_count + "]")
            else:
                print('\t' * self.tab_count + f"{name} : {typ}")
        self.dec_tab_count()

        print('\t' * self.tab_count + f"Return Type: {node.return_type}")
        if node.return_size:
            print('\t' * self.tab_count + "Return Size: [")
            self.inc_tab_count()
            node.return_size.accept(self)
            self.dec_tab_count()
            print('\t' * self.tab_count + "]")

        print('\t' * self.tab_count + "Body:")
        self.inc_tab_count()
        node.body.accept(self)
        self.dec_tab_count()

        self.dec_tab_count()

    def visit_block_node(self, block_node):
        self.node_count += 1
        print('\t' * self.tab_count, "New Block => ")
        self.inc_tab_count()
        
        for st in block_node.stmts:
            st.accept(self)
        
        self.dec_tab_count()

    def visit_program_node(self, node):
        for stmt in node.stmts:
            stmt.accept(self)

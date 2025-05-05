#First some AST Node classes we'll use to build the AST with
class ASTNode:
    def __init__(self):
        self.name = "ASTNode"    

class ASTStatementNode(ASTNode):
    def __init__(self):
        self.name = "ASTStatementNode"

class ASTExpressionNode(ASTNode):
    def __init__(self):
        self.name = "ASTExpressionNode"

class ASTVariableNode(ASTExpressionNode):
    def __init__(self, lexeme):
        self.name = "ASTVariableNode"
        self.lexeme = lexeme

    def accept(self, visitor):
        visitor.visit_variable_node(self)

class ASTIntegerNode(ASTExpressionNode):
    def __init__(self, v):
        self.name = "ASTIntegerNode"
        self.value = v

    def accept(self, visitor):
        visitor.visit_integer_node(self)  

class ASTFloatNode(ASTExpressionNode):
    def __init__(self, v):
        self.name = "ASTFloatNode"
        self.value = v

    def accept(self, visitor):
        visitor.visit_float_node(self)

class ASTBooleanNode(ASTExpressionNode):
    def __init__(self, v):
        self.name = "ASTBooleanNode"
        self.value = v

    def accept(self, visitor):
        visitor.visit_boolean_node(self)

class ASTColourNode(ASTExpressionNode):
    def __init__(self, v):
        self.name = "ASTColourNode"
        self.value = v

    def accept(self, visitor):
        visitor.visit_colour_node(self)      
class ASTPadWidthNode(ASTExpressionNode):
    def __init__(self):
        self.name = "ASTPadWidthNode"

    def accept(self, visitor):
        visitor.visit_pad_width_node(self)

class ASTPadHeightNode(ASTExpressionNode):
    def __init__(self):
        self.name = "ASTPadHeightNode"

    def accept(self, visitor):
        visitor.visit_pad_height_node(self)

class ASTPadReadNode(ASTExpressionNode):
    def __init__(self, expr1, expr2):
        self.name = "ASTPadReadNode"
        self.expr1 = expr1
        self.expr2 = expr2

    def accept(self, visitor):
        visitor.visit_pad_read_node(self)


class ASTPadRandINode(ASTExpressionNode):
    def __init__(self, expr):
        self.name = "ASTPadRandINode"
        self.expr = expr

    def accept(self, visitor):
        visitor.visit_pad_rand_int_node(self)

class ASTAssignmentNode(ASTStatementNode):
    def __init__(self, ast_var_node, ast_expression_node):
        self.name = "ASTStatementNode"        
        self.id   = ast_var_node
        self.expr = ast_expression_node

    def accept(self, visitor):
        visitor.visit_assignment_node(self)                

class ASTBlockNode(ASTNode):
    def __init__(self):
        self.name = "ASTBlockNode"
        self.stmts = []

    def add_statement(self, node):
        self.stmts.append(node)

    def accept(self, visitor):
        visitor.visit_block_node(self)        

class ASTProgramNode(ASTNode):
    def __init__(self):
        self.name = "ASTProgramNode"
        self.stmts = []

    def add_statement(self, stmt):
        self.stmts.append(stmt)

    def accept(self, visitor):
        visitor.visit_program_node(self)
        for stmt in self.stmts:
            stmt.accept(visitor)

class ASTVisitor:
    def visit_integer_node(self, node):
        raise NotImplementedError()

    def visit_variable_node(self, node):
        raise NotImplementedError()
    
    def visit_float_node(self, node):
        raise NotImplementedError()
    
    def visit_boolean_node(self, node):
        raise NotImplementedError()
    
    def visit_colour_node(self, node):
        raise NotImplementedError()
    
    def visit_pad_width_node(self, node):
        raise NotImplementedError()
    
    def visit_pad_height_node(self, node):
        raise NotImplementedError()
    
    def visit_pad_read_node(self, node):
        raise NotImplementedError()
    
    def visit_pad_rand_int_node(self, node):
        raise NotImplementedError()

    def visit_assignment_node(self, node):
        raise NotImplementedError()
    
    def visit_block_node(self, node):
        raise NotImplementedError()
    
    def inc_tab_count(self):
        raise NotImplementedError()
    
    def dec_tab_count(self):
        raise NotImplementedError()

class PrintNodesVisitor(ASTVisitor):
    def __init__(self):
        self.name = "Print Tree Visitor"
        self.node_count = 0
        self.tab_count = 0

    def inc_tab_count(self):
        self.tab_count += 1

    def dec_tab_count(self):
        self.tab_count -= 1
        
    def visit_integer_node(self, int_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Integer value::", int_node.value)

    def visit_variable_node(self, var_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Variable => ", var_node.lexeme)

    def visit_float_node(self, float_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Float value::", float_node.value)

    def visit_boolean_node(self, bool_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Boolean value::", bool_node.value)

    def visit_colour_node(self, colour_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Colour value::", colour_node.value)

    def visit_pad_width_node(self, pad_width_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Pad Width value")

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


    def visit_assignment_node(self, ass_node):
        self.node_count += 1
        print('\t' * self.tab_count, "Assignment node => ")
        self.inc_tab_count()        
        ass_node.id.accept(self)
        ass_node.expr.accept(self)
        self.dec_tab_count()

    def visit_block_node(self, block_node):
        self.node_count += 1
        print('\t' * self.tab_count, "New Block => ")
        self.inc_tab_count()
        
        for st in block_node.stmts:
            st.accept(self)
        
        self.dec_tab_count()
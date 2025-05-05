import astnodes as ast
import lexer as lex

class Parser:
    def __init__(self, src_program_str):
        self.lexer = lex.Lexer()
        self.index = -1  #start at -1 so that the first token is at index 0
        self.src_program = src_program_str
        self.tokens = self.lexer.GenerateTokens(self.src_program)
        self.crtToken = lex.Token("", lex.TokenType.error)
        self.nextToken = lex.Token("", lex.TokenType.error)
        self.ASTroot = ast.ASTProgramNode()

    def NextTokenSkipWS_Comments(self):
        self.index += 1   #Gets next token 
        if (self.index < len(self.tokens)):
            self.crtToken = self.tokens[self.index]
        else:
            self.crtToken = lex.Token(lex.TokenType.end, "END")

    def NextToken(self):
        self.NextTokenSkipWS_Comments()
        while (self.crtToken.type == lex.TokenType.whitespace 
            or self.crtToken.type == lex.TokenType.linecomment
            or self.crtToken.type == lex.TokenType.blockcomment):
            self.NextTokenSkipWS_Comments()
                

    def ParseLiteral(self):
        if self.crtToken.type == lex.TokenType.integer:
            val = self.crtToken.lexeme
            self.NextToken()
            return ast.ASTIntegerNode(val)

        elif self.crtToken.type == lex.TokenType.floatliteral:
            val = self.crtToken.lexeme
            self.NextToken()
            return ast.ASTFloatNode(val)

        elif self.crtToken.type == lex.TokenType.booleanliteral:
            val = self.crtToken.lexeme
            self.NextToken()
            return ast.ASTBooleanNode(val)

        elif self.crtToken.type == lex.TokenType.colourliteral:
            val = self.crtToken.lexeme
            self.NextToken()
            return ast.ASTColourNode(val)

        else:
            raise Exception("Syntax Error: Expected a literal.")

    def ParseExpression(self):
        
        # Delegate literal types
        if self.crtToken.type in [
            lex.TokenType.integer,
            lex.TokenType.floatliteral,
            lex.TokenType.booleanliteral,
            lex.TokenType.colourliteral
        ]:
            return self.ParseLiteral()

        if self.crtToken.type == lex.TokenType.kw__width:
            self.NextToken()
            return ast.ASTPadWidthNode()

        elif self.crtToken.type == lex.TokenType.kw__height:
            self.NextToken()
            return ast.ASTPadHeightNode()

        elif self.crtToken.type == lex.TokenType.identifier:
            value = self.crtToken.lexeme
            self.NextToken()
            return ast.ASTVariableNode(value)
        elif self.crtToken.type == lex.TokenType.kw__read:
            self.NextToken()
            expr1 = self.ParseExpression()
            if self.crtToken.type != lex.TokenType.comma:
                print("Syntax Error: expected ',' after first expression in __read")
                return ast.ASTErrorNode()
            self.NextToken()
            expr2 = self.ParseExpression()
            return ast.ASTPadReadNode(expr1, expr2)

        elif self.crtToken.type == lex.TokenType.kw__random_int:
            self.NextToken()
            expr = self.ParseExpression()
            return ast.ASTPadRandINode(expr)

        else:
            print(f"Syntax error: Unexpected token {self.crtToken.type}")
            return None

    def ParseAssignment(self):
        #Assignment is made up of two main parts; the LHS (the variable) and RHS (the expression)
        if (self.crtToken.type == lex.TokenType.identifier):
            #create AST node to store the identifier            
            assignment_lhs = ast.ASTVariableNode(self.crtToken.lexeme)
            self.NextToken()
            #print("Variable Token Matched ::: Nxt Token is ", self.crtToken.type, self.crtToken.lexeme)

        if (self.crtToken.type == lex.TokenType.equals):
            #no need to do anything ... token can be discarded
            self.NextToken()
            #print("EQ Token Matched ::: Nxt Token is ", self.crtToken.type, self.crtToken.lexeme)

        #Next sequence of tokens should make up an expression ... therefor call ParseExpression that will return the subtree representing that expression
        assignment_rhs = self.ParseExpression()
                
        return ast.ASTAssignmentNode(assignment_lhs, assignment_rhs)
            
    def ParseStatement(self):
        #At the moment we only have assignment statements .... you'll need to add more for the assignment - branching depends on the token type
        return self.ParseAssignment()

    def ParseBlock(self):
        #At the moment we only have assignment statements .... you'll need to add more for the assignment - branching depends on the token type

        block = ast.ASTBlockNode()

        while (self.crtToken.type != lex.TokenType.end):
            #print("New Statement - Processing Initial Token:: ", self.crtToken.type, self.crtToken.lexeme)
            s = self.ParseStatement()
            block.add_statement(s)
            if (self.crtToken.type == lex.TokenType.semicolon):
                self.NextToken()
            else:
                print("Syntax Error - No Semicolon separating statements in block")
                break
        
        return block

    def ParseProgram(self):                        
        self.NextToken()  #set crtToken to the first token (skip all WS)
        b = self.ParseBlock()        
        return b        

    def Parse(self):        
        self.ASTroot = self.ParseProgram()


parser = Parser(("x = __read 5, 10; y = __random_int 7;"))
parser.Parse()

print_visitor = ast.PrintNodesVisitor()
parser.ASTroot.accept(print_visitor)
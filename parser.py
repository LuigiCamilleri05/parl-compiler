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
                

    def ParseExpression(self):
        #for now we'll assume an expression can only be an integer
        if (self.crtToken.type == lex.TokenType.integer):
            value = self.crtToken.lexeme
            self.NextToken()
            return ast.ASTIntegerNode(value)

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


parser = Parser("     x=   23 ; y=  100;  z = 23 ;")
parser.Parse()

print_visitor = ast.PrintNodesVisitor()
parser.ASTroot.accept(print_visitor)
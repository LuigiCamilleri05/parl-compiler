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

    def ParsePadRead(self):
        if self.crtToken.type != lex.TokenType.kw__read:
            raise Exception("Syntax Error: Expected '__read'")
        self.NextToken()

        expr1 = self.ParseExpression()

        if self.crtToken.type != lex.TokenType.comma:
            raise Exception("Syntax Error: Expected ',' in __read")
        self.NextToken()

        expr2 = self.ParseExpression()

        return ast.ASTPadReadNode(expr1, expr2)
    
    def ParsePadRandI(self):
        if self.crtToken.type != lex.TokenType.kw__random_int:
            raise Exception("Syntax Error: Expected '__random_int'")
        self.NextToken()

        expr = self.ParseExpression()
        return ast.ASTPadRandINode(expr)
                
    def ParseType(self):
        if self.crtToken.type in [
            lex.TokenType.kw_int,
            lex.TokenType.kw_float,
            lex.TokenType.kw_bool,
            lex.TokenType.kw_colour
        ]:
            type_name = self.crtToken.lexeme
            self.NextToken()
            return type_name
        else:
            raise Exception("Syntax Error: Expected a type.")

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
        
    def ParseFunctionCall(self, function_name):
        # Assumes current token is '('
        if self.crtToken.type != lex.TokenType.lparen:
            raise Exception("Syntax Error: Expected '(' in function call.")
        self.NextToken()

        args = []
        if self.crtToken.type != lex.TokenType.rparen:
            # Parse first arg
            args.append(self.ParseExpression())
            # Parse remaining args
            while self.crtToken.type == lex.TokenType.comma:
                self.NextToken()
                args.append(self.ParseExpression())

        if self.crtToken.type != lex.TokenType.rparen:
            raise Exception("Syntax Error: Expected ')' after function arguments.")
        self.NextToken()

        return ast.ASTFunctionCallNode(function_name, args)


    def ParseFactor(self):
        tok = self.crtToken

        if tok.type in [
            lex.TokenType.integer,
            lex.TokenType.floatliteral,
            lex.TokenType.booleanliteral,
            lex.TokenType.colourliteral
        ]:
            return self.ParseLiteral()

        elif tok.type == lex.TokenType.identifier:
            # Could be a variable or function call
            id_name = tok.lexeme
            self.NextToken()
            if self.crtToken.type == lex.TokenType.lparen:
                return self.ParseFunctionCall(id_name)
            else:
                return ast.ASTVariableNode(id_name)

        elif tok.type == lex.TokenType.lparen:
            self.NextToken()
            expr = self.ParseExpression()
            if self.crtToken.type != lex.TokenType.rparen:
                raise Exception("Syntax Error: expected ')'")
            self.NextToken()
            return expr

        elif tok.type in [lex.TokenType.minus, lex.TokenType.kw_not]:
            op = tok.lexeme
            self.NextToken()
            expr = self.ParseFactor()
            return ast.ASTUnaryOpNode(op, expr)

        elif tok.type == lex.TokenType.kw__read:
            return self.ParsePadRead()

        elif tok.type == lex.TokenType.kw__random_int:
            return self.ParsePadRandI()

        elif tok.type == lex.TokenType.kw__width:
            self.NextToken()
            return ast.ASTPadWidthNode()

        elif tok.type == lex.TokenType.kw__height:
            self.NextToken()
            return ast.ASTPadHeightNode()

        else:
            raise Exception(f"Syntax Error: Unexpected token {tok.type} in factor")

    def ParseTerm(self):
        left = self.ParseFactor()

        while self.crtToken.type in [
            lex.TokenType.multiply,
            lex.TokenType.slash,
            lex.TokenType.kw_and
        ]:
            op = self.crtToken.lexeme
            self.NextToken()
            right = self.ParseFactor()
            left = ast.ASTBinaryOpNode(op, left, right)

        return left

    def ParseSimpleExpression(self):
        left = self.ParseTerm()

        while self.crtToken.type in [
            lex.TokenType.plus,
            lex.TokenType.minus,
            lex.TokenType.kw_or
        ]:
            op = self.crtToken.lexeme
            self.NextToken()
            right = self.ParseTerm()
            left = ast.ASTBinaryOpNode(op, left, right)

        return left

    def ParseExpression(self):
        left = self.ParseSimpleExpression()

        if self.crtToken.type in [
            lex.TokenType.less,
            lex.TokenType.greater,
            lex.TokenType.equal_equal,
            lex.TokenType.not_equal,
            lex.TokenType.less_equal,
            lex.TokenType.greater_equal
        ]:
            op = self.crtToken.lexeme
            self.NextToken()
            right = self.ParseSimpleExpression()
            left = ast.ASTBinaryOpNode(op, left, right)

        if self.crtToken.type == lex.TokenType.kw_as:
            self.NextToken()
            cast_type = self.ParseType()
            left = ast.ASTCastNode(left, cast_type)

        return left

    def ParseVariableDecl(self):
        # Match 'let'
        if self.crtToken.type != lex.TokenType.kw_let:
            raise Exception("Syntax Error: Expected 'let' at start of variable declaration.")
        self.NextToken()

        # Match identifier
        if self.crtToken.type != lex.TokenType.identifier:
            raise Exception("Syntax Error: Expected identifier after 'let'.")
        identifier = self.crtToken.lexeme
        self.NextToken()

        # Match ':'
        if self.crtToken.type != lex.TokenType.colon:
            raise Exception("Syntax Error: Expected ':' after identifier in declaration.")
        self.NextToken()

        vartype = self.ParseType()

        # Match '='
        if self.crtToken.type != lex.TokenType.equals:
            raise Exception("Syntax Error: Expected '=' in variable declaration.")
        self.NextToken()

        # Parse the initializer expression
        expr = self.ParseExpression()

        return ast.ASTVariableDeclNode(identifier, vartype, expr)


    def ParseAssignment(self):
        #Assignment is made up of two main parts; the LHS (the variable) and RHS (the expression)
        if (self.crtToken.type == lex.TokenType.identifier):
            #create AST node to store the identifier            
            assignment_lhs = self.ParseExpression()
            if not isinstance(assignment_lhs, ast.ASTVariableNode):
                raise Exception("Syntax Error: Left-hand side must be a variable")
            
            #print("Variable Token Matched ::: Nxt Token is ", self.crtToken.type, self.crtToken.lexeme)

        if (self.crtToken.type == lex.TokenType.equals):
            #no need to do anything ... token can be discarded
            self.NextToken()
            #print("EQ Token Matched ::: Nxt Token is ", self.crtToken.type, self.crtToken.lexeme)

        #Next sequence of tokens should make up an expression ... therefor call ParseExpression that will return the subtree representing that expression
        assignment_rhs = self.ParseExpression()
                
        return ast.ASTAssignmentNode(assignment_lhs, assignment_rhs)
            
    def ParseStatement(self):
        if (self.crtToken.type == lex.TokenType.kw_let):
            return self.ParseVariableDecl()
        elif (self.crtToken.type == lex.TokenType.identifier):
            return self.ParseAssignment()
        elif (self.crtToken.type == lex.TokenType.kw__print):
            return #TODO
        elif (self.crtToken.type == lex.TokenType.kw__delay):
            return #TODO
        elif (self.crtToken.type == lex.TokenType.kw__write):
            return #TODO
        elif (self.crtToken.type == lex.TokenType.kw_if):
            return #TODO
        elif (self.crtToken.type == lex.TokenType.kw_for):
            return #TODO
        elif (self.crtToken.type == lex.TokenType.kw_while):
            return #TODO
        elif (self.crtToken.type == lex.TokenType.kw_return):
            return #TODO
        elif (self.crtToken.type == lex.TokenType.kw_fun):
            return #TODO
        elif self.crtToken.type == lex.TokenType.lbrace:
            return self.ParseBlock()
        else:
            raise Exception(f"Syntax Error: Unexpected token {self.crtToken.type}")

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
        self.NextToken()  #set crtToken to the first token (skip all WS and comments)
        b = self.ParseBlock()        
        return b        

    def Parse(self):        
        self.ASTroot = self.ParseProgram()


parser = Parser(("a = 5;"))
parser.Parse()

print_visitor = ast.PrintNodesVisitor()
parser.ASTroot.accept(print_visitor)
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
            or self.crtToken.type == lex.TokenType.blockcomment
            or self.crtToken.type == lex.TokenType.newline):
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

        if self.crtToken.type == lex.TokenType.equals:
            self.NextToken()
            expr = self.ParseExpression()
            return ast.ASTVariableDeclNode(identifier, vartype, expr)

        elif self.crtToken.type == lex.TokenType.lbracket:
            return self.ParseVariableDeclArray(identifier, vartype)

        else:
            raise Exception("Syntax Error: Expected '=' or '[' in variable declaration")
        
    def ParseVariableDeclArray(self, identifier, vartype):
        self.NextToken()

        # Case 1: declared size [3] = [val]
        if self.crtToken.type == lex.TokenType.integer:
            size = ast.ASTIntegerNode(self.crtToken.lexeme)
            self.NextToken()

            if self.crtToken.type != lex.TokenType.rbracket:
                raise Exception("Expected ']' after array size")
            self.NextToken()

            if self.crtToken.type != lex.TokenType.equals:
                raise Exception("Expected '=' after ']' in sized array")
            self.NextToken()

            if self.crtToken.type != lex.TokenType.lbracket:
                raise Exception("Expected '[' to start array literal")
            self.NextToken()

            value = self.ParseLiteral()

            if self.crtToken.type != lex.TokenType.rbracket:
                raise Exception("Expected ']' after single array literal")
            self.NextToken()

            return ast.ASTArrayDeclNode(identifier, vartype, size, [value])

        # Case 2: inferred size [] = [val, val, ...]
        elif self.crtToken.type == lex.TokenType.rbracket:
            size = None
            self.NextToken()

            if self.crtToken.type != lex.TokenType.equals:
                raise Exception("Expected '=' after ']' in inferred array")
            self.NextToken()

            if self.crtToken.type != lex.TokenType.lbracket:
                raise Exception("Expected '[' to start array literal")
            self.NextToken()

            values = [self.ParseLiteral()]

            while self.crtToken.type == lex.TokenType.comma:
                self.NextToken()
                values.append(self.ParseLiteral())

            if self.crtToken.type != lex.TokenType.rbracket:
                raise Exception("Expected ']' to close array literal")
            self.NextToken()

            return ast.ASTArrayDeclNode(identifier, vartype, size, values)

        else:
            raise Exception("Syntax Error: Invalid array declaration format")



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
    
    def ParsePrintStatement(self):
        if self.crtToken.type != lex.TokenType.kw__print:
            raise Exception("Syntax Error: Expected '__print'")
        self.NextToken()

        expr = self.ParseExpression()
        return ast.ASTPrintNode(expr)
    
    def ParseDelayStatement(self):
        if self.crtToken.type != lex.TokenType.kw__delay:
            raise Exception("Syntax Error: Expected '__delay'")
        self.NextToken()

        expr = self.ParseExpression()
        return ast.ASTDelayNode(expr)
    
    def ParseWriteStatement(self):
        if self.crtToken.type == lex.TokenType.kw__write:
            self.NextToken()
            x_expr = self.ParseExpression()
            if self.crtToken.type != lex.TokenType.comma:
                raise Exception("Syntax Error: Expected ','")
            self.NextToken()
            y_expr = self.ParseExpression()
            if self.crtToken.type != lex.TokenType.comma:
                raise Exception("Syntax Error: Expected ','")
            self.NextToken()
            val_expr = self.ParseExpression()
            return ast.ASTWriteNode(x_expr, y_expr, val_expr)

        elif self.crtToken.type == lex.TokenType.kw__write_box:
            self.NextToken()
            x_expr = self.ParseExpression()
            if self.crtToken.type != lex.TokenType.comma:
                raise Exception("Syntax Error: Expected ','")
            self.NextToken()
            y_expr = self.ParseExpression()
            if self.crtToken.type != lex.TokenType.comma:
                raise Exception("Syntax Error: Expected ','")
            self.NextToken()
            w_expr = self.ParseExpression()
            if self.crtToken.type != lex.TokenType.comma:
                raise Exception("Syntax Error: Expected ','")
            self.NextToken()
            h_expr = self.ParseExpression()
            if self.crtToken.type != lex.TokenType.comma:
                raise Exception("Syntax Error: Expected ','")
            self.NextToken()
            val_expr = self.ParseExpression()
            return ast.ASTWriteBoxNode(x_expr, y_expr, w_expr, h_expr, val_expr)

        else:
            raise Exception("Syntax Error: Expected '__write' or '__write_box'")
        
    def ParseIfStatement(self):
        if self.crtToken.type != lex.TokenType.kw_if:
            raise Exception("Syntax Error: Expected 'if'")
        self.NextToken()

        if self.crtToken.type != lex.TokenType.lparen:
            raise Exception("Syntax Error: Expected '(' after 'if'")
        self.NextToken()

        condition = self.ParseExpression()

        if self.crtToken.type != lex.TokenType.rparen:
            raise Exception("Syntax Error: Expected ')' after condition")
        self.NextToken()

        then_block = self.ParseBlock()

        else_block = None
        if self.crtToken.type == lex.TokenType.kw_else:
            self.NextToken()
            else_block = self.ParseBlock()

        return ast.ASTIfNode(condition, then_block, else_block)

    def ExpectSemicolon(self):
        if self.crtToken.type != lex.TokenType.semicolon:
            raise Exception("Syntax Error: Expected ';' after statement")
        self.NextToken()

            
    def ParseStatement(self):
        if self.crtToken.type == lex.TokenType.kw_let:
            stmt = self.ParseVariableDecl()
            self.ExpectSemicolon()
            return stmt
        elif self.crtToken.type == lex.TokenType.identifier:
            stmt = self.ParseAssignment()
            self.ExpectSemicolon()
            return stmt
        elif self.crtToken.type == lex.TokenType.kw__print:
            stmt = self.ParsePrintStatement()
            self.ExpectSemicolon()
            return stmt
        elif self.crtToken.type == lex.TokenType.kw__delay:
            stmt = self.ParseDelayStatement()
            self.ExpectSemicolon()
            return stmt
        elif self.crtToken.type in [lex.TokenType.kw__write, lex.TokenType.kw__write_box]:
            stmt = self.ParseWriteStatement()
            self.ExpectSemicolon()
            return stmt
        elif (self.crtToken.type == lex.TokenType.kw_if):
            return self.ParseIfStatement()
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
        if self.crtToken.type != lex.TokenType.lbrace:
            raise Exception("Syntax Error: Expected '{' to start a block")

        self.NextToken()  # consume '{'
        block = ast.ASTBlockNode()

        while self.crtToken.type != lex.TokenType.rbrace:
            if self.crtToken.type == lex.TokenType.end:
                raise Exception("Syntax Error: Unexpected end of input inside block")
            stmt = self.ParseStatement()
            if stmt:
                block.add_statement(stmt)

        self.NextToken()  # consume '}'
        return block


    def ParseProgram(self):
        self.NextToken()
        program = ast.ASTBlockNode()
        while self.crtToken.type != lex.TokenType.end:
            stmt = self.ParseStatement()
            if stmt:
                program.add_statement(stmt)
        return program     

    def Parse(self):        
        self.ASTroot = self.ParseProgram()


parser = Parser(("""

    let x : int = 5;
    if (x < 10) {
        __print x;
    } else {
        __print 0;
    }

"""))
parser.Parse()

print_visitor = ast.PrintNodesVisitor()
parser.ASTroot.accept(print_visitor)
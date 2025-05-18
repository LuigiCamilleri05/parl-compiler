# Importing modules from the same directory
import astnodes as ast # Gets the AST nodes
import lexer as lex # Performs lexical analysis

# Parser class parsing the source program and generate ASTs
class Parser:
    
    # Constructor initializing the parser
    def __init__(self, src_program_str):
        self.lexer = lex.Lexer()
        self.index = -1  # Starts at -1 so that the first token is at index 0
        self.src_program = src_program_str
        self.tokens = self.lexer.GenerateTokensNoPrinting(self.src_program)
        self.crtToken = lex.Token("", lex.TokenType.error)
        self.nextToken = lex.Token("", lex.TokenType.error)
        

    # Function to skip whitespace and comments
    def NextTokenSkipWS_Comments(self):
        self.index += 1   # Gets next token 
        if (self.index < len(self.tokens)):
            # Assigns the next token to the current token
            self.crtToken = self.tokens[self.index]
        else:
            self.crtToken = lex.Token(lex.TokenType.end, "END")

    # Function which skips whitespace and comments by calling the NextTokenSkipWS_Comments function
    # once when it is not a whitespace or comment and keeps calling the NextTokenSkipWS_Comments if it is a whitespace or comment
    def NextToken(self):
        self.NextTokenSkipWS_Comments()
        while (self.crtToken.type == lex.TokenType.whitespace 
            or self.crtToken.type == lex.TokenType.linecomment
            or self.crtToken.type == lex.TokenType.blockcomment
            or self.crtToken.type == lex.TokenType.newline):
            self.NextTokenSkipWS_Comments()

        # Helper functions to check for specific tokens instead of repeating code
    def ExpectSemicolon(self):
        if self.crtToken.type != lex.TokenType.semicolon:
            raise Exception("Syntax Error: Expected ';' after statement")
        self.NextToken()

    def ExpectComma(self):
        if self.crtToken.type != lex.TokenType.comma:
            raise Exception("Syntax Error: Expected ','")
        self.NextToken()

    # The rest of the code are the parsing functions
    # The parsing functions are organized by the PARl EBNF grammar
    # The parsing functions check token by token using self.NextToken() to move to the next token
    # Every time a token is checked to see if it is the expected token in the grammar by checking its type
    # The functions call each other recursively and use each other as arguments to parse the entire program

    # ⟨Type⟩
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

    # ⟨Literal⟩
    def ParseLiteral(self):
        # ⟨IntegerLiteral⟩
        if self.crtToken.type == lex.TokenType.integer:
            val = self.crtToken.lexeme
            self.NextToken()
            return ast.ASTIntegerNode(val)
        
        # ⟨FloatLiteral⟩
        elif self.crtToken.type == lex.TokenType.floatliteral:
            val = self.crtToken.lexeme
            self.NextToken()
            return ast.ASTFloatNode(val)

        # ⟨BooleanLiteral⟩
        elif self.crtToken.type == lex.TokenType.booleanliteral:
            val = self.crtToken.lexeme
            self.NextToken()
            return ast.ASTBooleanNode(val)

        # ⟨ColourLiteral⟩
        elif self.crtToken.type == lex.TokenType.colourliteral:
            val = self.crtToken.lexeme
            self.NextToken()
            return ast.ASTColourNode(val)

        else:
            raise Exception("Syntax Error: Expected a literal.")

    # ⟨PadRead⟩
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
    
    # ⟨PadRandI⟩
    def ParsePadRandI(self):
        if self.crtToken.type != lex.TokenType.kw__random_int:
            raise Exception("Syntax Error: Expected '__random_int'")
        self.NextToken()

        expr = self.ParseExpression()
        return ast.ASTPadRandINode(expr)
        
    # ⟨FunctionCall⟩
    def ParseFunctionCall(self, function_name):
        # Assumes current token is '('
        # ⟨ActualParams⟩
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

    # ⟨Factor⟩
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
            index_expr = None
            self.NextToken()

            # ⟨SubExpr⟩
            if self.crtToken.type == lex.TokenType.lbracket:
                self.NextToken()
                index_expr = self.ParseExpression()
                if self.crtToken.type != lex.TokenType.rbracket:
                    raise Exception("Syntax Error: Expected ']' after array index")
                self.NextToken()
            if self.crtToken.type == lex.TokenType.lparen:
                return self.ParseFunctionCall(id_name)
            else:
                return ast.ASTVariableNode(id_name, index_expr)

        elif tok.type == lex.TokenType.lparen:
            self.NextToken()
            expr = self.ParseExpression()
            if self.crtToken.type != lex.TokenType.rparen:
                raise Exception("Syntax Error: expected ')'")
            self.NextToken()
            return expr

        # ⟨UnaryOp⟩
        elif tok.type in [lex.TokenType.minus, lex.TokenType.kw_not]:
            op = tok.lexeme
            self.NextToken()
            expr = self.ParseExpression()
            return ast.ASTUnaryOpNode(op, expr)

        elif tok.type == lex.TokenType.kw__read:
            return self.ParsePadRead()

        elif tok.type == lex.TokenType.kw__random_int:
            return self.ParsePadRandI()

        # ⟨PadWidth⟩
        elif tok.type == lex.TokenType.kw__width:
            self.NextToken()
            return ast.ASTPadWidthNode()
        
        # ⟨PadHeight⟩
        elif tok.type == lex.TokenType.kw__height:
            self.NextToken()
            return ast.ASTPadHeightNode()

        else:
            raise Exception(f"Syntax Error: Unexpected token {tok.type} in factor")

    # ⟨Term⟩
    def ParseTerm(self):
        left = self.ParseFactor()

        # ⟨MultiplicativeOp⟩
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

    # ⟨SimpleExpr⟩
    def ParseSimpleExpression(self):
        left = self.ParseTerm()

        # ⟨AdditiveOp⟩
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
    
    # ⟨Expr⟩
    def ParseExpression(self):
        left = self.ParseSimpleExpression()

        # ⟨RelationalOp⟩
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
    
    # ⟨Assignment⟩
    def ParseAssignment(self):
        if (self.crtToken.type == lex.TokenType.identifier):
            assignment_lhs = self.ParseExpression()
            if not isinstance(assignment_lhs, ast.ASTVariableNode):
                raise Exception("Syntax Error: Left-hand side must be a variable")

        if (self.crtToken.type == lex.TokenType.equals):
            self.NextToken()
        assignment_rhs = self.ParseExpression()

        return ast.ASTAssignmentNode(assignment_lhs, assignment_rhs)

    # ⟨VariableDecl⟩
    def ParseVariableDecl(self):
        if self.crtToken.type != lex.TokenType.kw_let:
            raise Exception("Syntax Error: Expected 'let' at start of variable declaration.")
        self.NextToken()

        if self.crtToken.type != lex.TokenType.identifier:
            raise Exception("Syntax Error: Expected identifier after 'let'.")
        identifier = self.crtToken.lexeme
        self.NextToken()

        if self.crtToken.type != lex.TokenType.colon:
            raise Exception("Syntax Error: Expected ':' after identifier in declaration.")
        self.NextToken()

        vartype = self.ParseType()

        if self.crtToken.type == lex.TokenType.equals:
            self.NextToken()
            expr = self.ParseExpression()
            return ast.ASTVariableDeclNode(identifier, vartype, expr)

        # ⟨VariableDeclSuffix⟩
        elif self.crtToken.type == lex.TokenType.lbracket:
            return self.ParseVariableDeclArray(identifier, vartype)

        else:
            raise Exception("Syntax Error: Expected '=' or '[' in variable declaration")
        
    # ⟨VariableDeclArray⟩    
    def ParseVariableDeclArray(self, identifier, vartype):
        self.NextToken()

        # Case 1: declared size array
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

            return ast.ASTArrayDeclNode(identifier, vartype + "[]", size, [value])

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

            return ast.ASTArrayDeclNode(identifier, vartype + "[]", size, values)

        else:
            raise Exception("Syntax Error: Invalid array declaration format")
        
    # ⟨PrintStatement⟩    
    def ParsePrintStatement(self):
        if self.crtToken.type != lex.TokenType.kw__print:
            raise Exception("Syntax Error: Expected '__print'")
        self.NextToken()

        expr = self.ParseExpression()
        return ast.ASTPrintNode(expr)
    
    # ⟨DelayStatement⟩
    def ParseDelayStatement(self):
        if self.crtToken.type != lex.TokenType.kw__delay:
            raise Exception("Syntax Error: Expected '__delay'")
        self.NextToken()

        expr = self.ParseExpression()
        return ast.ASTDelayNode(expr)
    
    # ⟨ClearStatement⟩ which is added to the language
    def ParseClearStatement(self):
        if self.crtToken.type != lex.TokenType.kw__clear:
            raise Exception("Syntax Error: Expected '__clear'")
        self.NextToken()

        expr = self.ParseExpression()
        return ast.ASTClearNode(expr)
    
    # ⟨WriteStatement⟩
    def ParseWriteStatement(self):
        if self.crtToken.type == lex.TokenType.kw__write:
            self.NextToken()
            x_expr = self.ParseExpression()
            self.ExpectComma()
            y_expr = self.ParseExpression()
            self.ExpectComma()
            val_expr = self.ParseExpression()
            return ast.ASTWriteNode(x_expr, y_expr, val_expr)

        elif self.crtToken.type == lex.TokenType.kw__write_box:
            self.NextToken()
            x_expr = self.ParseExpression()
            self.ExpectComma()
            y_expr = self.ParseExpression()
            self.ExpectComma()
            w_expr = self.ParseExpression()
            self.ExpectComma()
            h_expr = self.ParseExpression()
            self.ExpectComma()
            val_expr = self.ParseExpression()
            return ast.ASTWriteBoxNode(x_expr, y_expr, w_expr, h_expr, val_expr)

        else:
            raise Exception("Syntax Error: Expected '__write' or '__write_box'")
        
    # ⟨RtrnStatement⟩
    def ParseRtrnStatement(self):
        if self.crtToken.type != lex.TokenType.kw_return:
            raise Exception("Syntax Error: Expected '_return'")
        self.NextToken()

        expr = self.ParseExpression()
        return ast.ASTRtrnNode(expr)
        
    # ⟨IfStatement⟩
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
    
    # ⟨ForStatement⟩
    def ParseForStatement(self):
        if self.crtToken.type != lex.TokenType.kw_for:
            raise Exception("Syntax Error: Expected 'for'")
        self.NextToken()

        if self.crtToken.type != lex.TokenType.lparen:
            raise Exception("Syntax Error: Expected '(' after 'for'")
        self.NextToken()

        # Optional initializer
        init = None
        if self.crtToken.type == lex.TokenType.kw_let:
            init = self.ParseVariableDecl()

        self.ExpectSemicolon()

        # Condition (required)
        condition = self.ParseExpression()

        self.ExpectSemicolon()

        # Optional update
        update = None
        if self.crtToken.type == lex.TokenType.identifier:
            update = self.ParseAssignment()

        if self.crtToken.type != lex.TokenType.rparen:
            raise Exception("Syntax Error: Expected ')' to close 'for' loop control")
        self.NextToken()

        # Block
        body = self.ParseBlock()

        return ast.ASTForNode(init, condition, update, body)
    
    # ⟨WhileStatement⟩  
    def ParseWhileStatement(self):
        if self.crtToken.type != lex.TokenType.kw_while:
            raise Exception("Syntax Error: Expected 'while'")
        self.NextToken()

        if self.crtToken.type != lex.TokenType.lparen:
            raise Exception("Syntax Error: Expected '(' after 'while'")
        self.NextToken()

        condition = self.ParseExpression()

        if self.crtToken.type != lex.TokenType.rparen:
            raise Exception("Syntax Error: Expected ')' after condition")
        self.NextToken()

        body = self.ParseBlock()

        return ast.ASTWhileNode(condition, body)
    
    # ⟨FormalParam⟩
    def ParseFormalParam(self):
        if self.crtToken.type != lex.TokenType.identifier:
            raise Exception("Expected identifier in parameter list")
        name = self.crtToken.lexeme
        self.NextToken()

        if self.crtToken.type != lex.TokenType.colon:
            raise Exception("Expected ':' after parameter name")
        self.NextToken()

        param_type = self.ParseType()
        size = None

        # Check for array type
        if self.crtToken.type == lex.TokenType.lbracket:
            self.NextToken()
            if self.crtToken.type != lex.TokenType.integer:
                raise Exception("Expected integer size for array parameter")
            size = ast.ASTIntegerNode(self.crtToken.lexeme)
            self.NextToken()
            if self.crtToken.type != lex.TokenType.rbracket:
                raise Exception("Expected ']' after array size")
            self.NextToken()
            param_type += "[]"

        
        return (name, param_type, size)
    
    # ⟨FormalParams⟩
    def ParseFormalParams(self):
        params = [self.ParseFormalParam()]
        while self.crtToken.type == lex.TokenType.comma:
            self.NextToken()
            params.append(self.ParseFormalParam())
        return params

    # ⟨FunctionDecl⟩
    def ParseFunctionDecl(self):
        if self.crtToken.type != lex.TokenType.kw_fun:
            raise Exception("Syntax Error: Expected 'fun' at start of function declaration")
        self.NextToken()

        if self.crtToken.type != lex.TokenType.identifier:
            raise Exception("Expected function name after 'fun'")
        name = self.crtToken.lexeme
        self.NextToken()

        if self.crtToken.type != lex.TokenType.lparen:
            raise Exception("Expected '(' after function name")
        self.NextToken()

        params = []
        if self.crtToken.type != lex.TokenType.rparen:
            params = self.ParseFormalParams()

        if self.crtToken.type != lex.TokenType.rparen:
            raise Exception("Expected ')' after parameters")
        self.NextToken()

        if self.crtToken.type != lex.TokenType.arrow:
            raise Exception("Expected '->' for return type")
        self.NextToken()

        return_type = self.ParseType()
        return_size = None

        if self.crtToken.type == lex.TokenType.lbracket:
            self.NextToken()
            if self.crtToken.type != lex.TokenType.integer:
                raise Exception("Expected size inside return type brackets")
            return_size = self.crtToken.lexeme
            self.NextToken()
            if self.crtToken.type != lex.TokenType.rbracket:
                raise Exception("Expected ']' after return size")
            self.NextToken()

        body = self.ParseBlock()
        return ast.ASTFunctionDeclNode(name, params, return_type, return_size, body)

    # ⟨Statement⟩ 
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
        elif self.crtToken.type == lex.TokenType.kw__clear:
            stmt = self.ParseClearStatement()
            self.ExpectSemicolon()
            return stmt
        elif self.crtToken.type in [lex.TokenType.kw__write, lex.TokenType.kw__write_box]:
            stmt = self.ParseWriteStatement()
            self.ExpectSemicolon()
            return stmt
        elif (self.crtToken.type == lex.TokenType.kw_if):
            return self.ParseIfStatement()
        elif (self.crtToken.type == lex.TokenType.kw_for):
            return self.ParseForStatement()
        elif (self.crtToken.type == lex.TokenType.kw_while):
            return self.ParseWhileStatement()
        elif (self.crtToken.type == lex.TokenType.kw_return):
            stmt = self.ParseRtrnStatement()
            self.ExpectSemicolon()
            return stmt
        elif (self.crtToken.type == lex.TokenType.kw_fun):
            return self.ParseFunctionDecl()
        elif self.crtToken.type == lex.TokenType.lbrace:
            return self.ParseBlock()
        else:
            raise Exception(f"Syntax Error: Unexpected token {self.crtToken.type}")

    # ⟨Block⟩
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

        self.NextToken()  # Consumes '}'
        return block

    # ⟨Program⟩ 
    def ParseProgram(self):
        self.NextToken()
        program = ast.ASTProgramNode()
        while self.crtToken.type != lex.TokenType.end:
            stmt = self.ParseStatement()
            if stmt:
                program.add_statement(stmt)
        return program     

    # Entry point for parsing the entire program into an AST
    def Parse(self):        
        self.ASTroot = self.ParseProgram()
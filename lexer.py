# Lexer for PArl programming language

# enum for token types
from enum import Enum

# TokenType enum represents different token types
class TokenType(Enum):
    identifier = 1
    integer = 2
    hexletter = 3
    equals = 4
    semicolon = 5
    plus = 6
    minus = 7
    multiply = 8
    slash = 9
    less = 10
    greater = 11
    excl = 12
    lparen = 13
    rparen = 14
    lbrace = 15
    rbrace = 16
    lbracket = 17
    rbracket = 18
    colon = 19
    comma = 20
    hash = 21
    dot = 22
    floatliteral = 23
    booleanliteral = 24
    colourliteral = 25
    kw_let = 26
    kw_fun = 27
    kw_if = 28
    kw_else = 29
    kw_for = 30
    kw_while = 31
    kw_return = 32
    kw_as = 33
    kw_not = 34
    kw_and = 35
    kw_or = 36
    kw_float = 37
    kw_int = 38
    kw_bool = 39
    kw_colour = 40
    kw__print = 41
    kw__delay = 42
    kw__write = 43
    kw__write_box = 44
    kw__random_int = 45
    kw__read = 46
    kw__width = 47
    kw__height = 48
    equal_equal = 49     
    not_equal = 50       
    less_equal = 51      
    greater_equal = 52   
    arrow = 53           
    error = 54
    end = 55
    whitespace = 56
    linecomment = 57
    blockcomment = 58
    newline = 59


# Token class represents a token with its type and lexeme
class Token:
    def __init__(self, t, l):
        self.type = t
        self.lexeme = l        

# Lexer class handles the lexical analysis of the input
class Lexer:
    def __init__(self):
        # Initializes the chcaracter categories
        self.lexeme_list = ["letter", "digit", "hexletter", "underscore", "plus", "minus",
                            "multiply", "slash", "equals", "less", "greater", 
                            "excl", "lparen", "rparen", "lbrace", "rbrace",
                            "lbracket", "rbracket", "colon", "comma", "semicolon",
                            "hash", "dot","whitespace", "newline", "other",]
        # Initializes the states and accepting states
        self.states_list = list(range(47))  
        self.states_accp = list(range(1, 24)) + [25] + list(range(28, 34)) + [39, 41, 44, 46]

        # Initializes the transition table
        self.rows = len(self.states_list)
        self.cols = len(self.lexeme_list)
        self.Tx = [[-1 for j in range(self.cols)] for i in range(self.rows)]
        self.InitialiseTxTable();     


    def InitialiseTxTable(self):
        def set_tx(s, l, n):
            self.Tx[s][self.lexeme_list.index(l)] = n

        # Identifiers
        set_tx(0, "letter", 1)
        set_tx(0, "hexletter", 1)
        for l in ["letter", "hexletter", "underscore", "digit"]:
            set_tx(1, l, 1)

        set_tx(0, "underscore", 45)
        set_tx(45, "underscore", 46)
        set_tx(46, "letter", 46)
        set_tx(46, "hexletter", 46)
        set_tx(46, "underscore", 46)


        # Integers
        set_tx(0, "digit", 2)
        set_tx(2, "digit", 2)

        # Operators and Symbols
        ops = {
            "equals": 3, "semicolon": 4, "plus": 5, "minus": 6,
            "multiply": 7, "slash": 8, "less": 9, "greater": 10,
            "excl": 11, "lparen": 12, "rparen": 13, "lbrace": 14,
            "rbrace": 15, "lbracket": 16, "rbracket": 17, "colon": 18,
            "comma": 19, "hash": 20, "dot": 21, "whitespace": 22,
            "newline": 23
        }
        # Loop through the operators and symbols and set the transitions
        for key, val in ops.items():
            set_tx(0, key, val)

        # Floats
        set_tx(2, "dot", 24)
        set_tx(24, "digit", 25)
        set_tx(25, "digit", 25)
        set_tx(25, "letter", 26)
        # For floats with plus or minus sign
        for l in ["plus", "minus"]:
            set_tx(26, l, 27)
        set_tx(26, "digit", 28)
        set_tx(27, "digit", 28)
        set_tx(28, "digit", 28)
        set_tx(28, "letter", 28)
        set_tx(28, "hexletter", 28)

        # Compound operators
        set_tx(3, "equals", 29)
        set_tx(11, "equals", 30)
        set_tx(9, "equals", 31)
        set_tx(10, "equals", 32)

        # Arrow operator
        set_tx(6, "greater", 33)

        # Colour literals
        set_tx(20, "digit", 34)
        set_tx(20, "hexletter", 34)
        # Since colour literals have a fixed length of 7
        for i in range(34, 39):
            set_tx(i, "digit", i + 1)
            set_tx(i, "hexletter", i + 1)

        # Line comments
        set_tx(8, "slash", 40)
        # Loops until the end of the line
        for i, lex in enumerate(self.lexeme_list):
            if lex != "newline":
                self.Tx[40][i] = 40
        set_tx(40, "newline", 41)

        # Block comments
        set_tx(8, "multiply", 42)
        # Loops until the end of the it reaches a *, if there is a / after it, it will be a block comment
        for i in range(len(self.lexeme_list)):
            self.Tx[42][i] = 42
        set_tx(42, "multiply", 43)
        for i in range(len(self.lexeme_list)):
            self.Tx[43][i] = 42
        set_tx(43, "slash", 44)

    # Checks if the state is an accepting state
    def AcceptingStates(self, state):
        try:
            self.states_accp.index(state)
            return True;
        except ValueError:
            return False;

    # Returns the token based on the final state and lexeme
    def GetTokenTypeByFinalState(self, state, lexeme):
        if state == 1:
            # Check if the lexeme is a keyword or identifier
            if lexeme in self.keywords:
                return Token(self.keywords[lexeme], lexeme)
            elif lexeme in ["true", "false"]:
                return Token(TokenType.booleanliteral, lexeme)
            elif lexeme in ["float", "int", "bool", "colour"]:
                return Token(TokenType.type, lexeme)
            else:
                return Token(TokenType.identifier, lexeme)
        elif state == 2:
            return Token(TokenType.integer, lexeme)
        elif state == 3:
            return Token(TokenType.equals, lexeme)
        elif state == 4:
            return Token(TokenType.semicolon, lexeme)
        elif state == 5:
            return Token(TokenType.plus, lexeme)
        elif state == 6:
            return Token(TokenType.minus, lexeme)
        elif state == 7:
            return Token(TokenType.multiply, lexeme)
        elif state == 8:
            return Token(TokenType.slash, lexeme)
        elif state == 9:
            return Token(TokenType.less, lexeme)
        elif state == 10:
            return Token(TokenType.greater, lexeme)
        elif state == 11:
            return Token(TokenType.excl, lexeme)
        elif state == 12:
            return Token(TokenType.lparen, lexeme)
        elif state == 13:
            return Token(TokenType.rparen, lexeme)
        elif state == 14:
            return Token(TokenType.lbrace, lexeme)
        elif state == 15:
            return Token(TokenType.rbrace, lexeme)
        elif state == 16:
            return Token(TokenType.lbracket, lexeme)
        elif state == 17:
            return Token(TokenType.rbracket, lexeme)
        elif state == 18:
            return Token(TokenType.colon, lexeme)
        elif state == 19:
            return Token(TokenType.comma, lexeme)
        elif state == 20:
            return Token(TokenType.hash, lexeme)
        elif state == 21:
            return Token(TokenType.dot, lexeme)
        elif state == 22:
            return Token(TokenType.whitespace, lexeme)
        elif state == 23:
            return Token(TokenType.newline, lexeme)
        elif state == 25 or state == 28:
            return Token(TokenType.floatliteral, lexeme)

        # Compound operators
        elif state == 29:
            return Token(TokenType.equal_equal, lexeme)
        elif state == 30:
            return Token(TokenType.not_equal, lexeme)
        elif state == 31:
            return Token(TokenType.less_equal, lexeme)
        elif state == 32:
            return Token(TokenType.greater_equal, lexeme)
        
        # Arrow operator
        elif state == 33:
            return Token(TokenType.arrow, lexeme)
        
        elif state == 39:
            return Token(TokenType.colourliteral, lexeme)
        
        # Comments
        elif state == 41:
            return Token(TokenType.linecomment, lexeme)
        elif state == 44:
            return Token(TokenType.blockcomment, lexeme)
        elif state == 46:
            if lexeme in self.underscore_keywords:
                return Token(self.underscore_keywords[lexeme], lexeme)
            else:
                return Token(TokenType.error, lexeme)
    
        else:
            return Token(TokenType.error, lexeme)

    def CatChar(self, character):

        if character in 'ABCDEFabcdef':
            return "hexletter"
        elif character.isalpha():
            return "letter"
        elif character.isdigit():
            return "digit"
        elif character == "_":
            return "underscore" # underscore is treated like an identifier not a symbol in PArl

        # Operators
        elif character == "+":
            return "plus"
        elif character == "-":
            return "minus"
        elif character == "*":
            return "multiply"
        elif character == "/":
            return "slash"        
        elif character == "=":
            return "equals"
        elif character == "<":
            return "less"
        elif character == ">":
            return "greater"
        elif character == "!":
            return "excl"

        # Symbols
        elif character == "(":
            return "lparen"
        elif character == ")":
            return "rparen"
        elif character == "{":
            return "lbrace"
        elif character == "}":
            return "rbrace"
        elif character == "[":
            return "lbracket"
        elif character == "]":
            return "rbracket"
        elif character == ":":
            return "colon"
        elif character == ",":
            return "comma"
        elif character == ";":
            return "semicolon"
        elif character == "#":
            return "hash"
        elif  character == ".":
            return "dot"
        
        # Whitespace and newlines
        elif character in [' ', '\t', '\r']:
            return "whitespace"
        elif character == "\n":
            return "newline"
        else:
            return "other"

    # Checks if the end of the input is reached by comparing the index with the length of the string
    def EndOfInput(self, src_program_str, src_program_idx):
        if (src_program_idx > len(src_program_str)-1):
            return True;
        else:
            return False;

    # Returns the next character in the input string and updates the index
    def NextChar(self, src_program_str, src_program_idx):
        if (not self.EndOfInput(src_program_str, src_program_idx)):
            return True, src_program_str[src_program_idx]
        else: 
            return False, "." # . will be removed in lexeme[:-1]

    # Gets the next token from the input string
    def NextToken(self, src_program_str, src_program_idx):
        state = 0  
        stack = []
        lexeme = ""
        stack.append(-2); # -2 is a marker for the stack to indicate that it is empty 
        
        if self.EndOfInput(src_program_str, src_program_idx):
            return Token(TokenType.end, "end"), "end"

        # -1 when the end of the input is reached or error is encountered
        while (state != -1):
            # Checks if state is an accepting state and clears the stack if it is
            if self.AcceptingStates(state): 
                stack.clear();
            stack.append(state);
            
            # Gets the next character and adds it to the lexeme
            exists, character = self.NextChar(src_program_str, src_program_idx);
            lexeme += character
            if (not exists): 
                if state == 40:
                    character = "\n"
                    exists = True
                else:
                    break  
            # Increments the index to get the next character
            src_program_idx = src_program_idx + 1
            
            # Returns the character label  
            cat = self.CatChar(character);
            state = self.Tx[state][self.lexeme_list.index(cat)];
            
        # Rmoves the last character from the lexeme
        lexeme = lexeme[:-1]

        syntax_error = False;
        
        # Checks for errrs
        while (len(stack) > 0):
            if (stack[-1] == -2): 
                syntax_error = True
                break   
            if (not self.AcceptingStates(stack[-1])):
                stack.pop();
                print("POPPED => ", stack)
                lexeme = lexeme[:-1]
            else:
                state = stack.pop()
                break
        if syntax_error:
            return Token(TokenType.error, "error"), "error"
        if self.AcceptingStates(state):
            return self.GetTokenTypeByFinalState(state, lexeme), lexeme
        else: 
            return Token(TokenType.error, "error"), "error"
        
    # Generates tokens from the input string
    def GenerateTokens(Lexer, src_program_str):
        print("INPUT:: " + src_program_str)
        tokens_list = []
        src_program_idx = 0;
        token, lexeme = Lexer.NextToken(src_program_str, src_program_idx)
        tokens_list.append(token);

        while (token != TokenType.end):  
            src_program_idx = src_program_idx + len(lexeme)    
            token, lexeme = Lexer.NextToken(src_program_str, src_program_idx)
            tokens_list.append(token)
            print ("Nxt TOKEN: ", token.type, " ", lexeme, "(", len(lexeme), ")  => IDX: ", src_program_idx)
            if (token.type == TokenType.error):
                break; 
            if (token.type == TokenType.end):
                break; 
        if (token.type == TokenType.end):
            print("Encountered end of Input token!! Done")
            
        return tokens_list;

    
    # List of keywords in PArl
    keywords = {
        "let": TokenType.kw_let,
        "fun": TokenType.kw_fun,
        "if": TokenType.kw_if,
        "else": TokenType.kw_else,
        "for": TokenType.kw_for,
        "while": TokenType.kw_while,
        "return": TokenType.kw_return,
        "as": TokenType.kw_as,
        "not": TokenType.kw_not,
        "and": TokenType.kw_and,
        "or": TokenType.kw_or,
        "float": TokenType.kw_float,
        "int": TokenType.kw_int,
        "bool": TokenType.kw_bool,
        "colour": TokenType.kw_colour,
    }

    underscore_keywords = {
        "__print": TokenType.kw__print,
        "__delay": TokenType.kw__delay,
        "__write": TokenType.kw__write,
        "__write_box": TokenType.kw__write_box,
        "__random_int": TokenType.kw__random_int,
        "__read": TokenType.kw__read,
        "__width": TokenType.kw__width,
        "__height": TokenType.kw__height,
    }
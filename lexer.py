#Class to wrap the different tokens we'll be using
from enum import Enum

class TokenType(Enum):
    identifier = 1
    integer = 2
    equals = 3
    semicolon = 4
    plus = 5
    minus = 6
    multiply = 7
    slash = 8
    less = 9
    greater = 10
    excl = 11
    lparen = 12
    rparen = 13
    lbrace = 14
    rbrace = 15
    lbracket = 16
    rbracket = 17
    colon = 18
    comma = 19
    hash = 20
    dot = 21
    floatliteral = 22
    booleanliteral = 23
    colourliteral = 24
    kw_let = 25
    kw_fun = 26
    kw_if = 27
    kw_else = 28
    kw_for = 29
    kw_while = 30
    kw_return = 31
    kw_as = 32
    kw_not = 33
    kw_and = 34
    kw_or = 35
    kw_float = 36
    kw_int = 37
    kw_bool = 38
    kw_colour = 39
    kw__print = 40
    kw__delay = 41
    kw__write = 42
    kw__write_box = 43
    kw__random_int = 44
    kw__read = 45
    kw__width = 46
    kw__height = 47
    equal_equal = 48     
    not_equal = 49       
    less_equal = 50      
    greater_equal = 51   
    arrow = 52           
    error = 53
    end = 54
    whitespace = 55
    linecomment = 59
    blockcomment = 60
    newline = 61


class Token:
    def __init__(self, t, l):
        self.type = t
        self.lexeme = l        

#Lexer class wrapper for code above
class Lexer:
    def __init__(self):
        self.lexeme_list = ["letter", "digit", "underscore", "plus", "minus",
                            "multiply", "slash", "equals", "less", "greater", 
                            "excl", "lparen", "rparen", "lbrace", "rbrace",
                            "lbracket", "rbracket", "colon", "comma", "semicolon",
                            "hash", "dot","whitespace","other", "newline",]
        self.states_list = list(range(70))  
        self.states_accp = list(range(1, 24)) + [29, 32, 48, 49, 50, 51, 52, 58, 61, 65]

        self.rows = len(self.states_list)
        self.cols = len(self.lexeme_list)

        
        self.Tx = [[-1 for j in range(self.cols)] for i in range(self.rows)]
        self.InitialiseTxTable();     

    def InitialiseTxTable(self):
        
        self.Tx[0][self.lexeme_list.index("letter")] = 1
        self.Tx[0][self.lexeme_list.index("underscore")] = 1
        self.Tx[1][self.lexeme_list.index("letter")] = 1
        self.Tx[1][self.lexeme_list.index("digit")] = 1
        self.Tx[1][self.lexeme_list.index("underscore")] = 1

        
        self.Tx[0][self.lexeme_list.index("digit")] = 2
        self.Tx[2][self.lexeme_list.index("digit")] = 2

        
        self.Tx[0][self.lexeme_list.index("equals")] = 3
        self.Tx[0][self.lexeme_list.index("semicolon")] = 4
        self.Tx[0][self.lexeme_list.index("plus")] = 5
        self.Tx[0][self.lexeme_list.index("minus")] = 6
        self.Tx[0][self.lexeme_list.index("multiply")] = 7
        self.Tx[0][self.lexeme_list.index("slash")] = 8
        self.Tx[0][self.lexeme_list.index("less")] = 9
        self.Tx[0][self.lexeme_list.index("greater")] = 10
        self.Tx[0][self.lexeme_list.index("excl")] = 11
        self.Tx[0][self.lexeme_list.index("lparen")] = 12
        self.Tx[0][self.lexeme_list.index("rparen")] = 13
        self.Tx[0][self.lexeme_list.index("lbrace")] = 14
        self.Tx[0][self.lexeme_list.index("rbrace")] = 15
        self.Tx[0][self.lexeme_list.index("lbracket")] = 16
        self.Tx[0][self.lexeme_list.index("rbracket")] = 17
        self.Tx[0][self.lexeme_list.index("colon")] = 18
        self.Tx[0][self.lexeme_list.index("comma")] = 19
        self.Tx[0][self.lexeme_list.index("hash")] = 20
        self.Tx[0][self.lexeme_list.index("dot")] = 21

        self.Tx[0][self.lexeme_list.index("whitespace")] = 22
        self.Tx[0][self.lexeme_list.index("newline")] = 23

        self.Tx[8][self.lexeme_list.index("slash")] = 60  

        
        for i, lex in enumerate(self.lexeme_list):
            if lex != "newline":
                self.Tx[60][i] = 60
        self.Tx[60][self.lexeme_list.index("newline")] = 61  

        self.Tx[8][self.lexeme_list.index("multiply")] = 63  
        
        for i, lex in enumerate(self.lexeme_list):
            if lex != "multiply":
                self.Tx[63][i] = 63
        self.Tx[63][self.lexeme_list.index("multiply")] = 64
        self.Tx[64][self.lexeme_list.index("slash")] = 65  

        # Floats
        self.Tx[2][self.lexeme_list.index("dot")] = 28     
        self.Tx[28][self.lexeme_list.index("digit")] = 29  
        self.Tx[29][self.lexeme_list.index("digit")] = 29  
        self.Tx[29][self.lexeme_list.index("letter")] = 30 
        self.Tx[30][self.lexeme_list.index("plus")] = 31   
        self.Tx[30][self.lexeme_list.index("minus")] = 31  
        self.Tx[30][self.lexeme_list.index("digit")] = 32 
        self.Tx[31][self.lexeme_list.index("digit")] = 32  
        self.Tx[32][self.lexeme_list.index("digit")] = 32 
        self.Tx[32][self.lexeme_list.index("letter")] = 32  

        # Compound operators 
        self.Tx[3][self.lexeme_list.index("equals")] = 48  
        self.Tx[11][self.lexeme_list.index("equals")] = 49 
        self.Tx[9][self.lexeme_list.index("equals")] = 50  
        self.Tx[10][self.lexeme_list.index("equals")] = 51 
        
        # Arrow operator 
        self.Tx[6][self.lexeme_list.index("greater")] = 52  

        # After #
        self.Tx[20][self.lexeme_list.index("digit")] = 53
        self.Tx[20][self.lexeme_list.index("letter")] = 53

        self.Tx[53][self.lexeme_list.index("digit")] = 54
        self.Tx[53][self.lexeme_list.index("letter")] = 54

        self.Tx[54][self.lexeme_list.index("digit")] = 55
        self.Tx[54][self.lexeme_list.index("letter")] = 55

        self.Tx[55][self.lexeme_list.index("digit")] = 56
        self.Tx[55][self.lexeme_list.index("letter")] = 56

        self.Tx[56][self.lexeme_list.index("digit")] = 57
        self.Tx[56][self.lexeme_list.index("letter")] = 57

        self.Tx[57][self.lexeme_list.index("digit")] = 58
        self.Tx[57][self.lexeme_list.index("letter")] = 58

        

        for row in self.Tx:
            print(row)

    def AcceptingStates(self, state):
        try:
            self.states_accp.index(state)
            return True;
        except ValueError:
            return False;

    def GetTokenTypeByFinalState(self, state, lexeme):
        if state == 1:
            if lexeme in self.keywords:
                return Token(self.keywords[lexeme], lexeme)
            elif lexeme in ["true", "false"]:
                return Token(TokenType.booleanliteral, lexeme)
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
        elif state == 29 or state == 32 or state == 33:
            return Token(TokenType.floatliteral, lexeme)

        # Compound operators
        elif state == 48:
            return Token(TokenType.equal_equal, lexeme)
        elif state == 49:
            return Token(TokenType.not_equal, lexeme)
        elif state == 50:
            return Token(TokenType.less_equal, lexeme)
        elif state == 51:
            return Token(TokenType.greater_equal, lexeme)
        
        # Arrow operator
        elif state == 52:
            return Token(TokenType.arrow, lexeme)
        
        elif state == 58:
            return Token(TokenType.colourliteral, lexeme)
        elif state == 61:
            return Token(TokenType.linecomment, lexeme)
        elif state == 65:
            return Token(TokenType.blockcomment, lexeme)
    
        else:
            return Token(TokenType.error, lexeme)

    def CatChar(self, character):

        if character.isalpha():
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
        elif character in [' ', '\t', '\r']:
            return "whitespace"
        elif character == "\n":
            return "newline"
        else:
            return "other"

    def EndOfInput(self, src_program_str, src_program_idx):
        if (src_program_idx > len(src_program_str)-1):
            return True;
        else:
            return False;

    def NextChar(self, src_program_str, src_program_idx):
        if (not self.EndOfInput(src_program_str, src_program_idx)):
            return True, src_program_str[src_program_idx]
        else: 
            return False, "."

    def NextToken(self, src_program_str, src_program_idx):
        state = 0  
        stack = []
        lexeme = ""
        stack.append(-2);  
        
        if self.EndOfInput(src_program_str, src_program_idx):
            return Token(TokenType.end, "end"), "end"

        while (state != -1):
            if self.AcceptingStates(state): 
                stack.clear();
            stack.append(state);
            
            exists, character = self.NextChar(src_program_str, src_program_idx);
            lexeme += character
            if (not exists): 
                 
                break  
            src_program_idx = src_program_idx + 1
            
            cat = self.CatChar(character);
            state = self.Tx[state][self.lexeme_list.index(cat)];
            
        
        lexeme = lexeme[:-1]

        syntax_error = False;
        
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


    def GenerateTokens(self, src_program_str):
        print("INPUT:: " + src_program_str)
        tokens_list = []
        src_program_idx = 0;
        token, lexeme = self.NextToken(src_program_str, src_program_idx)
        tokens_list.append(token);

        while (token != TokenType.end):  
            src_program_idx = src_program_idx + len(lexeme)    
            token, lexeme = self.NextToken(src_program_str, src_program_idx)
            tokens_list.append(token)
            print ("Nxt TOKEN: ", token.type, " ", lexeme, "(", len(lexeme), ")  => IDX: ", src_program_idx)
            if (token.type == TokenType.error):
                break; 
            if (token.type == TokenType.end):
                break; 
        if (token.type == TokenType.end):
            print("Encountered end of Input token!! Done")
        
        return tokens_list;
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
        "__print": TokenType.kw__print,
        "__delay": TokenType.kw__delay,
        "__write": TokenType.kw__write,
        "__write_box": TokenType.kw__write_box,
        "__random_int": TokenType.kw__random_int,
        "__read": TokenType.kw__read,
        "__width": TokenType.kw__width,
        "__height": TokenType.kw__height
    }

lex = Lexer()
toks = lex.GenerateTokens("3.532 +, 3.14 * 2.5; let x = 3; let y = 4; let z = x + y; if (x < y) { z = x + y; } else { z = x - y; } # This is a comment\n") 

for t in toks:
    print(t.type, t.lexeme)
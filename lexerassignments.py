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
    error = 22
    end = 23


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
                            "hash", "dot","other"]
        self.states_list = list(range(22))
        self.states_accp = list(range(1, 22))   

        self.rows = len(self.states_list)
        self.cols = len(self.lexeme_list)

        # Let's take integer -1 to represent the error state for this DFA
        self.Tx = [[-1 for j in range(self.cols)] for i in range(self.rows)]
        self.InitialiseTxTable();     

    def InitialiseTxTable(self):
        # Identifiers: start with letter or underscore, followed by letters/digits
        self.Tx[0][self.lexeme_list.index("letter")] = 1
        self.Tx[0][self.lexeme_list.index("underscore")] = 1
        self.Tx[1][self.lexeme_list.index("letter")] = 1
        self.Tx[1][self.lexeme_list.index("digit")] = 1
        self.Tx[1][self.lexeme_list.index("underscore")] = 1

        # Integers: sequence of digits
        self.Tx[0][self.lexeme_list.index("digit")] = 2
        self.Tx[2][self.lexeme_list.index("digit")] = 2

        # Single-character operators & symbols (direct transitions to unique states)
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
        else:
            return "other"

    def EndOfInput(self, src_program_str, src_program_idx):
        if (src_program_idx > len(src_program_str)-1):
            return True;
        else:
            return False;

    def SkipWhitespace(self, src_program_str, src_program_idx):
        while src_program_idx < len(src_program_str) and src_program_str[src_program_idx] in [' ', '\t', '\n', '\r']:
            src_program_idx += 1
        return src_program_idx

    def NextChar(self, src_program_str, src_program_idx):
        if (not self.EndOfInput(src_program_str, src_program_idx)):
            return True, src_program_str[src_program_idx]
        else: 
            return False, "."

    def NextToken(self, src_program_str, src_program_idx):
        state = 0  #initial state is 0 - check Tx
        stack = []
        lexeme = ""
        stack.append(-2);  #insert the error state at the bottom of the stack.

        src_program_idx = self.SkipWhitespace(src_program_str, src_program_idx) #skip whitespace

        #if at end of input return the end token
        if self.EndOfInput(src_program_str, src_program_idx):
            return Token(TokenType.end, "end"), "end"

        while (state != -1):
            if self.AcceptingStates(state): 
                stack.clear();
            stack.append(state);
            
            exists, character = self.NextChar(src_program_str, src_program_idx);
            lexeme += character
            if (not exists): 
                #print("LAST LEXEME: ", lexeme); 
                break  #Break out of loop if we're at the end of the string
            src_program_idx = src_program_idx + 1
            
            cat = self.CatChar(character);
            state = self.Tx[state][self.lexeme_list.index(cat)];
            #print("Lexeme: ", lexeme, " => NEXT STATE: ", state, "  => CAT: ", cat, "  => CHAR:", character, "  => STACK: ", stack)
        
        lexeme = lexeme[:-1] #remove the last character added which sent the lexer to state -1    

        syntax_error = False;
        #rollback
        while (len(stack) > 0):
            if (stack[-1] == -2): #report a syntax error
                syntax_error = True
                break    

            #Pop this state if not an accepting state.
            if (not self.AcceptingStates(stack[-1])):
                stack.pop();
                print("POPPED => ", stack)
                lexeme = lexeme[:-1]
            
            #This is an accepting state ... return it.    
            else:
                state = stack.pop()
                break
        
        #print("Lexeme: ", lexeme, "with state: ", state)

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

        while (token != TokenType.end):  #this loop is simulating the Parser asking for the next token
            src_program_idx = src_program_idx + len(lexeme)    
            token, lexeme = self.NextToken(src_program_str, src_program_idx)
            tokens_list.append(token);
            print ("Nxt TOKEN: ", token.type, " ", lexeme, "(", len(lexeme), ")  => IDX: ", src_program_idx)
            if (token.type == TokenType.error):
                break; #A Lexical error was encountered
            
            if (token.type == TokenType.end):
                break; #We're done ... no more src input

        if (token.type == TokenType.end):
            print("Encountered end of Input token!! Done")
        
        return tokens_list;

lex = Lexer()
toks = lex.GenerateTokens("x=5+3-2*4/2<10>1!=0;(arr[2]){key:value,next:item#123.456;}")

for t in toks:
    print(t.type, t.lexeme)
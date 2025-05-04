from lexer import Lexer, TokenType

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

if __name__ == "__main__":
    test_code = """let x = 5 // this is a line comment
let y = 10 /* this is a
* multi-line
block comment */ let z = 15"""

    lex = Lexer()
    tokens = GenerateTokens(lex, test_code)

    for t in tokens:
        print(t.type, t.lexeme)
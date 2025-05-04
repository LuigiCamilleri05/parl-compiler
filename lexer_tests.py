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
    test_inputs = [
    "let x = 10;",
    "fun doStuff() { return x; }",
    "if true and false or not x",
    "colour red = #FF00FF;",
    "x == y",
    "x != y",
    "x <= y",
    "x >= y",
    "x -> y",
    "{ [ ( ) ] }",
    """let x = 5 // line comment
        let y """,
    "let y = 10 /* block comment */ let z = 15",
    "/* block /* nested */ still block */",
    "c = #FFAA00",
    "x = @;",
    "123abc",
    "#1234"
    "let fun if else for while return as not and or float int bool colour __print __delay __write __write_box __random_int __read __width __height"
]

    lexer = Lexer()

    for i, code in enumerate(test_inputs):
        print(f"\n--- Test {i+1} ---")
        tokens = GenerateTokens(lexer, code)
        for t in tokens:
            print(t.type, t.lexeme)
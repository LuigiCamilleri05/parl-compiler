from lexer import Lexer, TokenType

if __name__ == "__main__":
    test_inputs = [
    "let x = 10;",                      # Simple variable declaration with integer and semicolon
    "int",                              # Keyword recognition (type)
    "_let a d",                         # Underscore + identifiers (illegal vs legal identifiers)
    "__clear",                          # Double underscore keyword (custom system function)

    "x == y",                           # Compound operator: equal_equal
    "x != y",                           # Compound operator: not_equal
    "x <= y",                           # Compound operator: less_equal
    "x >= y",                           # Compound operator: greater_equal
    "x -> y",                           # Compound operator: arrow

    "{ [ ( ) ] }",                      # All grouping symbols

    "fun doStuff() { return x; }",      # Function declaration syntax and multiple token types
    "if true and false or not x",       # Boolean literals and logic operators

    # Colour literal (starts with `#` and has 6 hex digits)
    "colour red = #FF00FF;",            

    # Inline block comment handling
    "let y = 10 /* block comment */ let z = 15",  

    # Line comment ending with newline
    """let x = 5 // line comment
        let y """,                      

    # Nested block comments
    "/* block /* nested */ still block */",  

    # Colour literal edge case
    "c = #FFAA00",                      

    # Unknown character (@) => should trigger error
    "x = @;",                           

    # Invalid identifier after number => should tokenize `123` then error 
    "123abc",                           

    # Invalid colour literal (too short => error expected)
    "#1234",  

    "let fun if else for while return as not and or float int bool colour __print __delay __write __write_box __random_int __read __width __height"
    # Full keyword coverage (reserved & underscore keywords)
    ]

    lexer = Lexer()

    # Loops through each test input
    for i, code in enumerate(test_inputs):
        print(f"\n--- Test {i+1} ---")
        tokens = lexer.GenerateTokens(code)
        # Shows output of rows in lexer.Tx
        for row in lexer.Tx:
            print(row)

        # Shows output of tokens in input string
        for t in tokens:
            print(t.type, t.lexeme)
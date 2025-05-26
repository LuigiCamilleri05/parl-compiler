from lexer import Lexer

if __name__ == "__main__":
    test_inputs = [
    "let x = 10;",                      # Simple variable declaration with integer and semicolon
    "int",                              # Keyword recognition (type)
    "_let a d",                         # Underscore + identifiers (illegal vs legal identifiers)
    "2.5",
    
    "x == y",                           # Compound operator: equal_equal
    "x != y",                           # Compound operator: not_equal
    "x <= y",                           # Compound operator: less_equal
    "x >= y",                           # Compound operator: greater_equal
    "x -> y",                           # Compound operator: arrow

    "{ [ ( ) ] }",                      # All grouping symbols

    "if true and false or not",       # Boolean literals and logic operators

    # Colour literal (starts with `#` and has 6 hex digits)
    "colour red = #FF00FF;",            

    # Inline block comment handling
    "let y = 10 /* block comment */ let z = 15",  

    # Line comment ending with newline
    """let x = 5 // line comment
        let y """,                                       

    # Unknown character (@) => should trigger error
    "x = @;",                           

    # Invalid identifier after number => should tokenize `123` then error 
    "123abc",                           

    # Invalid colour literal (too short => error expected)
    "#1234",  

    "fun else for while return as float bool __print __delay __write __write_box __random_int __read __width __height __clear"
    # Full keyword coverage (reserved & underscore keywords)
    ]

    lexer = Lexer()

    # Loops through each test input
    for i, code in enumerate(test_inputs):
        print(f"\n--- Test {i+1} ---")
        tokens = lexer.GenerateTokens(code)
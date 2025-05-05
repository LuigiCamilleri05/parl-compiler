from lexer import Lexer, TokenType

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
    "#1234",
    "let fun if else for while return as not and or float int bool colour __print __delay __write __write_box __random_int __read __width __height",
    "_let a d"
]

    lexer = Lexer()

    for i, code in enumerate(test_inputs):
        print(f"\n--- Test {i+1} ---")
        tokens = lexer.GenerateTokens(code)
        for t in tokens:
            print(t.type, t.lexeme)
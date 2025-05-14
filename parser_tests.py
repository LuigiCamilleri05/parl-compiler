from parser import Parser
from astnodes import PrintNodesVisitor

test_inputs = [
    # Simple variable declaration
    "let x : int = 5;",

    # Variable declaration and if statement
    """
    let x : int = 5;
    if (x < 10) {
        __print x;
    } else {
        __print 0;
    }
    """,

    # While loop
    """
    let x : int = 0;
    while (x < 5) {
        __print x;
        x = x + 1;
    }
    """,

    # For loop with full header
    """
    for (let i : int = 0; i < 10; i = i + 1) {
        __print i;
    }
    """,

    # Function declaration
    """
    fun add(a : int, b : int) -> int {
        return a + b;
    }
    """,

    # Incorrect syntax (missing semicolon)
    "let x : int = 5",

    # Nested blocks
    """
    {
        let x : int = 3;
        {
            let y : int = x + 2;
            __print y;
        }
    }
    """,

    """
    __clear 5;
    """,
    """
    fun sum(arr:int[8]) -> int {
    return arr[0] + arr[1];
    }
    """
]

if __name__ == "__main__":
    for i, code in enumerate(test_inputs):
        print(f"\n--- Test {i + 1} ---")
        try:
            parser = Parser(code)
            parser.Parse()
            visitor = PrintNodesVisitor()
            parser.ASTroot.accept(visitor)
        except Exception as e:
            print(f"Syntax Error: {e}")

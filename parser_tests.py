from parser import Parser
from astnodes import PrintNodesVisitor

test_inputs = [
    # Simple variable declaration with integer
    "let x : int = 5;",

    # Float declaration
    "let pi : float = 3.14;",

    # Boolean literal usage
    "let b : bool = true;",

    # Colour literal
    "let c : colour = #FFAACC;",

    # Unary minus
    "let x : int = -5;",

    # Unary not
    "let b : bool = not false;",

    # Simple arithmetic with precedence
    "let y : int = 3 + 4 * 2;",

    # Arithmetic with type casting
    "let z : float = (5 + 3) as float;",

    # Array declaration with fixed size and one value
    "let arr : int[3] = [1];",

    # Array declaration with inferred size
    "let arr : int[] = [1, 2, 3];",

    # PadWidth and PadHeight usage
    "let w : int = __width;",
    "let h : int = __height;",

    # __read pad function
    "let input : int = __read 2, 3;",

    # __random_int function
    "let rand : int = __random_int 10;",

    # Assignment after declaration
    """
    let x : int = 0;
    x = 5;
    """,

    # Simple block with declaration inside
    "{ let x : int = 2; }",

    # If statement
    """
    if (true) {
        __print 1;
    }
    """,

    # If-else block
    """
    if (false) {
        __print 0;
    } else {
        __print 1;
    }
    """,

    # While loop with update
    """
    let x : int = 0;
    while (x < 3) {
        x = x + 1;
    }
    """,

    # For loop with full components
    """
    for (let i : int = 0; i < 5; i = i + 1) {
        __print i;
    }
    """,

    # Function declaration with return
    """
    fun add(a : int, b : int) -> int {
        return a + b;
    }
    """,

    # Function declaration with array parameter
    """
    fun sum(arr : int[3]) -> int {
        return arr[0] + arr[1];
    }
    """,

    # Function call
    """
    let result : int = add(1, 2);
    """,

    # Function with return inside nested block
    """
    fun value() -> int {
        {
            let x : int = 2;
            return x;
        }
    }
    """,

    # Multiple statements inside a block
    """
    {
        let a : int = 1;
        a = a + 2;
        __print a;
    }
    """,

    # __write statement
    "__write 10, 20, #FF00FF;",

    # __write_box statement
    "__write_box 0, 0, 5, 5, #000000;",

    # __clear with expression
    "__clear 5;",

    # return statement
    "return 42;",

    # Nested blocks
    """
    {
        let x : int = 1;
        {
            let y : int = x + 1;
            __print y;
        }
    }
    """,

    # Edge case: missing semicolon
    "let x : int = 5",

    # Edge case: invalid token
    "let x : int = @;",

    # Function with no parameters
    """
    fun nop() -> int {
        return 1;
    }
    """,

    # A variable cast to another type
    """
    let x : int = 5;
    let y : float = x as float;
    """,

    # A function declaration missing the '->' and return type 
    """
    fun brokenFunc(a : int) {
        return a;
    }
    """,

    # An empty block 
    """
    {
    }
    """,

    # A function with a array returned with literal values (Error expected)
    """
    fun getNums() -> int[3] {
        return [1, 2, 3];
    }
    """,

    # A nested function call
    """
    fun double(a : int) -> int {
        return a + a;
    }
    let result : int = double(1 + 2);
    """,

    # A cast in an arithmetic expression (Error expected)
    """
    let a : float = (5 + 3) as float * 2.0;
    """,

    # Multiple unary operators chained
    """
    let val : int = - -5;
    """,

    # A variable with an identifier that resembles a keyword
    """
    let notnot : bool = true;
    """,
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

from parser import Parser
from code_generator import CodeGenerator

test_inputs = [
    "let x : int = 5;", # Basic test
    "let y : float = 3.14;", # Test float declaration
    "let b : bool = true;", # Test boolean declaration
    """let c : colour = #00ff00; 
       let x : int = 5;""", # Test colour declaration and multiple lines
    "let x : int = 5; x = x + 1;", # Test assignment and addition
    "let x : int = 5; x = x - 1;", # Test subtraction
    "let x : int = 5; x = x * 2;", # Test multiplication
    "let x : int = 5; x = x / 2;", # Test division
    "let x : bool = 3 < 5;", # Test <
    "let x : bool = 3 > 5;", # Test >
    "let x : bool = 3 <= 5;", # Test <=
    "let x : bool = 3 >= 5;", # Test >=
    "let x : bool = 3 == 5;", # Test ==
    "let x : bool = 3 != 5;", # Test !=
    "let x : bool = true and false;", # Test and
    "let x : bool = true or false;", # Test or
    "__delay 1000;", # Test delay
    "let x : int = 5; __delay x;", # Test delay with variable
    "__clear #00ff00;", # Test clear
    "let x : colour = #00ff00; __clear x;", # Test clear with variable
    """
        // Test __write with literals
        __write 5, 10, #ff0000;

        // Test __write with variables
        let x : int = 5;
        let y : int = 10;
        let c : colour = #ff0000;
        __write x, y, c;
    """,
    """
        // Test __write_box with literals
        __write_box 0, 0, 2, 2, #0000ff;

        // Test __write_box with variables
        let x : int = 0;
        let y : int = 0;
        let w : int = 2;
        let h : int = 2;
        let c : colour = #0000ff;
        __write_box x, y, w, h, c;
    """,
    """
        // Test __print with a literal
        __print 42;

        // Test __print with a variable
        let x : int = 42;
        __print x;
    """,
    """
        // Test __width and __height
        let w : int = __width;
        let h : int = __height;
        __print w;
        __print h;
    """,
    """
    let c : int = __random_int 10;
    """,

     # Simple read using literals
    "__read 0, 0;",

    # Using variables for coordinates
    "let x : int = 5; let y : int = 10; __read x, y;",

    # Read with expression
    "__read 2+3, 7-4;",

    # Full assignment
    "let c : colour = __read 4, 5;"
    "__print not true;",         # Should print 0
    "__print not false;",        # Should print 1
    "let a: bool = true; __print not a;"
    "__print -42;",              # Should print -42
    "let x: int = 5; __print -x;"  # Should print -5

    # Negate floats
    "__print -3.14;",
    "let y: float = 2.5; __print -y;",

    # Test Block Scope
    """
    {
    let x : int = 1;
    let y : float = 2.5;
    let z : bool = true;
    }
    """,
    # Test emplty block
    """
    {
    }
    """,
    # Test nested blocks
    """
    {
        let x : int = 1;
        {
            let y : float = 2.5;
            {
                let z : bool = true;
            }
        }
    }
    """,


]


for i, program in enumerate(test_inputs):
    print(f"\n=== Test {i+1} ===")

    try:
        parser = Parser(program)
        parser.Parse()

        codegen = CodeGenerator()
        parser.ASTroot.accept(codegen)

        print("Generated PArIR Code:")
        for instr in codegen.instructions:
            print(instr)

    except Exception as e:
        print(f"Error during parsing/codegen: {e}")


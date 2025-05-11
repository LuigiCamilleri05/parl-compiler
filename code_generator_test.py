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


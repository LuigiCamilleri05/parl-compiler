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


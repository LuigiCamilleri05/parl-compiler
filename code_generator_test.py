from parser import Parser
from code_generator import CodeGenerator

test_inputs = [
    "let x : int = 5;",
    "let y : float = 3.14;",
    "let b : bool = true;",
    """let c : colour = #00ff00;
       let x : int = 5;""",
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


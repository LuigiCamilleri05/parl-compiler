from parser import Parser
from semantic_analyzer import SemanticAnalyzer  # Make sure this is your visitor class name

test_programs = [
    # Valid program
    """
    let x : int = 5;
    let y : int = x + 10;
    """,

    # Redeclaration in same scope
    """
    let x : int = 5;
    let x : int = 6;
    """,

    # Use before declaration
    """
    let y : int = x + 1;
    let x : int = 5;
    """,

    # Type mismatch
    """
    let x : int = true;
    """,

    # Valid function
    """
    fun addOne(n: int) -> int {
        return n + 1;
    }
    let x : int = addOne(5);
    """,

    # Function returns wrong type
    """
    fun wrong() -> int {
        return true;
    }
    """,

    """
    let x : int = 0;
    while (x < 10) {
        x = x + 1;
    }
    """,
]

for i, code in enumerate(test_programs):
    print(f"\n--- Test Case {i + 1} ---")
    try:
        parser = Parser(code)
        parser.Parse()
        analyzer = SemanticAnalyzer()
        parser.ASTroot.accept(analyzer)
        print("✅ Semantic check passed.")
    except Exception as e:
        print(f"❌ Semantic error: {e}")

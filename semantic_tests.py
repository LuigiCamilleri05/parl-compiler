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

    """
    for (let i : int = 0; i < 10; i = i + 1) {
        i = i + 1;
    }
    """,

    """
    let flag : bool = true;
    let i : int = 0;
    if (flag) {
        i = 1;
    } else {
        i = 0;
    }
    """,

    # Logical NOT on a boolean
    """
    let x : bool = true;
    let y : bool = not x;
    """,

    # Unary minus on an integer
    """
    let x : int = 5;
    let y : int = -x;
    """,

    # Unary minus on a float
    """
    let x : float = 3.14;
    let y : float = -x;
    """,

    # NOT on an int — should fail
    """
    let x : int = 5;
    let y : bool = not x;
    """,

    # Unary minus on a boolean — should fail
    """
    let x : bool = true;
    let y : int = -x;
    """

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

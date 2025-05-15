from parser import Parser
from semantic_analyzer import SemanticAnalyzer  # Make sure this is your visitor class name

test_programs = [
    
    """
    fun sum(arr:int[8]) -> int {
    return arr[0] + arr[1];
    }
    """,
    """
    fun MaxInArray(x:int[8]) -> int {
            let m:int = 0;
            for (let i:int = 0; i < 8; i = i + 1) {
                if (x[i] > m) {
                    m = x[i];
                }
            }
            return m;
        }

        let list_of_integers:int[] = [23, 54, 3, 65, 99, 120, 34, 21];
        let max:int = MaxInArray(list_of_integers);
        __print max;
    """,
    """
    fun draw_pattern(offset:int) -> bool {
        let colors:colour[] = [#FF0000, #FF7F00, #FFFF00, #00FF00, #0000FF, #4B0082, #9400D3]; // Rainbow colors

        for (let x:int = 0; x < __width; x = x + 3) {
            for (let y:int = 0; y < __height; y = y + 3) {                        
                let colorIndex:int = (x + y + offset) / 7;
                __write_box x, y, 2, 2, colors[colorIndex];
            }
        }

        return true;
    }

    let offset:int = 0;
    let r:bool = false;

    while (true) {
        r = draw_pattern(offset);
        offset = offset + 1;
        __delay 10; // Delay to make the movement visible
    }
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

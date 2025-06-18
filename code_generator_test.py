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
    "let c : int = __random_int 10;",

    # Full assignment
    "let c : colour = __read 4, 5;",
    "__print not true;",         # Should print 0
    "__print not false;",        # Should print 1
    "let a: bool = true; __print not a;",
    "__print -42;",              # Should print -42
    "let x: int = 5; __print -x;",  # Should print -5

    # Negate floats
    "__print -3.14;",
    "let y: float = 2.5; __print -y;",
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

    # Test Block Scope
    """
    {
    let x : int = 1;
    let y : float = 2.5;
    let z : bool = true;
    }
    """,
    # Test empty block
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
    # Basic cast checks
    """
    // Cast int to float
    let x : float = 5 as float;

    // Cast float to int
    let y : int = 3.14 as int;

    // Cast int to colour
    let c : colour = 255 as colour;
    """,
    # Basic if-else checks
    """ 
    let x:int = 5;
    let y:int = 10;

    if (x < y) {
        __print x;
    } else {
        __print y;
    }

    if (x < 0) {   
       __print x;
    }
    """,
    # Nested if-else checks
    """
    let a:int = 1;
    let b:int = 2;

    if (a < b) {
        if (b < 10) {
            __print b;
        } else {
            __print a;
        }
    }
    """,
    # Normal while loop
    """
    let i:int = 0;
    while (i < 3) {
        i = i + 1;
    }
    """,
    # Loop with nested block
    """
    let i:int = 0;

    while (i < 2) {
        {
            __print i;
        }
        i = i + 1;
    }
    """,
    """
    let i:int = 0;
    let limit:int = 5;

    while (i < limit) {
        __print i;
        i = i + 1;
    }
    """,
    # Infinite loop
    """ 
    let flag:bool = true;

    while (flag) {
        __print 1;
        flag = false;
    }
    """,
    # Empty Block
    """
    let x:int = 2;

    while (x < 1) {
    }
    """,
    # Basic for loop
    """
    for (let i:int = 0; i < 3; i = i + 1) {
        __print i;
    }
    """,
    # Empty for loop
    """ 
    for (let i:int = 0; i < 2; i = i + 1) {
    }
    """,
    # For loop with nested block
    """
    for (let i:int = 0; i < 2; i = i + 1) {
        {
        __print i;
        }
    }
    """,
    # For loop decrementing
    """
    for (let i:int = 5; i > 0; i = i - 1) {
        {
        __print i;
        }
    }
    """,
    # Example in the assignment
    """
    let c:colour = 0 as colour;

    for (let i:int = 0; i < 64; i = i + 1) {
    c = (__random_int 1677216) as colour;
    __clear c;

    __delay 16;
    }
    """,
    # For loop with nested for loop
    """
    for (let i:int = 0; i < 2; i = i + 1) {
        for (let j:int = 0; j < 3; j = j + 1) {
            __print i;
            __print j;
        }
    }
    """,
    # For loop in while loop
    """
    let i:int = 0;
        while (i < 2) {
            for (let j:int = 0; j < 2; j = j + 1) {
                __print i;
                __print j;
            }
            i = i + 1;
        }
    """,
    # For loop with nested while loop
    """
    for (let i:int = 0; i < 2; i = i + 1) {
        let j:int = 0;
        while (j < 2) {
            __print i;
            __print j;
            j = j + 1;
        }
    }
    """,
    # For loop in if statement
    """
    let x:int = 1;
    if (x < 2) {
        for (let i:int = 0; i < 2; i = i + 1) {
            __print i;
        }
    }
    """,
    # While loop in if statement    
    """
    let x:int = 0;
    if (x == 0) {
        let i:int = 0;
        while (i < 2) {
            __print i;
            i = i + 1;
        }
    }
    """,
    # Function with one parameter
    """
    fun square(n:int) -> int {
        return n * n;
    }

    let val:int = square(4);
    __print val;
    """,
    # Function with if statement
    """
    fun max(a:int, b:int) -> int {
        if (a > b) {
            return a;
        } else {
            return b;
        }
    }

    let biggest:int = max(10, 20);
    __print biggest;
    """,
    # Nested functions
    """
    fun add(a:int, b:int) -> int {
        return a + b;
    }

    fun mul(x:int, y:int) -> int {
        return x * y;
    }

    let result:int = mul(add(2, 3), 4);  // (2+3)*4 = 20
    __print result;
    """,
    # Function called in while loop
    """
    fun IsEven(n:int) -> bool {
        return n/2 == 1;
    }

    let x:int = 2;

    while (IsEven(x)) {
    __print x;
    x = x + 1;
    }
    """,
    # Function call in for loop
    """
    fun IsEven(n:int) -> bool {
        return (n /2) == 1;
    }

    // Loop while x is even, using a function as the condition
    for (let x:int = 2; IsEven(x); x = x +1) {
        __print x;
        x = x + 1;
    }
    """,
    # Last test not array
    """
    fun XGreaterY(x:int, y:int) -> bool {
    let ans:bool = true;
    if (y > x) { ans = false; }
    return ans;
    }

    fun XGreaterY_2(x:int, y:int) -> bool {
    return x > y;
    }

    fun AverageOfTwo(x:int, y:int) -> float {
    let t0:int = x + y;
    let t1:float = t0 / 2 as float;
    return t1;
    }

    fun AverageOfTwo_2(x:int, y:int) -> float {
    return (x + y) / 2 as float;
    }

    fun Max(x:int, y:int) -> int {
    let m:int = x;
    if (y > m) { m = y; }
    return m;
    }

    __write 10, 14, #00ff00;
    __delay 100;
    __write_box 10, 14, 2, 2, #0000ff;

    for (let i:int = 0; i < 10; i = i + 1) {
    __print i;
    __delay 1000;
    }

    fun Race(p1_c:colour, p2_c:colour, score_max:int) -> int {
        let p1_score:int = 0;
        let p2_score:int = 0;

    while ((p1_score < score_max) and (p2_score < score_max)) {
        let p1_toss:int = __random_int 1000;
        let p2_toss:int = __random_int 1000;

    if (p1_toss > p2_toss) {
        p1_score = p1_score + 1;
    __write 1, p1_score, p1_c;
    } else {
        p2_score = p2_score + 1;
        __write 2, p2_score, p2_c;
    }

    __delay 100;
    }

    if (p2_score > p1_score) {
        return 2;
    }

        return 1;
    }

    let c1:colour = #00ff00;
    let c2:colour = #0000ff;
    let m:int = __height;
    let w:int = Race(c1, c2, m);
    __print w;
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


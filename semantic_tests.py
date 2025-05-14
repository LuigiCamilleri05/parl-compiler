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
    """,

    # __print with valid int expression
    """
    let x : int = 5;
    __print x;
    """,

    # __delay with valid int expression
    """
    let delayMs : int = 1000;
    __delay delayMs;
    """,

    # __clear with valid colour expression
    """
    let c : colour = #FF00FF;
    __clear c;
    """,
    # __clear with invalid type (e.g., int) 
    """
    let x : int = 5;
    __clear x;
    """,

    # __write with correct argument types (int, int, colour)
    """
    let x : int = 10;
    let y : int = 20;
    __write x, y, #FF00FF;
    """,

    # ❌ __write with incorrect type (e.g., colour used as x)
    """
    let c : colour = #FF00FF;
    __write c, 20, #00FF00;
    """,

    # __write_box with correct argument types
    """
    let x : int = 0;
    let y : int = 0;
    let w : int = 1;
    let h : int = 1;
    __write_box x, y, w, h, #00FF00;
    """,

    # ❌ __write_box with incorrect value type
    """
    let x : int = 0;
    let y : int = 0;
    let w : int = 1;
    let h : int = 1;
    __write_box x, y, w, h, 42;
    """,
     # Valid return type
    """
    fun getVal() -> int {
        return 5;
    }
    """,

    # Return type mismatch
    """
    fun getBool() -> bool {
        return 42;
    }
    """,

    # Missing return (should pass unless return required to be explicit in every path)
    """
    fun missingReturn() -> int {
        if (true) {
            return 1;
        }
    }
    """,

    # Missing return in non-void function (should fail)
    """
    fun test(n: int) -> int {
        if (n < 10) {
            return n;
        }
        // No return here!
    }
    """,

    # Return outside of function
    """
    return 5;
    """,

    # Valid cast from int to float
    """
    let x : int = 5;
    let y : float = x as float;
    """,

    # Valid cast from float to int
    """
    let x : float = 3.14;
    let y : int = x as int;
    """,

    # Valid cast from bool to int
    """
    let x : bool = true;
    let y : int = x as int;
    """,

    # Valid cast from int to colour
    """
    let x : int = 255;
    let y : colour = x as colour;
    """,

    # Invalid cast to unknown type
    """
    let x : int = 1;
    let y : foo = x as foo;
    """,

    # Invalid cast from colour to bool
    """
    let c : colour = #00FF00;
    let x : bool = c as bool;
    """,
        # __width and __height used as int values
    """
    let w : int = __width;
    let h : int = __height;
    """,

    # __read with correct argument types
    """
    let x : int = 10;
    let y : int = 20;
    let c : colour = __read x, y;
    """,

    # __read with incorrect argument type
    """
    let f : float = 3.14;
    let c : colour = __read f, 2;
    """,

    # __random_int with valid int argument
    """
    let upper : int = 100;
    let rand : int = __random_int(upper);
    """,

    # __random_int with invalid (e.g., bool) argument
    """
    let b : bool = true;
    let rand : int = __random_int(b);
    """,
    # Function with nested function should fail
    """
    let x : int = 5;
    if (x < 10) {
        fun notAllowed() -> int {
            return 42;
        }
    }
    """,
    """
    let x : int = 5;
    if (x < 10) {
        let x : int = 10;
    }
    """,
    """
    fun MoreThan50 ( x : int ) -> bool {
        let x : int = 23; // syntax ok , but this should not be allowed !!
        if ( x <= 50 ) {
            return false;
        }
        return true;
        }

        let x : int = 45; // this is fine
    while (x < 50) {
        __print MoreThan50(x); // “false” x6 since bool operator is <
        x = x + 1;
    }

    let x : int = 45; // re-declaration in the same scope... not allowed!!
    while (MoreThan50(x)) {
        __print MoreThan50(x); // “false” x5 since bool operator is <=
        x = x + 1;
    }
    """,
    """
    /* This function takes two integers and returns true if
    the first argument is greater than the second.
    Otherwise it returns false. */
    fun XGreaterY(x: int, y: int) -> bool {
        let ans: bool = true;
        if (y > x) { 
            ans = false; 
        }
        return ans;
    }

    // Same functionality as function above but using less code
    fun XGreaterY2(x: int, y: int) -> bool {
        return x > y;
    }

    // Allocates memory space for 4 variables (x, y, t0, t1).
    fun AverageOfTwo(x: int, y: int) -> float {
        let t0: int = x + y;
        let t1: float = t0 / 2 as float; // casting expression to a float
        return t1;
    }

    /* Same functionality as function above but using less code.
    Note the use of the brackets in the expression following
    the return statement. Allocates space for 2 variables. */
    fun AverageOfTwo2(x: int, y: int) -> float {
        return (x + y) / 2 as float;
    }

    // Takes two integers and returns the max of the two.
    fun Max(x: int, y: int) -> int {
        let m: int = x;
        if (y > m) { 
            m = y; 
        }
        return m;
    }

    __write 10, 14, #00ff00;
    __delay 100;
    __write_box 10, 14, 2, 2, #0000ff;

    for (let i: int = 0; i < 10; i = i + 1) {
        __print i;
        __delay 1000;
    }

    /* This function takes two colours (players) and a max score.
    A while loop is used to iteratively draw random numbers for the two
    players and advance (along the y-axis) the player that gets the
    highest score. Returns the winner (either 1 or 2) when max score is
    reached by any of the players. Winner printed on console. */
    fun Race(p1c: colour, p2c: colour, scoremax: int) -> int {
        let p1score: int = 0;
        let p2score: int = 0;

        // while (Max(p1score, p2score) < scoremax) // Alternative loop
        while ((p1score < scoremax) and (p2score < scoremax)) {
            let p1toss: int = __random_int(1000);
            let p2toss: int = __random_int(1000);

            if (p1toss > p2toss) {
                p1score = p1score + 1;
                __write 1, p1score, p1c;
            } else {
                p2score = p2score + 1;
                __write 2, p2score, p2c;
            }

            __delay 100;
        }

        if (p2score > p1score) {
            return 2;
        }
        return 1;
    }

    // Execution (program entry point) starts at the first statement
    // that is not a function declaration.
    let c1: colour = #00ff00; // green
    let c2: colour = #0000ff; // blue
    let m: int = __height;    // the height (y-values) of the pad
    let w: int = Race(c1, c2, m); // call function Race
    __print w; // prints value of expression to VM logs
""",
    """
    fun sum(arr:int[8]) -> int {
    return arr[0] + arr[1];
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

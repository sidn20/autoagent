import math
import re

def calculate(expression: str) -> str:
    """
    Safely evaluate a math expression.
    Supports: +, -, *, /, **, sqrt, sin, cos, log, pi, e
    
    Why not just use eval()? Because eval("__import__('os').system('rm -rf /')")
    would delete your entire system. We whitelist safe operations only.
    """
    # Clean the expression
    expression = expression.strip()
    expression = expression.strip("'\"")  # remove quotes LLM adds
    expression = expression.replace("^", "**")  # support ^ for power
    expression = expression.replace("x", "*")   # support x for multiply

    # Whitelist allowed characters only
    allowed = re.compile(r'^[\d\s\+\-\*\/\(\)\.\%\*\,]+$')
    
    # Safe math functions
    safe_dict = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log2": math.log2,
        "log10": math.log10,
        "abs": abs,
        "round": round,
        "pi": math.pi,
        "e": math.e,
        "pow": math.pow,
        "ceil": math.ceil,
        "floor": math.floor
    }

    try:
        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return f"{result}"
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: Could not calculate '{expression}' — {str(e)}"

if __name__ == "__main__":
    tests = [
        "2 + 2",
        "10 * 5 - 3",
        "sqrt(144)",
        "2 ** 10",
        "pi * 5 ** 2",
        "log(100, 10)",
        "10 / 0",
        "invalid!!!"
    ]

    print("Calculator Tool Tests:")
    print("=" * 40)
    for expr in tests:
        result = calculate(expr)
        print(f"  {expr:20} = {result}")

from flask import Flask, request, jsonify
from flask_cors import CORS
import ast

app = Flask(__name__)
CORS(app)

def parse_python_code(code):
    try:
        parsed = ast.parse(code)
        explanations = []

        class CodeAnalyzer(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Handle function definition
                params = [arg.arg for arg in node.args.args]
                explanations.append(f"Defines a function `{node.name}` that accepts parameters: {params}.")
                self.generic_visit(node)

            def visit_If(self, node):
                # Handle if condition
                condition = ast.unparse(node.test).strip()
                explanations.append(f"Checks if `{condition}`.")
                
                # Handle return in if block
                for body_node in node.body:
                    if isinstance(body_node, ast.Return):
                        value = ast.unparse(body_node.value).strip()
                        explanations.append(f"Returns `{value}` if the condition is true.")
                
                # Handle else block
                if node.orelse:
                    for else_node in node.orelse:
                        if isinstance(else_node, ast.Return):
                            value = ast.unparse(else_node.value).strip()
                            explanations.append(f"Returns `{value}` otherwise.")
                
                self.generic_visit(node)

        analyzer = CodeAnalyzer()
        analyzer.visit(parsed)
        
        return "\n".join(explanations) if explanations else "No explanation generated."

    except SyntaxError as e:
        raise e
    except Exception as e:
        return f"Error parsing code: {str(e)}"

@app.route('/generate', methods=['POST'])
def generate_explanation():
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        language = data.get('language', 'python')

        if not code:
            return jsonify({"error": "Empty code input!"}), 400

        if language == 'python':
            explanation = parse_python_code(code)
        else:
            explanation = "Unsupported language."

        return jsonify({"explanation": explanation})
    
    except Exception as e:
        print("Backend Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
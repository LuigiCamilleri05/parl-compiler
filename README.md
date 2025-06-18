# 🛠️ PARL Compiler

This project implements a compiler for an **imaginary programming language called PArL**, which compiles into a low-level intermediate language named **PArIR**, designed for a custom stack-based virtual machine.
It covers **lexical analysis**, **parsing**, **semantic analysis**, and **intermediate code generation (PArIR)** targeting a stack-based virtual machine.

Developed as part of the **CPS2000 - Compiler Theory and Practice** course at the University of Malta.

---

## 📁 Project Structure

```bash
├── astnodes.py # AST node definitions
├── code_generator.py # PArIR code generation from AST
├── code_generator_test.py # Tests for the code generator
├── lexer.py # Lexical analyzer (tokenizer)
├── lexer_tests.py # Tokenization tests
├── parser.py # Recursive descent parser for PARL
├── parser_tests.py # Parser tests
├── semantic_analyzer.py # Semantic analysis (type checking, scopes)
├── semantic_tests.py # Tests for semantic analysis
├── symbol_table.py # Symbol table with scope management
└── README.md # Setup instructions and project info
```
---

## 🧪 Requirements

- Python 3.8 or later

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/parl-compiler.git
cd parl-compiler
```

### 2. Run Tests
To see the functionality of each compiler stage run the following files:
```bash
python lexer_tests.py
```
```bash
python parser_tests.py
```
```bash
python semantic_tests.py
```
```bash 
python code_generator_test
```
💡 Note: The code generator produces PArIR for a virtual machine tied to a simulator that is not publicly accessible.

👨‍💻 Author
Luigi Camilleri
# Simple Pascal Interpreter

## Overview

The Simple Pascal Interpreter is a Python-based interpreter designed to parse and execute Pascal-like programming language code. This project aims to provide a basic understanding of how interpreters work, including tokenization, parsing, and execution of expressions and statements.

## Features

- **Tokenization**: Converts input code into tokens that represent the basic elements of the language (e.g., integers, operators).
- **Parsing**: Analyzes the token stream to create an Abstract Syntax Tree (AST) that represents the structure of the code.
- **Execution**: Evaluates the AST to execute the code and produce results.
- **Error Handling**: Provides error messages for parsing errors, invalid operators, and division by zero.

## Project Structure

The project consists of several Python files organized as follows:

- **Calc.py**: A simple calculator interpreter that supports basic arithmetic operations.
- **CalcwtAST.py**: An interpreter that uses an Abstract Syntax Tree (AST) for expression evaluation.
- **Calcwtprecedence.py**: An interpreter that respects operator precedence in arithmetic expressions.
- **PASCAL.py**: The main entry point for executing Pascal programs.
- **Utils/**: A directory containing utility modules for tokenization, parsing, and symbol table management.
  - **lexer.py**: Implements the lexer for tokenizing input code.
  - **Interpreter_pascal.py**: Contains the interpreter logic for executing Pascal code.
  - **Symboltable_pascal.py**: Manages symbol tables for variable declarations and scopes.
  - **lexer_pascal.py**: Implements the lexer for Pascal-specific tokens.
  - **Parser_pascal.py**: Implements the parser for Pascal programs.

## Getting Started

### Prerequisites

- Python 3.x installed on your machine.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/simple-pascal-interpreter.git
   cd simple-pascal-interpreter

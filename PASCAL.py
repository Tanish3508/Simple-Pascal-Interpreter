from Utils.Interpreter_pascal import Interpreter
from Utils.Semantic_Analyzer_pascal import SemanticAnalyzer
from Utils.Parser_pascal import Parser
from Utils.lexer_pascal import Lexer,SemanticError,ParserError,LexerError
print('All imported\n')

import sys

def main():
   text="""\
     PROGRAM Part10;
VAR
   number     : INTEGER;
   a, b, c, x : INTEGER;
   y          : REAL;

BEGIN {Part10}
   BEGIN
      number := 2;
      a := number;
      b := 10 * a + 10 * number DIV 4;
      c := a - - b
   END;
   x := 11;
   y := 20 / 7 + 3.14;
   { writeln('a = ', a); }
   { writeln('b = ', b); }
   { writeln('c = ', c); }
   { writeln('number = ', number); }
   { writeln('x = ', x); }
   { writeln('y = ', y); }
END.  {Part10}
     """
        
   lexer = Lexer(text)
   try:
      parser = Parser(lexer)
      tree = parser.parse()
   except (ParserError,LexerError) as e:
      print(e.message)
      sys.exit(1)
   semantic_analyzer = SemanticAnalyzer()
   try:
      semantic_analyzer.visit(tree)
   except SemanticError as e:
      print(e.message)
      sys.exit(1)
   interpreter=Interpreter(tree)
   interpreter.interpret()
   
if __name__=='__main__':
    main()
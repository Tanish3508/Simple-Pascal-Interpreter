from Utils.Symboltable_pascal import SymbolTableBuilder
from Utils.Interpreter_pascal import Interpreter
from Utils.Parser_pascal import Parser
from Utils.lexer_pascal import Lexer
print('All imported\n')

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
        
    lexer=Lexer(text)
    parser=Parser(lexer)
    interpreter=Interpreter(parser)
    symtab_builder=SymbolTableBuilder()
    tree=parser.parse()
    interpreter.visit(tree)
    symtab_builder.visit(tree)
    print(symtab_builder.symtab)
    print(interpreter.GLOBAL_SCOPE)
if __name__=='__main__':
    main()
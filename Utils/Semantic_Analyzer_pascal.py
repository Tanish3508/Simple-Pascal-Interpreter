import argparse
import sys

_SHOULD_LOG_SCOPE=False

from Utils.lexer_pascal import Lexer,SemanticError,ParserError,LexerError,ErrorCode
from Utils.Parser_pascal import Parser
from Utils.Symboltable_pascal import ScopedSymbolTable,VarSymbol,ProcedureSymbol

class NodeVisitor(object):
    def visit(self,node):
        method_name='visit_'+type(node).__name__
        visitor=getattr(self,method_name,self.generic_visit)
        return visitor(node)
    def generic_visit(self,node):
        raise Exception(f'No visit_{type(node).__name__} method')
        
class SemanticAnalyzer(NodeVisitor):
    def __init__(self):
        self.current_scope=None
    
    def error(self,error_code,token):
        raise SemanticError(error_code==error_code,token=token,message=f'{error_code.value} -> {token}')
    
    def log(self,msg):
        if _SHOULD_LOG_SCOPE:
            print(msg)
    
    def visit_Block(self,node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)
    
    def visit_Program(self,node):
        print('ENTER scope: global')
        global_scope=ScopedSymbolTable(scope_name='global',scope_level=1,enclosing_scope=self.current_scope)
        self.current_scope=global_scope
    
        self.visit(node.block)
        print(global_scope)
        self.current_scope=self.current_scope.enclosing_scope
        print('LEAVE scope: global')
    
    def visit_ProcedureCall(self,node):
        proc_name=node.proc_name
        token=self.current_scope.lookup(proc_name)
        if len(token.params)!=len(node.actual_params):
            self.error(error_code=ErrorCode.PARAM_INEQUALITY,token=node.token)
        for param_node in node.actual_params:
            self.visit(param_node)
        proc_symbol=self.current_scope.lookup(node.proc_name)
        node.proc_symbol=proc_symbol
    
    def visit_Compound(self,node):
        for child in node.children:
            self.visit(child)
    
    def visit_Var(self,node):
        var_name=node.value
        var_symbol=self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise Exception(f"Error: Symbol(identifier) not found '{var_name}'")
    
    def visit_Assign(self,node):
        self.visit(node.right)
        self.visit(node.left)
    
    def visit_BinOp(self,node):
        self.visit(node.left)
        self.visit(node.right)
    
    def visit_Num(self,node):
        pass
    
    def visit_UnaryOp(self,node):
        pass
    
    def visit_NoOp(self,node):
        pass
    
    def visit_ProcedureDecl(self,node):
        proc_name=node.proc_name
        proc_symbol=ProcedureSymbol(proc_name)
        self.current_scope.insert(proc_symbol)
        
        print(f'ENTER scope: {proc_name}')
        procedure_scope=ScopedSymbolTable(scope_name=proc_name,scope_level=self.current_scope.scope_level+1,enclosing_scope=self.current_scope)
        self.current_scope=procedure_scope
        
        for param in node.params:
            param_type=self.current_scope.lookup(param.type_node.value)
            param_name=param.var_node.value
            var_symbol=VarSymbol(param_name,param_type)
            self.current_scope.insert(var_symbol)
            proc_symbol.params.append(var_symbol)
            
        self.visit(node.block_node)
        
        print(procedure_scope)
        self.current_scope=self.current_scope.enclosing_scope
        print(f'LEAVE scope: {proc_name}')
        self.log(f'LEAVE scope: {proc_name}')
        proc_symbol.block_ast=node.block_node
               
    def visit_VarDecl(self,node):
        type_name=node.type_node.value
        type_symbol=self.current_scope.lookup(type_name)
        
        var_name=node.var_node.value
        var_symbol=VarSymbol(var_name,type_symbol)
        if self.current_scope.lookup(var_name,current_scope_only=True):
            self.error(error_code=ErrorCode.DUPLICATE_ID,token=node.var_node.token)
        
        self.current_scope.insert(var_symbol)
    
    def visit_Var(self,node):
        var_name=node.value
        var_symbol=self.current_scope.lookup(var_name)
        if var_symbol is None:
            self.error(error_code=ErrorCode.ID_NOT_FOUND,token=node.token)
            
    
        
def main():
    text = """
program Main;
   var b, x, y : real;
   var z : integer;

   procedure AlphaA(a : integer);
      var b : integer;

      procedure Beta(c : integer);
         var y : integer;

         procedure Gamma(c : integer);
            var x : integer;
         begin { Gamma }
            x := a + b + c + x + y + z;
         end;  { Gamma }

      begin { Beta }

      end;  { Beta }

   begin { AlphaA }

   end;  { AlphaA }

   procedure AlphaB(a : integer);
      var c : real;
   begin { AlphaB }
      c := a + b;
   end;  { AlphaB }

begin { Main }
end.  { Main }
"""
    #parser = argparse.ArgumentParser(
    #    description='SPI - Simple Pascal Interpreter'
    #)
    #parser.add_argument('inputfile', help='Pascal source file')
    #parser.add_argument(
    #    '--scope',
    #    help='Print scope information',
    #    action='store_true',
    #)
    #args = parser.parse_args()
    #global _SHOULD_LOG_SCOPE
    #_SHOULD_LOG_SCOPE = args.scope
    
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
if __name__=='__main__':
    main()
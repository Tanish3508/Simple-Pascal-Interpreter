from collections import OrderedDict
from Utils.lexer_pascal import Lexer,TokenType
from Utils.Parser_pascal import Parser

class NodeVisitor(object):
    def visit(self,node):
        method_name='visit_'+type(node).__name__
        visitor=getattr(self,method_name,self.generic_visit)
        return visitor(node)
    def generic_visit(self,node):
        raise Exception(f'No visit_{type(node).__name__} method')

class Symbol(object):
    def __init__(self,name,type=None):
        self.name=name
        self.type=type

class ProcedureSymbol(Symbol):      
    def __init__(self,name,params=None):
        super(ProcedureSymbol,self).__init__(name)
        self.params=params if params is not None else [] 
    
    def __str__(self):
        return f'<{self.__class__.__name__}(name={self.name}, parameters={self.params})>'

    __repr__=__str__

class BuiltinTypeSymbol(Symbol):
    def __init__(self,name):
        super().__init__(name)
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.name}')>"
    
class VarSymbol(Symbol):
    def __init__(self,name,type):
        super().__init__(name,type)
    
    def __str__(self):
        return f"<{self.__class__.__name__}(name='{self.name}', type='{self.type}')>"
    
    __repr__=__str__
    
class ScopedSymbolTable(object):
    def __init__(self,scope_name,scope_level,enclosing_scope=None):
        self._symbols = OrderedDict()
        self.scope_name=scope_name
        self.scope_level=scope_level
        self.enclosing_scope=enclosing_scope
        self._init_builtins()
    
    def _init_builtins(self):
        self.insert(BuiltinTypeSymbol(TokenType.INT))
        self.insert(BuiltinTypeSymbol(TokenType.REAL))
    
    def __str__(self):
        h1='SCOPE (SCOPED SYMBOL TABLE)'
        lines=['\n',h1, '='*len(h1)]
        for h_name,h_value in (('Scope name',self.scope_name),('Scope level',self.scope_level),('Enclosing Scope',self.enclosing_scope.scope_name if self.enclosing_scope else None)):
            lines.append('%-15s: %s' % (h_name,h_value))
        
        h2='Scope (Scoped symbol table) contents'
        lines.extend([h2, '-'*len(h2)])
        lines.extend(('%7s: %r' % (key,value)) for key,value in self._symbols.items())
        lines.append('\n')
        s='\n'.join(lines)
        return s

    __repr__=__str__
    
    def insert(self,symbol):
        self._symbols[symbol.name]=symbol

    def lookup(self,name,current_scope_only=False):
        symbol=self._symbols.get(name)
        if symbol is not None:
            return symbol
        if current_scope_only:
            return None
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)
    
class S2SCompiler(NodeVisitor):
    def __init__(self):
        self.current_scope=None
        self.code=[]
    
    def visit_Block(self,node):
        for declaration in node.declarations:
            self.visit(declaration)
        indent='\t'*(self.current_scope.scope_level-1)
        self.code.append('\n'+indent+'begin')
        self.visit(node.compound_statement)
    
    def visit_Program(self,node):
        global_scope=ScopedSymbolTable(scope_name='global',scope_level=1,enclosing_scope=self.current_scope)
        self.current_scope=global_scope
        self.code.append(f'program {node.name};')
        
        self.visit(node.block)
        self.code.append('end. {END OF Main}')
        self.current_scope=self.current_scope.enclosing_scope
    
    def visit_Compound(self,node):
        for child in node.children:
            self.visit(child)
    
    def visit_Var(self,node):
        var_name=node.value
        var_symbol=self.scope.lookup(var_name)
        if var_symbol is None:
            raise Exception(f"Error: Symbol(identifier) not found '{var_name}'")
    
    def visit_Assign(self,node):
        r=self.visit(node.right)
        l=self.visit(node.left)
        indent='\t'*(self.current_scope.scope_level)
        self.code.append(indent+l+' := '+r+';')
    
    def visit_BinOp(self,node):
        l=self.visit(node.left)
        r=self.visit(node.right)
        if node.op.type==TokenType.PLUS:
            l+=' + '+r
        elif node.op.type==TokenType.MINUS:
            l+=' - '+r
        elif node.op.type==TokenType.MUL:
            l+=' * '+r
        elif node.op.type==TokenType.INT_DIV:
            l+=' DIV '+r
        elif node.op.type==TokenType.FLOAT_DIV:
            l+=' / '+r
        return l
    
    def visit_NoOp(self,node):
        self.code.append(' ')
        pass
    
    def visit_ProcedureDecl(self,node):
        proc_name=node.proc_name
        proc_symbol=ProcedureSymbol(proc_name)
        self.current_scope.insert(proc_symbol)

        procedure_scope=ScopedSymbolTable(scope_name=proc_name,scope_level=self.current_scope.scope_level+1,enclosing_scope=self.current_scope)
        self.current_scope=procedure_scope
        parameters=[]
        for param in node.params:
            param_type=self.current_scope.lookup(param.type_node.value)
            param_name=param.var_node.value
            var_symbol=VarSymbol(param_name,param_type)
            parameters.append(f'{param_name}{self.current_scope.scope_level} : {param_type}')
            self.current_scope.insert(var_symbol)
            proc_symbol.params.append(var_symbol)
        
        indent='\t'*(self.current_scope.scope_level-1)
        paramstr=', '.join(parameters)
        h=f'procedure {proc_name}{self.current_scope.scope_level-1}({paramstr});'
        self.code.append(indent+h)
        self.visit(node.block_node)
        self.code.append(indent+'end; {END OF '+proc_name+str(self.current_scope.scope_level-1)+'}')
        self.current_scope=self.current_scope.enclosing_scope

               
    def visit_VarDecl(self,node):
        type_name=node.type_node.value
        type_symbol=self.current_scope.lookup(type_name)
        
        var_name=node.var_node.value
        var_symbol=VarSymbol(var_name,type_symbol)
        if self.current_scope.lookup(var_name,current_scope_only=True):
            raise Exception(f"Error: Duplicate identifier '{var_name}' found")
        
        self.current_scope.insert(var_symbol)
        indent='\t'*(self.current_scope.scope_level)
        self.code.append(indent+f'var {var_name}{self.current_scope.scope_level} : {type_name};')
    
    def visit_Var(self,node):
        var_name=node.value
        var_symbol=self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise Exception(f"Error: Symbol(identifier) not found '{var_name}' ")
        return f'<{var_name}{self.current_scope.scope_level}:{var_symbol.type}>'

if __name__ == '__main__':
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

    lexer = Lexer(text)
    parser = Parser(lexer)
    tree = parser.parse()
    compiler = S2SCompiler()
    compiler.visit(tree)
    code='\n'.join(compiler.code)
    print(code)
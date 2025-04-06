INT,REAL,PLUS,MINUS,MUL,DIV,LBRAK,RBRAK,EOF='INTEGER','REAL','PLUS','MINUS','MUL','DIV','(',')','EOF'
BEGIN,END,ASSIGN,ID,SEMI,DOT='BEGIN','END','=','id',';','.'
PROGRAM,VAR,COLON,COMMA,INT_CONST,REAL_CONST,INT_DIV,REAL_DIV='PROGRAM','VAR','COLON','COMMA','INTEGER_CONST','REAL_CONST','INTEGER_DIV','REAL_DIV'
from collections import OrderedDict

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
    
class BuiltinTypeSymbol(Symbol):
    def __init__(self,name):
        super().__init__(name)
    
    def __str__(self):
        return self.name
    
    __repr__=__str__
    
class VarSymbol(Symbol):
    def __init__(self,name,type):
        super().__init__(name,type)
    
    def __str__(self):
        return f'<{self.name}:{self.type}>'
    
    __repr__=__str__
    
class SymbolTable(object):
    def __init__(self):
        self._symbols=OrderedDict()
        self._init_builtins()
        
    
    def _init_builtins(self):
        self.define(BuiltinTypeSymbol(INT))
        self.define(BuiltinTypeSymbol(REAL))
    
    def __str__(self):
        s=f'Symbols: {[value for value in self._symbols.values()]}'
        return s
    
    __repr__=__str__
    
    def define(self,symbol):
        print(f'Define: {symbol}')
        self._symbols[symbol.name]=symbol
    
    def lookup(self,name):
        print(f'Lookup: {name}')
        symbol=self._symbols.get(name)
        return symbol
    
class SymbolTableBuilder(NodeVisitor):
    def __init__(self):
        self.symtab=SymbolTable()
    
    def visit_Block(self,node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)
    
    def visit_Program(self,node):
        self.visit(node.block)
    
    def visit_BinOp(self,node):
        self.visit(node.left)
        self.visit(node.right)
    
    def visit_Num(self,node):
        pass
    
    def visit_UnaryOp(self,node):
        self.visit(node.expr)
    
    def visit_Compound(self,node):
        for child in node.children:
            self.visit(child)
    
    def visit_NoOp(self,node):
        pass
    
    def visit_VarDecl(self,node):
        type_name=node.type_node.value
        type_symbol=self.symtab.lookup(type_name)
        var_name=node.var_node.value
        var_symbol=VarSymbol(var_name,type_symbol)
        self.symtab.define(var_symbol)
    
    def visit_Assign(self,node):
        var_name=node.left.value
        var_symbol=self.symtab.lookup(var_name)
        if var_symbol is None:
            raise NameError(repr(var_name))
        self.visit(node.right)
    
    def visit_Var(self,node):
        var_name=node.value
        var_symbol=self.symtab.lookup(var_name)
        if var_symbol is None:
            raise NameError(repr(var_name))
        
        
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

class ProcedureSymbol(Symbol):      
    def __init__(self,name,params=None):
        super(ProcedureSymbol,self).__init__(name)
        self.params=params if params is not None else [] 
        self.block_ast=None
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
        self.insert(BuiltinTypeSymbol('INTEGER'))
        self.insert(BuiltinTypeSymbol('REAL'))
    
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
    
class SymbolTableBuilder(NodeVisitor):
    def __init__(self):
        self.symtab=ScopedSymbolTable()
    
    def visit_Block(self,node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)
    
    def visit_ProcedureDecl(self,node):
        pass
    
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
        
        
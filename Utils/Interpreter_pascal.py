INT,REAL,PLUS,MINUS,MUL,DIV,LBRAK,RBRAK,EOF='INTEGER','REAL','PLUS','MINUS','MUL','DIV','(',')','EOF'
BEGIN,END,ASSIGN,ID,SEMI,DOT='BEGIN','END','=','id',';','.'
PROGRAM,VAR,COLON,COMMA,INT_CONST,REAL_CONST,INT_DIV,REAL_DIV='PROGRAM','VAR','COLON','COMMA','INTEGER_CONST','REAL_CONST','INTEGER_DIV','REAL_DIV'

class NodeVisitor(object):
    def visit(self,node):
        method_name='visit_'+type(node).__name__
        visitor=getattr(self,method_name,self.generic_visit)
        return visitor(node)
    def generic_visit(self,node):
        raise Exception(f'No visit_{type(node).__name__} method')

class Interpreter(NodeVisitor):
    def __init__(self,parser):
        self.parser=parser
        self.GLOBAL_SCOPE={}
    
    def visit_BinOp(self,node):
        if node.op.type==PLUS:
            return self.visit(node.left)+self.visit(node.right)
        elif node.op.type==MINUS:
            return self.visit(node.left)-self.visit(node.right)
        elif node.op.type==MUL:
            return self.visit(node.left)*self.visit(node.right)
        elif node.op.type==INT_DIV:
            return self.visit(node.left)//self.visit(node.right)
        elif node.op.type==REAL_DIV:
            return float(self.visit(node.left))/float(self.visit(node.right))
    
    def visit_UnaryOp(self,node):
        op=node.op.type
        if op==PLUS:
            return +self.visit(node.expr)
        else:
            return -self.visit(node.expr)
    
    def visit_Compound(self,node):
        for child in node.children:
            self.visit(child)
    
    def visit_NoOp(self,node):
        pass
    
    def visit_Assign(self,node):
        var_name=node.left.value
        self.GLOBAL_SCOPE[var_name]=self.visit(node.right)
    
    def visit_Var(self,node):
        var_name=node.value
        val=self.GLOBAL_SCOPE.get(var_name)
        if val is None:
            raise NameError(repr(var_name))
        else:
            return val
    
    def visit_Program(self,node):
        self.visit(node.block)
    
    def visit_Block(self,node):
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)
        
    def visit_VarDecl(self,node):
        pass
    
    def visit_Type(self,node):
        pass
        
    def visit_Num(self,node):
        return node.value
    
    def interpret(self):
        tree=self.parser.parse()
        return self.visit(tree)

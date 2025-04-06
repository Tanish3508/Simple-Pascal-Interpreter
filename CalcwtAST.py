INT,PLUS,MINUS,MUL,DIV,LBRAK,RBRAK,EOF='INTEGER','PLUS','MINUS','MUL','DIV','(',')','EOF'
from Utils.lexer import Lexer

class AST(object):
    pass

class BinOp(AST):
    def __init__(self,left,op,right):
        self.left=left
        self.token=self.op=op
        self.right=right

class UnaryOp(AST):
    def __init__(self,op,expr):
        self.token=self.op=op
        self.expr=expr
    
class Num(AST):
    def __init__(self,token):
        self.token=token
        self.value=token.value
    
class Parser(object):
    def __init__(self,lexer:Lexer):
        self.lexer=lexer
        self.current_token=self.lexer.get_next_token()
    
    def error(self):
        raise Exception('Invalid Syntax')
    
    def eat(self,token_type):
        if self.current_token.type==token_type:
            self.current_token=self.lexer.get_next_token()
        else:
            self.error()
    
    def factor(self):
        token=self.current_token
        if token.type==PLUS:
            self.eat(PLUS)
            node=UnaryOp(token,self.factor())
            return node
        elif token.type==MINUS:
            self.eat(MINUS)
            node=UnaryOp(token,self.factor())
            return node
        elif token.type==INT:
            self.eat(INT)
            return Num(token)
        elif token.type==LBRAK:
            self.eat(LBRAK)
            node=self.expr()
            self.eat(RBRAK)
            return node
    
    def term(self):
        node=self.factor()
        while self.current_token.type in (MUL,DIV):
            token=self.current_token
            if token.type==MUL:
                self.eat(MUL)
            else:
                self.eat(DIV)
            node=BinOp(left=node,op=token,right=self.factor())
        return node
    
    def expr(self):
        node=self.term()
        while self.current_token.type in (PLUS,MINUS):
            token=self.current_token
            if token.type==PLUS:
                self.eat(PLUS)
            else:
                self.eat(MINUS)
            node=BinOp(left=node,op=token,right=self.term())
        return node
    
    def parse(self):
        return self.expr()
    
class NodeVisitor(object):
    def visit(self,node):
        method_name='visit_'+type(node).__name__
        visitor=getattr(self,method_name,self.generic_visit)
        return visitor(node)
    def generic_visit(self,node):
        raise Exception(f'No visit_{type(node).__name__} method')

class Interpreter(NodeVisitor):
    def __init__(self,parser:Parser):
        self.parser=parser
    
    def visit_BinOp(self,node):
        if node.op.type==PLUS:
            return self.visit(node.left)+self.visit(node.right)
        elif node.op.type==MINUS:
            return self.visit(node.left)-self.visit(node.right)
        elif node.op.type==MUL:
            return self.visit(node.left)*self.visit(node.right)
        elif node.op.type==DIV:
            return self.visit(node.left)/self.visit(node.right)
    
    def visit_UnaryOp(self,node):
        op=node.op.type
        if op==PLUS:
            return +self.visit(node.expr)
        else:
            return -self.visit(node.expr)
        
    def visit_Num(self,node):
        return node.value
    
    def interpret(self):
        tree=self.parser.parse()
        return self.visit(tree)
    
def main():
    while True:
        try:
            text=input('spi> ')
        except EOFError:
            break
        
        if not text:continue
        
        lexer=Lexer(text)
        parser=Parser(lexer)
        interpreter=Interpreter(parser)
        result=interpreter.interpret()
        print(result)

if __name__=='__main__':
    main()
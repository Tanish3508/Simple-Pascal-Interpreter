INT,PLUS,MINUS,MUL,DIV,LBRAK,RBRAK,EOF='INTEGER','PLUS','MINUS','MUL','DIV','(',')','EOF'
from Utils.lexer import Lexer

class Interpreter(object):
    def __init__(self,lexer:Lexer):
        self.lexer=lexer
        self.current_token=self.lexer.get_next_token()
        
    def error(self):
        raise Exception('Invalid syntax')
    
    def eat(self,token_type):
        if self.current_token.type==token_type:
            self.current_token=self.lexer.get_next_token()
        else:
            self.error()
        
    def factor(self):
        token=self.current_token
        if token.type==INT:     
            self.eat(INT)
            return token.value
        elif token.type==LBRAK:
            self.eat(LBRAK)
            res=self.expr()
            self.eat(RBRAK)
            return res
    
    def term(self):
        res=self.factor()
        while self.current_token.type in (MUL,DIV):
            token=self.current_token
            if token.type==MUL:
                self.eat(MUL)
                res*=self.factor()
            elif token.type==DIV:
                self.eat(DIV)
                res/=self.factor()
        return res
    
    def expr(self):
        res=self.term()
        while self.current_token.type in (PLUS,MINUS):
            token=self.current_token
            if token.type==PLUS:
                self.eat(PLUS)
                res+=self.term()
            elif token.type==MINUS:
                self.eat(MINUS)
                res-=self.term()
        return res
    
        
def main():
    while True:
        try:
            text=input('calc>')
        except EOFError:
            break
        if not text:
            continue
        lexer=Lexer(text)
        interpreter=Interpreter(lexer)
        res=interpreter.expr()
        print(res)

if __name__=='__main__':
    main()  
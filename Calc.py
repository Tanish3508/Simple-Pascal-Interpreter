INT,PLUS,MINUS,MUL,DIV,EOF='INTEGER','PLUS','MINUS','MUL','DIV','EOF'
PE,OE,ZDE='parsing error','missing operator error','division by 0 error'
class Token(object):
    def __init__(self,type,value):
        self.type=type
        self.value=value
        
    def __str__(self):
        return f'Token({self.type},{repr(self.value)})'
    
    def __repr__(self):
        return self.__str__()
    
class Interpreter(object):
    def __init__(self,text):
        self.text=text
        self.pos=0
        self.current_token=None
        self.current_char=self.text[self.pos]
        
    def error(self,etype):
        if etype==PE:
            raise Exception('Error parsing Input')
        elif etype==OE:
            raise Exception('Not a valid operator')
        elif etype==ZDE:
            raise ZeroDivisionError
    
    def advance(self):
        self.pos+=1
        if self.pos>len(self.text)-1:
            self.current_char=None
        else:
            self.current_char=self.text[self.pos]
    
    def skip_blank(self):
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def integer(self):
        result=''
        while self.current_char and self.current_char.isdigit():
            result+=self.current_char
            self.advance()
        return int(result)
    
    def get_next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_blank()
                continue
            
            if self.current_char.isdigit():
                return Token(INT,self.integer())
            
            if self.current_char=='+':
                self.advance()
                return Token(PLUS,'+')
            if self.current_char=='-':
                self.advance()
                return Token(MINUS,'-')
            if self.current_char=='*':
                self.advance()
                return Token(MUL,'*')
            if self.current_char=='/':
                self.advance()
                return Token(DIV,'/')
            self.error(PE) 
        return Token(EOF,None)
    
    def eat(self,token_type):
        if self.current_token.type==token_type:
            self.current_token=self.get_next_token()
        else:
            self.error(PE)
    
    def term(self):
        token=self.current_token
        self.eat(INT)
        return token.value
    
    def expr(self):
        self.current_token=self.get_next_token()
        result=self.term()
        while self.current_token.type in (PLUS,MINUS,MUL,DIV):
            op=self.current_token
            if op.type==PLUS:
                self.eat(PLUS)
                result=result+self.term()
            elif op.type==MINUS:
                self.eat(MINUS)
                result=result-self.term()
            elif op.type==MUL:
                self.eat(MUL)
                result=result*self.term()
            elif op.type==DIV:
                self.eat(DIV)
                a=self.term()
                if a!=0:result=result/a
                else:self.error(ZDE)
            else:
                self.error(OE)
            
        return result
def main():
    while True:
        try:
            text=input('calc>')
        except EOFError:
            break
        
        if not text:continue
        
        interpreter=Interpreter(text)
        result=interpreter.expr()
        print(result)

if __name__=='__main__':
    main()
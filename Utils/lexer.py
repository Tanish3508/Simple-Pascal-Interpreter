INT,PLUS,MINUS,MUL,DIV,LBRAK,RBRAK,EOF='INTEGER','PLUS','MINUS','MUL','DIV','(',')','EOF'

class Token(object):
    def __init__(self,type,value):
        self.type=type
        self.value=value
    
    def __str__(self):
        return f'Token({self.type},{repr(self.value)})'
    
    def __repr__(self):
        return self.__str__()
    
class Lexer(object):
    def __init__(self,text):
        self.text=text
        self.pos=0
        self.current_char=self.text[self.pos]
    
    def error(self):
        raise Exception('Invalid Character')
    
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
        res=''
        while self.current_char and self.current_char.isdigit():
            res+=self.current_char
            self.advance()
        return int(res)
    
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
            
            if self.current_char=='(':
                self.advance()
                return Token(LBRAK,'(')
            
            if self.current_char==')':
                self.advance()
                return Token(RBRAK,')')
            
            self.error()
    
        return Token(EOF,None)
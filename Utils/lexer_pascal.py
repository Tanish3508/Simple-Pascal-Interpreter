INT,REAL,PLUS,MINUS,MUL,DIV,LBRAK,RBRAK,EOF='INTEGER','REAL','PLUS','MINUS','MUL','DIV','(',')','EOF'
BEGIN,END,ASSIGN,ID,SEMI,DOT='BEGIN','END','=','id',';','.'
PROGRAM,VAR,COLON,COMMA,INT_CONST,REAL_CONST,INT_DIV,REAL_DIV='PROGRAM','VAR','COLON','COMMA','INTEGER_CONST','REAL_CONST','INTEGER_DIV','REAL_DIV'

class Token(object):
    def __init__(self,type,value):
        self.type=type
        self.value=value
    
    def __str__(self):
        return f'Token({self.type},{repr(self.value)})'
    
    def __repr__(self):
        return self.__str__()

RESERVED_KEYWORDS = {
    'PROGRAM': Token('PROGRAM', 'PROGRAM'),
    'VAR': Token('VAR', 'VAR'),
    'DIV': Token('INTEGER_DIV', 'DIV'),
    'INTEGER': Token('INTEGER', 'INTEGER'),
    'REAL': Token('REAL', 'REAL'),
    'BEGIN': Token('BEGIN', 'BEGIN'),
    'END': Token('END', 'END'),
}
    
class Lexer(object):
    def __init__(self,text):
        self.text=text
        self.pos=0
        self.current_char=self.text[self.pos]
    
    def error(self):
        raise Exception('Invalid Character')
    
    def peek(self):
        peek_pos=self.pos+1
        if peek_pos>len(self.text)-1:
            return None
        else:
            return self.text[peek_pos]
    
    def advance(self):
        self.pos+=1
        if self.pos>len(self.text)-1:
            self.current_char=None
        else:
            self.current_char=self.text[self.pos]
    
    def _id(self):
        result=''
        while self.current_char and (self.current_char.isalnum() or self.current_char=='_'):
            result+=self.current_char
            self.advance()
        token=RESERVED_KEYWORDS.get(result,Token(ID,result))
        return token
    
    def skip_blank(self):
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        while self.current_char!='}':
            self.advance()
        self.advance()
    
    
    
    def number(self):
        res=''
        while self.current_char and self.current_char.isdigit():
            res+=self.current_char
            self.advance()
        if self.current_char=='.':
            res+=self.current_char
            self.advance()

            while self.current_char and self.current_char.isdigit():
                res+=self.current_char
                self.advance()
            token=Token(REAL_CONST,float(res))
        else:
            token=Token(INT_CONST,int(res))
        return token
    
    def get_next_token(self):
        while self.current_char:
            
            if self.current_char.isspace():
                self.skip_blank()
                continue
            
            if self.current_char=='{':
                self.advance()
                self.skip_comment()
                continue
            
            if self.current_char.isalpha() or self.current_char=='_':
                return self._id()
            
            if self.current_char==':' and self.peek()=='=':
                self.advance()
                self.advance()
                return Token(ASSIGN,':=')
            
            if self.current_char==':':
                self.advance()
                return Token(COLON,':')
            
            if self.current_char==';':
                self.advance()
                return Token(SEMI,';')
            
            if self.current_char==',':
                self.advance()
                return Token(COMMA,',')
            
            if self.current_char=='.':
                self.advance()
                return Token(DOT,'.')
            
            if self.current_char.isdigit():
                return self.number()
            
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
                return Token(REAL_DIV,'/')
            
            if self.current_char=='(':
                self.advance()
                return Token(LBRAK,'(')
            
            if self.current_char==')':
                self.advance()
                return Token(RBRAK,')')
            
            self.error()
    
        return Token(EOF,None)
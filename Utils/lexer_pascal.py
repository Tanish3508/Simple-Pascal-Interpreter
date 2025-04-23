from enum import Enum

class Token(object):
    def __init__(self,type,value,lineno=None,column=None):
        self.type=type
        self.value=value
        self.lineno=lineno
        self.column=column
    
    def __str__(self):
        return f'Token({self.type}, {repr(self.value)}, position={self.lineno}:{self.column})'
    
    def __repr__(self):
        return self.__str__()

class TokenType(Enum):
    PLUS          = '+'
    MINUS         = '-'
    MUL           = '*'
    FLOAT_DIV     = '/'
    LBRAK         = '('
    RBRAK         = ')'
    SEMI          = ';'
    DOT           = '.'
    COLON         = ':'
    COMMA         = ','
    

    PROGRAM       = 'PROGRAM'  
    INT           = 'INTEGER'
    REAL          = 'REAL'
    INT_DIV       = 'DIV'
    VAR           = 'VAR'
    PROCEDURE     = 'PROCEDURE'
    BEGIN         = 'BEGIN'
    END           = 'END'      
    ID            = 'ID'
    INT_CONST     = 'INTEGER_CONST'
    REAL_CONST    = 'REAL_CONST'
    ASSIGN        = ':='
    EOF           = 'EOF'

def _build_reserved_keywords():
    tt_list=list(TokenType)
    start_index=tt_list.index(TokenType.PROGRAM)
    end_index=tt_list.index(TokenType.END)
    reserved_keywords={token_type.value : token_type for token_type in tt_list[start_index:end_index+1]}
    return reserved_keywords
        
RESERVED_KEYWORDS = _build_reserved_keywords()
    
class Lexer(object):
    def __init__(self,text):
        self.text=text
        self.pos=0
        self.current_char=self.text[self.pos]
        self.lineno=1
        self.column=1
    
    def error(self):
        s=f"Lexer Error on '{self.current_char}' line: {self.lineno} column: {self.column}"
        raise LexerError(message=s)
    
    def peek(self):
        peek_pos=self.pos+1
        if peek_pos>len(self.text)-1:
            return None
        else:
            return self.text[peek_pos]
    
    def advance(self):
        if self.current_char=='\n':
            self.lineno+=1
            self.column=0
        
        self.pos+=1
        if self.pos>len(self.text)-1:
            self.current_char=None
        else:
            self.current_char=self.text[self.pos]
            self.column+=1
    
    def _id(self):
        token=Token(type=None,value=None,lineno=self.lineno,column=self.column)
        
        value=''
        while self.current_char and (self.current_char.isalnum() or self.current_char=='_'):
            value+=self.current_char
            self.advance()
        token_type=RESERVED_KEYWORDS.get(value.upper())
        if token_type is None:
            token.type=TokenType.ID
            token.value=value
        else:
            token.type=token_type
            token.value=value.upper()
        return token
    
    def skip_blank(self):
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        while self.current_char!='}':
            self.advance()
        self.advance()
    
    def number(self):
        token=Token(type=None,value=None,lineno=self.lineno,column=self.column)
        
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
            token.type=TokenType.REAL_CONST
            token.value=float(res)
        else:
            token.type=TokenType.INT_CONST
            token.value=int(res)
        
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
            
            if self.current_char.isdigit():
                return self.number()
            
            if self.current_char.isalpha() or self.current_char=='_':
                return self._id()
            
            if self.current_char==':' and self.peek()=='=':
                token=Token(type=TokenType.ASSIGN,value=TokenType.ASSIGN.value,lineno=self.lineno,column=self.column)
                self.advance()
                self.advance()
                return token
            
            try:
                token_type=TokenType(self.current_char)
            except ValueError:
                self.error()
            
            else:
                token=Token(type=token_type,value=token_type.value,lineno=self.lineno,column=self.column)
                self.advance()
                return token
    
        return Token(type=TokenType.EOF,value=None)
    
class ErrorCode(Enum):
    UNEXPECTED_TOKEN='Unexpected token'
    ID_NOT_FOUND='Identifier not found'
    DUPLICATE_ID='Duplicate id found'
    PARAM_INEQUALITY='More or Less Parameters than needed'

class Error(Exception):
    def __init__(self,error_code=None,token=None,message=None):
        self.error_code=error_code
        self.token=token
        self.message=f'{self.__class__.__name__}: {message}'
        
class LexerError(Error):
    pass

class ParserError(Error):
    pass
     
class SemanticError(Error):
    pass
INT,REAL,PLUS,MINUS,MUL,DIV,LBRAK,RBRAK,EOF='INTEGER','REAL','PLUS','MINUS','MUL','DIV','(',')','EOF'
BEGIN,END,ASSIGN,ID,SEMI,DOT='BEGIN','END','=','id',';','.'
PROGRAM,VAR,COLON,COMMA,INT_CONST,REAL_CONST,INT_DIV,REAL_DIV='PROGRAM','VAR','COLON','COMMA','INTEGER_CONST','REAL_CONST','INTEGER_DIV','REAL_DIV'

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

class Program(AST):
    def __init__(self,name,block):
        self.name=name
        self.block=block

class Block(AST):
    def __init__(self,declarations,compount_statement):
        self.declarations=declarations
        self.compound_statement=compount_statement

class VarDecl(AST):
    def __init__(self,var_node,type_node):
        self.var_node=var_node
        self.type_node=type_node

class Type(AST):
    def __init__(self,token):
        self.token=token
        self.value=token.value

class Compound(AST):
    def __init__(self):
        self.children=[]
        
class Assign(AST):
    def __init__(self,left,op,right):
        self.left=left
        self.token=self.op=op
        self.right=right
    
class Var(AST):
    def __init__(self,token):
        self.token=token
        self.value=token.value

class NoOp(AST):
    pass
    
class Parser(object):
    def __init__(self,lexer):
        self.lexer=lexer
        self.current_token=self.lexer.get_next_token()
    
    def error(self):
        raise Exception('Invalid Syntax')
    
    def eat(self,token_type):
        if self.current_token.type==token_type:
            self.current_token=self.lexer.get_next_token()
        else:
            self.error()
    
    def block(self):
        declaration_nodes=self.declarations()
        compound_statement_node=self.compound_statement()
        node=Block(declaration_nodes,compound_statement_node)
        return node
    
    def declarations(self):
        declarations=[]
        if self.current_token.type==VAR:
            self.eat(VAR)
            
            while self.current_token.type==ID:
                var_decl=self.variable_declarations()
                declarations.extend(var_decl)
                self.eat(SEMI)
        
        return declarations
    
    def variable_declarations(self):
        var_nodes=[Var(self.current_token)]
        self.eat(ID)
        
        while self.current_token.type==COMMA:
            self.eat(COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(ID)
        
        self.eat(COLON)
        
        type_node=self.type_spec()
        var_declarations=[VarDecl(var_node,type_node) for var_node in var_nodes]
        
        return var_declarations
    
    def type_spec(self):
        token=self.current_token
        if self.current_token.type==INT:
            self.eat(INT)
        else:
            self.eat(REAL)
        node=Type(token)
        return node           
    
    def program(self):
        self.eat(PROGRAM)
        var_node=self.variable()
        prog_name=var_node.value
        self.eat(SEMI)
        block_node=self.block()
        program_node=Program(prog_name,block_node)
        self.eat(DOT)
        return program_node
    
    def compound_statement(self):
        self.eat(BEGIN)
        nodes=self.statement_list()
        self.eat(END)
        
        root=Compound()
        for node in nodes:
            root.children.append(node)
        return root

    def statement_list(self):
        node=self.statement()
        results=[node]
        
        while self.current_token.type==SEMI:
            self.eat(SEMI)
            results.append(self.statement())
        if self.current_token.type==ID:
            self.error()
        
        return results
    
    def statement(self):
        if self.current_token.type==BEGIN:
            node=self.compound_statement()
        elif self.current_token.type==ID:
            node=self.assignment_statement()
        else:
            node=self.empty()
        return node
    
    def assignment_statement(self):
        left=self.variable()
        token=self.current_token
        self.eat(ASSIGN)
        right=self.expr()
        node=Assign(left,token,right)
        return node
    
    def variable(self):
        node=Var(self.current_token)
        self.eat(ID)
        return node
    
    def empty(self):
        return NoOp()
    
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
        elif token.type==INT_CONST:
            self.eat(INT_CONST)
            return Num(token)
        elif token.type==REAL_CONST:
            self.eat(REAL_CONST)
            return Num(token)
        elif token.type==LBRAK:
            self.eat(LBRAK)
            node=self.expr()
            self.eat(RBRAK)
            return node
        else:
            node=self.variable()
            return node
    
    def term(self):
        node=self.factor()
        while self.current_token.type in (MUL,INT_DIV,REAL_DIV):
            token=self.current_token
            if token.type==MUL:
                self.eat(MUL)
            elif token.type==INT_DIV:
                self.eat(INT_DIV)
            elif token.type==REAL_DIV:
                self.eat(REAL_DIV)
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
        node=self.program()
        if self.current_token.type!=EOF:
            self.error()
        return node
from Utils.lexer_pascal import ErrorCode,TokenType,ParserError

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

class Param(AST):
    def __init__(self, var_node,type_node):
        self.var_node=var_node
        self.type_node=type_node 

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

class ProcedureDecl(AST):
    def __init__(self, proc_name,params,block_node):
        self.proc_name=proc_name
        self.params=params
        self.block_node=block_node

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

class ProcedureCall(AST):
    def __init__(self,proc_name,actual_params,token):
        self.proc_name=proc_name
        self.actual_params=actual_params
        self.token=token
        self.proc_symbol=None
    
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
    
    def error(self,error_code,token):
        raise ParserError(error_code=error_code,token=token,message=f"{error_code.value} -> {token}")
    
    def eat(self,token_type):
        if self.current_token.type==token_type:
            self.current_token=self.lexer.get_next_token()
        else:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN,token=self.current_token)
    
    def block(self):
        declaration_nodes=self.declarations()
        compound_statement_node=self.compound_statement()
        node=Block(declaration_nodes,compound_statement_node)
        return node
    
    def declarations(self):
        declarations=[]
        while self.current_token.type==TokenType.VAR:
            self.eat(TokenType.VAR)
            while self.current_token.type==TokenType.ID:
                var_decl=self.variable_declarations()
                declarations.extend(var_decl)
                self.eat(TokenType.SEMI)
        while self.current_token.type==TokenType.PROCEDURE:
            proc_decl=self.procedure_declaration()
            declarations.append(proc_decl)
        
        return declarations

    def procedure_declaration(self):
        self.eat(TokenType.PROCEDURE)
        proc_name=self.current_token.value
        self.eat(TokenType.ID)
        params=[]
        
        if self.current_token.type==TokenType.LBRAK:
            self.eat(TokenType.LBRAK)
            params=self.formal_parameter_list()
            self.eat(TokenType.RBRAK)
        
        self.eat(TokenType.SEMI)
        block_node=self.block()
        proc_decl=ProcedureDecl(proc_name,params,block_node)
        self.eat(TokenType.SEMI)
        return proc_decl
    
    def formal_parameter_list(self):
        if not self.current_token.type==TokenType.ID:
            return []
        
        param_nodes=self.formal_parameters()
        
        while self.current_token.type==TokenType.SEMI:
            self.eat(TokenType.SEMI)
            param_nodes.extend(self.formal_parameters())
            
        return param_nodes
    
    def formal_parameters(self):
        param_nodes=[]
        param_tokens=[self.current_token]
        self.eat(TokenType.ID)
        while self.current_token.type==TokenType.COMMA:
            self.eat(TokenType.COMMA)
            param_tokens.append(self.current_token)
            self.eat(TokenType.ID)
        
        self.eat(TokenType.COLON)
        type_node=self.type_spec()
        
        for param_token in param_tokens:
            param_node=Param(Var(param_token),type_node)
            param_nodes.append(param_node)
        return param_nodes
            
    def variable_declarations(self):
        var_nodes=[Var(self.current_token)]
        self.eat(TokenType.ID)
        
        while self.current_token.type==TokenType.COMMA:
            self.eat(TokenType.COMMA)
            var_nodes.append(Var(self.current_token))
            self.eat(TokenType.ID)
        
        self.eat(TokenType.COLON)
        
        type_node=self.type_spec()
        var_declarations=[VarDecl(var_node,type_node) for var_node in var_nodes]
        
        return var_declarations
    
    def type_spec(self):
        token=self.current_token
        if self.current_token.type==TokenType.INT:
            self.eat(TokenType.INT)
        else:
            self.eat(TokenType.REAL)
        node=Type(token)
        return node           
    
    def program(self):
        self.eat(TokenType.PROGRAM)
        var_node=self.variable()
        prog_name=var_node.value
        self.eat(TokenType.SEMI)
        block_node=self.block()
        program_node=Program(prog_name,block_node)
        self.eat(TokenType.DOT)
        return program_node
    
    def compound_statement(self):
        self.eat(TokenType.BEGIN)
        nodes=self.statement_list()
        self.eat(TokenType.END)
        
        root=Compound()
        for node in nodes:
            root.children.append(node)
        return root

    def statement_list(self):
        node=self.statement()
        results=[node]
        
        while self.current_token.type==TokenType.SEMI:
            self.eat(TokenType.SEMI)
            results.append(self.statement())
        
        return results
    
    def statement(self):
        if self.current_token.type==TokenType.BEGIN:
            node=self.compound_statement()
        elif self.current_token.type==TokenType.ID and self.lexer.current_char=='(':
            node=self.proccall_statement()
        elif self.current_token.type==TokenType.ID:
            node=self.assignment_statement()
        else:
            node=self.empty()
        return node
    
    def assignment_statement(self):
        left=self.variable()
        token=self.current_token
        self.eat(TokenType.ASSIGN)
        right=self.expr()
        node=Assign(left,token,right)
        return node
    
    def proccall_statement(self):
        token=self.current_token
        proc_name=self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.LBRAK)
        
        actual_params=[]
        if self.current_token.type!=TokenType.COLON:
            node=self.expr()
            actual_params.append(node)
        while self.current_token.type==TokenType.COMMA:
            self.eat(TokenType.COMMA)
            node=self.expr()
            actual_params.append(node)

        self.eat(TokenType.RBRAK)
        node=ProcedureCall(proc_name=proc_name,actual_params=actual_params,token=token)
        return node    
    def variable(self):
        node=Var(self.current_token)
        self.eat(TokenType.ID)
        return node
    
    def empty(self):
        return NoOp()
    
    def factor(self):
        token=self.current_token
        if token.type==TokenType.PLUS:
            self.eat(TokenType.PLUS)
            node=UnaryOp(token,self.factor())
            return node
        elif token.type==TokenType.MINUS:
            self.eat(TokenType.MINUS)
            node=UnaryOp(token,self.factor())
            return node
        elif token.type==TokenType.INT_CONST:
            self.eat(TokenType.INT_CONST)
            return Num(token)
        elif token.type==TokenType.REAL_CONST:
            self.eat(TokenType.REAL_CONST)
            return Num(token)
        elif token.type==TokenType.LBRAK:
            self.eat(TokenType.LBRAK)
            node=self.expr()
            self.eat(TokenType.RBRAK)
            return node
        else:
            node=self.variable()
            return node
    
    def term(self):
        node=self.factor()
        while self.current_token.type in (TokenType.MUL,TokenType.INT_DIV,TokenType.FLOAT_DIV):
            token=self.current_token
            if token.type==TokenType.MUL:
                self.eat(TokenType.MUL)
            elif token.type==TokenType.INT_DIV:
                self.eat(TokenType.INT_DIV)
            elif token.type==TokenType.FLOAT_DIV:
                self.eat(TokenType.FLOAT_DIV)
            node=BinOp(left=node,op=token,right=self.factor())
        return node
    
    def expr(self):
        node=self.term()
        while self.current_token.type in (TokenType.PLUS,TokenType.MINUS):
            token=self.current_token
            if token.type==TokenType.PLUS:
                self.eat(TokenType.PLUS)
            else:
                self.eat(TokenType.MINUS)
            node=BinOp(left=node,op=token,right=self.term())
        return node
    
    def parse(self):
        node=self.program()
        if self.current_token.type!=TokenType.EOF:
            self.error(error_code=ErrorCode.UNEXPECTED_TOKEN,token=self.current_token)
        return node
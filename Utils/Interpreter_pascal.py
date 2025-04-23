from Utils.lexer_pascal import ErrorCode,TokenType
from Utils.callstack_pascal import CallStack,ActivationRecord,ARType

class NodeVisitor(object):
    def visit(self,node):
        method_name='visit_'+type(node).__name__
        visitor=getattr(self,method_name,self.generic_visit)
        return visitor(node)
    def generic_visit(self,node):
        raise Exception(f'No visit_{type(node).__name__} method')

class Interpreter(NodeVisitor):
    def __init__(self,tree):
        self.tree=tree
        self.call_stack=CallStack()
    
    def visit_BinOp(self,node):
        if node.op.type==TokenType.PLUS:
            return self.visit(node.left)+self.visit(node.right)
        elif node.op.type==TokenType.MINUS:
            return self.visit(node.left)-self.visit(node.right)
        elif node.op.type==TokenType.MUL:
            return self.visit(node.left)*self.visit(node.right)
        elif node.op.type==TokenType.INT_DIV:
            return self.visit(node.left)//self.visit(node.right)
        elif node.op.type==TokenType.FLOAT_DIV:
            return float(self.visit(node.left))/float(self.visit(node.right))
    
    def visit_UnaryOp(self,node):
        op=node.op.type
        if op==TokenType.PLUS:
            return +self.visit(node.expr)
        else:
            return -self.visit(node.expr)
    
    def visit_Compound(self,node):
        for child in node.children:
            self.visit(child)
    
    def visit_NoOp(self,node):
        pass
    
    def visit_ProcedureCall(self,node):
        proc_name=node.proc_name
        ar=ActivationRecord(name=proc_name,type=ARType.PROCEDURE,nesting_level=2)
        proc_symbol=node.proc_symbol
        formal_params=proc_symbol.params
        actual_params=node.actual_params
        for param_symbol,argument_node in zip(formal_params,actual_params):
            ar[param_symbol.name]=self.visit(argument_node)

        self.call_stack.push(ar)
        
        self.log(f'ENTER: PROCEDURE {proc_name}')
        self.log(str(self.call_stack))
        
        self.visit(proc_symbol.block_ast)
        
        self.log(f'LEAVE: PROCEDURE {proc_name}')
        self.log(str(self.call_stack))
        
        self.call_stack.pop()

    def visit_Assign(self,node):
        var_name=node.left.value
        var_value=self.visit(node.right)
        ar=self.call_stack.peek()
        ar[var_name]=var_value
    
    def visit_Var(self,node):
        var_name=node.value
        ar=self.call_stack.peek()
        val=ar.get(var_name)
        return val
    
    def log(self,msg):
        print(msg)
    
    def visit_Program(self,node):
        program_name=node.name
        
        ar=ActivationRecord(name=program_name,type=ARType.PROGRAM,nesting_level=1)
        self.call_stack.push(ar)
        
        self.log(str(self.call_stack))
        self.visit(node.block)
        
        self.log(f'LEAVE: PROGRAM {program_name}')
        self.log(str(self.call_stack))
        
        self.call_stack.pop()
        
    
    def visit_ProcedureDecl(self,node):
        pass
    
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
        tree=self.tree
        if tree is None:
            return ''
        return self.visit(tree)

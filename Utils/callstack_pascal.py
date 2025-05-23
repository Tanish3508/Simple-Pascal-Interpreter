from enum import Enum

class CallStack:
    def __init__(self):
        self._records=[]
    
    def push(self,ar):
        self._records.append(ar)
    
    def pop(self):
        return self._records.pop()
    
    def peek(self):
        return self._records[-1]
    
    def __str__(self):
        s='\n'.join(repr(ar) for ar in reversed(self._records))
        s=f'CALL STACK\n{s}\n'
        return s
    
    __repr__=__str__
    
class ARType(Enum):
    PROGRAM='PROGRAM'
    PROCEDURE='PROCEDURE'

class ActivationRecord:
    def __init__(self, name,type,nesting_level):
        self.name=name
        self.type=type
        self.nesting_level=nesting_level
        self.members={}
    
    def __setitem__(self,key,value):
        self.members[key]=value
    
    def __getitem__(self,key):
        return self.members[key]
    
    def get(self,key):
        return self.members.get(key)

    def __str__(self):
        lines=[f'{self.nesting_level}: {self.type} {self.name}']
        
        for name,val in self.members.items():
            lines.append(f'   {name:<20}: {val}')
        
        s='\n'.join(lines)
        return s
    
    __repr__=__str__
    

        
        
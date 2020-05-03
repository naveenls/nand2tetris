# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 11:27:09 2019

@author: HP
"""
import sys
import Syntax_Analyzer
import VMwriter
import SymbolTable

static_count=0
total_count=0

op_set={"+", "-","*", "/", "&amp;", "|", "&lt;", "&gt;", "="}
find_kind = {'arg': 'argument','static': 'static','var': 'local','field': 'this'}
ARITHMETIC={
    '+': 'add',
    '-': 'sub',
    '=': 'eq',
    '&gt;': 'gt',
    '&lt;': 'lt',
    '&amp;': 'and',
    '|': 'or'
}

ARITHMETIC_UNARY={
    '-': 'neg',
    '~': 'not'
}

keyword = {"class", "constructor", "function", "method", "field", \
					"static", "var", "int", "char", "boolean", "void", \
					"true", "false", "this", "null", "let", "do", "if", \
					"else", "while", "return"}

class Compile:
    if_index=-1
    while_index=-1
    def __init__(self,Inputfile,vmFile):
        #self.parser=Syntax_Analyzer.Parser(Inputfile,open(Inputfile[:-5]+"1.xml",'w'))
        #self.tokens=self.parser.Tokenize.tokens
        self.errFile=open(Inputfile[:-4]+"err",'w')
        Syntax_Analyzer.Parser(Inputfile,open(Inputfile[:-4]+"xml",'w'),self.errFile)
        self.xmlFile=open(Inputfile[:-4]+"xml",'r')
        self.tokens=[]
        self.initTokens()
        self.vm=VMwriter.VMWriter(vmFile)
        self.next_command=-1
        self.symbol_table=SymbolTable.SymbolTable()
        self.curr_insuct=None
        self.compileClass()
        self.errFile.close()
        
    def initTokens(self):
        for string in self.xmlFile:
            self.tokens.append(string)
            
    @property
    def getNextToken(self):
        self.next_command+=1
        self.curr_ins=self.tokens[self.next_command]
        return self.curr_ins
    
    @property
    def peekToken(self):
        self.curr_ins=self.tokens[self.next_command+1]
        return self.curr_ins
    
    def _getNextToken(self,n):
        self.next_command+=n
        
    def go_back(self):
        self.next_command=self.next_command-1
        
    @property
    def curr_ins(self):
        return self.curr_insuct
    
    @curr_ins.setter
    def curr_ins(self,string):
        string=string.split()
        if len(string)==1:
            string[0]=string[0][1:-1]
            string.append(None)

        elif len(string)==3:
            string[0]=string[0][1:-1]
            string.pop()
        else:
            string[0]=string[0][1:-1]
            str_var=""
            for i in range(len(string)-2,0,-1):
                str_var=string[i]+' '+str_var
                string.pop()
            string[1]=str_var
        self.curr_insuct=string
        
    def compileClass(self):
        self._getNextToken(2)
        self.className=self.getNextToken[1]
        #print('class name',self.className)
        self.getNextToken
        while self.peekToken[0]=="ClassVarDec":
            self.compileClassVarDec()
        
        while self.peekToken[0]=="subroutineDec":
            self.compileSubroutine()
            
        self.getNextToken
        self.vm.close()
        
    def compileClassVarDec(self):
        self.getNextToken
        kind=self.getNextToken[1]
        varType=self.getNextToken[1]
        variable=self.getNextToken[1]
        #print('Class var',kind,varType,variable)
        self.symbol_table.add(variable,varType,kind)
        
        while self.peekToken[1]!=';':
            self.getNextToken
            variable=self.getNextToken[1]
            #print('Class var',variable)
            self.symbol_table.add(variable,varType,kind)
        
        self._getNextToken(2)
    
    def compileSubroutine(self):
        self.getNextToken
        subroutine_type=self.getNextToken[1]
        self.getNextToken
        subroutine_name=self.getNextToken[1]
        
        self.symbol_table.initSubroutine()
        #print('Subroutine Name',subroutine_type,subroutine_name)
        if subroutine_type=="method":
            self.symbol_table.add('instamce', subroutine_type, 'arg')
        
        self.getNextToken
        self.compileParamList()
        self.getNextToken
        self._getNextToken(2)
        
        while self.peekToken[0]=="varDec":
            self.compileVarDec()
            
        function_name = '{}.{}'.format(self.className, subroutine_name)
        num_locals = self.symbol_table.var
        
        self.vm.writeFunction(function_name,num_locals)
        
        if subroutine_type=="constructor":
            num_fields = self.symbol_table.field
            self.vm.writePush('constant', num_fields)
            self.vm.writeCall('Memory.alloc',1)
            self.vm.writePop('pointer',0)
        
        elif subroutine_type=="method":
            self.vm.writePush('argument',0)
            self.vm.writePop('pointer',0)
        
        self.compileStatements()
        self._getNextToken(3)
        
    def compileParamList(self):
        self.getNextToken
        
        if self.peekToken[0]=="/parameterList":
            self.getNextToken
            return 
        else:
            type = self.getNextToken[1]
            name = self.getNextToken[1]
            self.symbol_table.add(name, type, 'arg')
            
        while self.peekToken[1]!=None:
            self.getNextToken
            type = self.getNextToken[1]
            name = self.getNextToken[1]
            self.symbol_table.add(name, type, 'arg')
        self.getNextToken
    
    def compileVarDec(self):
        self._getNextToken(2)
        type=self.getNextToken[1]
        name=self.getNextToken[1]
        self.symbol_table.add(name, type,'var')
        
        while self.peekToken[1]!=';':
            self.getNextToken
            name=self.getNextToken[1]
            #print('var',name)
            self.symbol_table.add(name, type,'var')
        
        self._getNextToken(2)
        
    def compileStatements(self):
        self.getNextToken
        while self.peekToken[0] in {"letStatement","ifStatement","whileStatement","doStatement","returnStatement"}:
            method = getattr(self, "compile"+self.peekToken[0][:-9], lambda: "InvalidStmt")
            method()
        
        self.getNextToken
        
    def compilelet(self):
        self._getNextToken(2)
        varName=self.getNextToken[1]
        var_kind =self.symbol_table.kind(varName)
        if var_kind==None:
            self.errFile.write("Declaration error: "+varName+" undeclared")
            self.errFile.close()
            sys.exit()
        var_index=self.symbol_table.index(varName)
        if self.peekToken[1]=='[':
            self.getNextToken
            self.compileExpressions()
            self.getNextToken
            self.vm.writePush(find_kind[var_kind], var_index)
            
            self.vm.writeArithmetic('add')
            self.vm.writePop('temp',0)
            
            self.getNextToken
            self.compileExpressions()
            self.getNextToken
        
            self.vm.writePush('temp',0)
            self.vm.writePop('pointer',1)
            self.vm.writePop('that',0)
            
        else:
            self.getNextToken
            self.compileExpressions()
            self.getNextToken
            self.vm.writePop(find_kind[var_kind], var_index)
        
        self.getNextToken
    
    def compilewhile(self):
        Compile.while_index+=1
        while_index = Compile.while_index
        self.vm.writeLabel('WHILE{}.{}\n'.format(self.className,while_index))
        
        self._getNextToken(3)
        self.compileExpressions()
        self.vm.writeArithmetic('not')
        self._getNextToken(2)
        
        self.vm.writeIf('WHILE_END{}.{}\n'.format(self.className,while_index))
        self.compileStatements() 
        self.vm.writeGoto('WHILE{}.{}\n'.format(self.className,while_index))
        self.vm.writeLabel('WHILE_END{}.{}\n'.format(self.className,while_index))
                
        self._getNextToken(2)
    
    def compiledo(self):
        self._getNextToken(2)
        self.compileSubroutineCall()
        self.vm.writePop('temp', 0)
        self._getNextToken(2)
        
    def compileif(self):
        Compile.if_index += 1
        if_index = Compile.if_index
        
        self._getNextToken(3)
        self.compileExpressions()
        self._getNextToken(2)

        self.vm.writeIf('IF_TRUE{}.{}\n'.format(self.className,if_index))
        self.vm.writeGoto('IF_FALSE{}.{}\n'.format(self.className,if_index))
        self.vm.writeLabel('IF_TRUE{}.{}\n'.format(self.className,if_index))
        self.compileStatements()
        self.vm.writeGoto('IF_END{}.{}\n'.format(self.className,if_index))
        
        self.getNextToken
        self.vm.writeLabel('IF_FALSE{}.{}\n'.format(self.className,if_index))
        
        if self.peekToken[1]=="else":
            self._getNextToken(2)
            self.compileStatements()
            self.getNextToken
            
        self.vm.writeLabel('IF_END{}.{}\n'.format(self.className,if_index))
        self.getNextToken
    
    def compilereturn(self):
        self._getNextToken(2)
        if self.peekToken[1]!=';':
            self.compileExpressions()
        else:
            self.vm.writePush('constant', 0)
        
        self.vm.writeReturn()
        self._getNextToken(2)
        
    def compileSubroutineCall(self):
        identifier=self.getNextToken[1]
        number_args=0
        if self.peekToken[1]=='.':
            self.getNextToken
            subroutine_name=self.getNextToken[1]
            type = self.symbol_table.type(identifier)
            
            if type!=None:
                instance_kind = self.symbol_table.kind(identifier)
                instance_index = self.symbol_table.index(identifier)
                self.vm.writePush(find_kind[instance_kind],instance_index)
                function_name = '{}.{}'.format(type, subroutine_name)
                number_args += 1
            else:
                class_name = identifier
                function_name = '{}.{}'.format(class_name, subroutine_name)
            
        elif self.peekToken[1]=='(':
            function_name = '{}.{}'.format(self.className,identifier)
            number_args += 1
            
            self.vm.writePush('pointer',0)
            
        self.getNextToken
        number_args+=self.compileExpressionList()
        self.getNextToken
        self.vm.writeCall(function_name,number_args)
        
    def compileExpressions(self):
        self.getNextToken
        self.compileTerm()
        
        while self.peekToken[1] in op_set:
            operation=self.getNextToken[1]
            self.compileTerm()
            
            if operation in ARITHMETIC.keys():
                self.vm.writeArithmetic(ARITHMETIC[operation])
            elif operation=='*':
                self.vm.writeCall('Math.multiply', 2)
            elif operation=='/':
                self.vm.writeCall('Math.divide', 2)
        
        self.getNextToken
        
    def compileExpressionList(self):
        number_args=0
        self.getNextToken
        
        if self.peekToken[0]!="/expressionList":
            self.compileExpressions()
            number_args+=1
        
        while self.peekToken[0]!="/expressionList":
            number_args+=1
            self.getNextToken
            self.compileExpressions()
            
        self.getNextToken
        return number_args
    
    def compileTerm(self):
        self.getNextToken
        next_token=self.getNextToken
        next_token_type=next_token[0]
        next_token=next_token[1]
        #print(next_token_type)
        if next_token_type=="integerConstant":
            self.vm.writePush('constant', next_token)
        elif next_token_type=="stringConstant":
            self.vm.writePush('constant', len(next_token))
            self.vm.writeCall('String.new', 1)
            for char in next_token:
              self.vm.writePush('constant', ord(char))
              self.vm.writeCall('String.appendChar', 2)
        elif next_token_type=="keyword":
            if next_token == 'this':
              self.vm.writePush('pointer',0)
            else:
              self.vm.writePush('constant',0)
              if next_token == 'true':
                self.vm.writeArithmetic('not')
        elif next_token=='(':
            self.compileExpressions()
            self.getNextToken
        elif next_token in ARITHMETIC_UNARY.keys():
            self.compileTerm()
            self.vm.writeArithmetic(ARITHMETIC_UNARY[next_token])
        else:
            nextNexttoken=self.getNextToken[1]
            if nextNexttoken=='[':
                arr_var=next_token
                self.compileExpressions()
                self.getNextToken
                
                array_kind=self.symbol_table.kind(arr_var)
                if array_kind==None:
                    self.errFile.write("Declaration error: "+arr_var+" undeclared")
                    self.errFile.close()
                    sys.exit()
                array_index=self.symbol_table.index(arr_var)
                self.vm.writePush(find_kind[array_kind], array_index)
                self.vm.writeArithmetic('add')
                self.vm.writePop('pointer',1)
                self.vm.writePush('that',0)
                
            elif nextNexttoken=='(' or nextNexttoken=='.':
                self.go_back()
                self.go_back()
                self.compileSubroutineCall()
            else:
                var_kind=self.symbol_table.kind(next_token)
                if var_kind==None:
                    self.errFile.write("Declaration error: "+next_token+" undeclared")
                    self.errFile.close()
                    sys.exit()
                var_index = self.symbol_table.index(next_token)
                self.vm.writePush(find_kind[var_kind], var_index)
                self.go_back()
        self.getNextToken
    
if __name__=="__main__":
    files=sys.argv
    for filename in files:
        if filename.endswith(".jack"): 
            vmFile=open(filename[:-4]+"vm",'w')
            JackFile=open(filename,'r')
            Compile(filename,vmFile)
            JackFile.close()
            vmFile.close()
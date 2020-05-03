# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 00:35:32 2019

@author: HP
"""

import Tokenizer
import sys

lexical_elements = {"keyword", "symbol", "integerConstant", "stringConstant", "identifier"}

keyword = {"class", "constructor", "function", "method", "field", \
					"static", "var", "int", "char", "boolean", "void", \
					"true", "false", "this", "null", "let", "do", "if", \
					"else", "while", "return"}

dataType={'void','int','char','boolean'}

symbol = {'(', ')', '[', ']', '{', '}', ',', ';', '=', '.', '+', '-', '*', \
		 '/', '&', '|', '~', '<', '>'}

keywordConstant={"true","false","null","this"}

op_set={"+", "-","*", "/", "&amp;", "|", "&lt;", "&gt;", "="}

symbol_set={'<':"&lt;", '>':"&gt;", '\'':"&quot;", '&':"&amp;"}

function_key={"constructor","function","method"}
var_key={"field","static"}
statement_type={'let','if','while','do','return'}
ARITHMETIC_UNARY={
    '-': 'neg',
    '~': 'not'
}

err_check={'identifier','dataType','sub_call'}
        
class Parser:
    err_File=None
    def __init__(self,inputFile,outputFile,errFile):
        self.Tokenize=Tokenizer.Tokenizer(inputFile)
        Parser.err_File=errFile
        self._next_command=-1
        outputFile.write(self.compileClass())
        outputFile.close()
      
    @property
    def getNextToken(self):
        self._next_command+=1
        return self.Tokenize.tokens[self._next_command][1]
    
    def go_back(self):
        self._next_command=self._next_command-1
    
    @staticmethod
    def formatTemplate(tokenType,element,string):
        #print(element,string,tokenType)
        if string==None:
            pass
        elif string in err_check:
            if string=='identifier':
                if not element.isidentifier():
                    Parser.err_File.write("ERROR: Expecting <identifier> but "+element)
                    Parser.err_File.close()
                    sys.exit()
            elif string=='dataType':
                if not element in dataType:
                    if element in keyword:
                        Parser.err_File.write("ERROR: "+element)
                    else:
                        Parser.err_File.write("ERROR: Expecting <keyword> but "+element)
                    Parser.err_File.close()
                    sys.exit()
            else:
                if element!='.' and element!='(':
                    if element in symbol:
                        Parser.err_File.write("ERROR: "+element)
                    else:
                        Parser.err_File.write("ERROR: Expecting <symbol> but "+element)
                    Parser.err_File.close()
                    sys.exit()
        elif element!=string:
            if tokenType=="keyword":
                if element in keyword:
                    Parser.err_File.write("ERROR: "+element)
                else:
                    Parser.err_File.write("ERROR: Expecting <keyword> but "+element)
            elif tokenType=="symbol":
                if element in symbol:
                    Parser.err_File.write("ERROR: "+element)
                else:
                    Parser.err_File.write("ERROR: Expecting <symbol> but "+element)
            Parser.err_File.close()
            sys.exit()
        if element in symbol_set:
            element=symbol_set[element]
        return "<{}> {} </{}>\n".format(tokenType,element,tokenType)
    
    @staticmethod
    def compileTypeVar(Vartype,variable):
        write_xml=""
        if Vartype in keyword:
            write_xml+=Parser.formatTemplate("keyword",Vartype,'dataType')
        else:
            write_xml+=Parser.formatTemplate("identifier",Vartype,'identifier')
        write_xml+=Parser.formatTemplate("identifier",variable,'identifier')
        return write_xml
    
    def compileClass(self):
        write_xml=""
        write_xml+="<class>\n"
        write_xml+=Parser.formatTemplate("keyword",self.getNextToken,"class")
        write_xml+=Parser.formatTemplate("identifier",self.getNextToken,'identifier')
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,'{')
        next_token=self.getNextToken
        
        while next_token=="static" or next_token=="field":
            self.go_back()
            write_xml+=self.compileClassVarDec()
            next_token=self.getNextToken
        
        while next_token in function_key:
            self.go_back()
            write_xml+=self.compileSubroutineDec()
            next_token=self.getNextToken
            
        write_xml+=Parser.formatTemplate("symbol",next_token,'}')
        write_xml+="</class>\n"
        return write_xml
        
    def compileClassVarDec(self):
        write_xml=""
        write_xml+="<ClassVarDec>\n"
        write_xml+=Parser.formatTemplate("keyword",self.getNextToken,None)
        varType=self.getNextToken;
        variable=self.getNextToken;
        write_xml+=Parser.compileTypeVar(varType,variable)
        next_token=self.getNextToken;
        
        while next_token==',':
            write_xml+=Parser.formatTemplate("symbol",next_token,None)
            write_xml+=Parser.formatTemplate("identifier",self.getNextToken,'identifier')
            next_token=self.getNextToken
        
        write_xml+=Parser.formatTemplate("symbol",next_token,';')
        write_xml+="</ClassVarDec>\n"
        return write_xml
    
    def compileSubroutineDec(self):
        write_xml=""
        write_xml+="<subroutineDec>\n"
        write_xml+=Parser.formatTemplate("keyword",self.getNextToken,None)
        varType=self.getNextToken;
        variable=self.getNextToken;
        write_xml+=Parser.compileTypeVar(varType,variable)
        write_xml+=self.compileParamList()
        write_xml+=self.compileSubroutineBody()
        write_xml+="</subroutineDec>\n"
        return write_xml
    
    def compileParamList(self):
        write_xml=""
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,'(')
        write_xml+="<parameterList>\n"
        nextToken = self.getNextToken
        if nextToken==")":
            write_xml+="</parameterList>\n"
            write_xml+=Parser.formatTemplate("symbol", nextToken,None)
            return write_xml
        varType=nextToken
        variable=self.getNextToken
        write_xml+=Parser.compileTypeVar(varType,variable)
        nextToken=self.getNextToken
        
        while nextToken==',':
            write_xml+=Parser.formatTemplate("symbol",nextToken,',')
            varType=self.getNextToken
            variable=self.getNextToken
            write_xml+=Parser.compileTypeVar(varType,variable)
            nextToken=self.getNextToken
        write_xml+="</parameterList>\n"
        write_xml+=Parser.formatTemplate("symbol",nextToken,')')
        return write_xml
    
    def compileSubroutineBody(self):
        write_xml=""
        write_xml+="<subroutineBody>\n"
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,'{')
        next_token=self.getNextToken
        
        while next_token=="var":
            self.go_back()
            write_xml+=self.compileVarDec()
            next_token=self.getNextToken
        
        self.go_back()
        write_xml+=self.compileStatements()
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,'}')
        write_xml+="</subroutineBody>\n"
        return write_xml
    
    def compileVarDec(self):
        write_xml=""
        write_xml+="<varDec>\n"
        write_xml+=Parser.formatTemplate("keyword",self.getNextToken,'var')
        varType=self.getNextToken
        variable=self.getNextToken
        write_xml+=Parser.compileTypeVar(varType,variable)
        nextToken=self.getNextToken
        
        while nextToken==',':
            write_xml+=Parser.formatTemplate("symbol",nextToken,None)
            variable=self.getNextToken
            write_xml+=Parser.formatTemplate("identifier",variable,'identifier')
            nextToken=self.getNextToken
        
        write_xml+=Parser.formatTemplate("symbol",nextToken,';')
        write_xml+="</varDec>\n"
        return write_xml
        
    def compileStatements(self):
        write_xml=""
        write_xml+="<statements>\n"
        next_token=self.getNextToken
        
        while next_token in statement_type:
            self.go_back()
            method = getattr(self, "compile"+next_token, lambda: "InvalidStmt")
            write_xml+=method()
            next_token=self.getNextToken
            
        self.go_back()
        write_xml+="</statements>\n"
        return write_xml
    
    def compilelet(self):
        write_xml=""
        write_xml+="<letStatement>\n"
        write_xml+=Parser.formatTemplate("keyword",self.getNextToken,None)
        write_xml+=Parser.formatTemplate("identifier",self.getNextToken,'identifier')
        next_token=self.getNextToken
        if next_token=='[':
            write_xml+=Parser.formatTemplate("symbol",next_token,None)
            write_xml+=self.compileExpressions()
            write_xml+=Parser.formatTemplate("symbol",self.getNextToken,']')
            next_token=self.getNextToken
        
        write_xml+=Parser.formatTemplate("symbol",next_token,'=')
        write_xml+=self.compileExpressions()
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,';')
        write_xml+="</letStatement>\n"
        return write_xml
    
    def compilewhile(self):
        write_xml=""
        write_xml+="<whileStatement>\n"
        write_xml+=Parser.formatTemplate("keyword",self.getNextToken,None)
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,'(')
        write_xml+=self.compileExpressions()
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,')')
        
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,'{')
        write_xml+=self.compileStatements()
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,'}')
        write_xml+="</whileStatement>\n"
        return write_xml
    
    def compiledo(self):
        write_xml=""
        write_xml+="<doStatement>\n"
        write_xml+=Parser.formatTemplate("keyword",self.getNextToken,None)
        write_xml+=self.compileSubroutineCall()
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,';')
        write_xml+="</doStatement>\n"
        return write_xml
       
    def compileif(self):
        write_xml=""
        write_xml+="<ifStatement>\n"
        write_xml+=Parser.formatTemplate("keyword",self.getNextToken,None)
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,'(')
        write_xml+=self.compileExpressions()
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,')')
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,'{')
        write_xml+=self.compileStatements()
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,'}')
        next_token=self.getNextToken
        
        if next_token=="else":
            write_xml+=Parser.formatTemplate("keyword",next_token,None)
            write_xml+=Parser.formatTemplate("symbol",self.getNextToken,'{')
            write_xml+=self.compileStatements()
            write_xml+=Parser.formatTemplate("symbol",self.getNextToken,'}')
        else:
            self.go_back()
            
        write_xml+="</ifStatement>\n"
        return write_xml
    
    def compilereturn(self):
        write_xml=""
        write_xml+="<returnStatement>\n"
        write_xml+=Parser.formatTemplate("keyword",self.getNextToken,None)
        next_token=self.getNextToken
        if next_token==';':
            write_xml+=Parser.formatTemplate("symbol",next_token,None)
        else:
            self.go_back()
            write_xml+=self.compileExpressions()
            write_xml+=Parser.formatTemplate("symbol",self.getNextToken,';')
            
        write_xml+="</returnStatement>\n"
        return write_xml
    
    def compileSubroutineCall(self):
        write_xml=""
        write_xml+=Parser.formatTemplate("identifier",self.getNextToken,"identifier")
        next_token=self.getNextToken
        write_xml+=Parser.formatTemplate("symbol",next_token,'sub_call')
        if next_token=='.':
            write_xml+=Parser.formatTemplate("identifier",self.getNextToken,"identifier")
            write_xml+=Parser.formatTemplate("symbol",self.getNextToken,'(')
        write_xml+=self.compileExpressionList()
        write_xml+=Parser.formatTemplate("symbol",self.getNextToken,')')
        return write_xml
        
    def compileExpressions(self):
        write_xml=""
        write_xml+="<expression>\n"
        write_xml+=self.compileTerm()
        next_token=self.getNextToken
        while next_token in op_set:
            write_xml+=Parser.formatTemplate("symbol",next_token,None)
            write_xml+=self.compileTerm()
            next_token=self.getNextToken
        self.go_back()
        write_xml+="</expression>\n"
        return write_xml
        
    def compileExpressionList(self):
        write_xml=""
        write_xml+="<expressionList>\n"
        next_token=self.getNextToken
        if next_token==")":
            self.go_back()
            write_xml+="</expressionList>\n"
            return write_xml
        self.go_back()
        write_xml+=self.compileExpressions()
        next_token=self.getNextToken
        if next_token!=",":
            self.go_back()
            write_xml+="</expressionList>\n"
            return write_xml
        while next_token==",":
            write_xml+=Parser.formatTemplate("symbol",next_token,None)
            write_xml+=self.compileExpressions()
            next_token=self.getNextToken
        self.go_back()
        write_xml+="</expressionList>\n"
        return write_xml
    
    def compileTerm(self):
        write_xml=""
        write_xml+="<term>\n"
        next_token=self.getNextToken
        if next_token.isnumeric():
            write_xml+=Parser.formatTemplate("integerConstant",next_token,None)
        elif next_token[0]=='"' and next_token[-1]=='"':
            write_xml+=Parser.formatTemplate("stringConstant",next_token[1:-1],None)
        elif next_token in keywordConstant:
            write_xml+=Parser.formatTemplate("keyword",next_token,None)
        elif next_token=='(':
            write_xml+=Parser.formatTemplate("symbol",next_token,None)
            write_xml+=self.compileExpressions()
            write_xml+=Parser.formatTemplate("symbol",self.getNextToken,')')
        elif next_token in ARITHMETIC_UNARY:
            write_xml+=Parser.formatTemplate("symbol",next_token,None)
            write_xml+=self.compileTerm()
        else:
            nextNexttoken=self.getNextToken
            if nextNexttoken=='[':
                write_xml+=Parser.formatTemplate("identifier",next_token,'identifier')
                write_xml+=Parser.formatTemplate("symbol",nextNexttoken,None)
                write_xml+=self.compileExpressions()
                write_xml+=Parser.formatTemplate("symbol",self.getNextToken,']')
            elif nextNexttoken=='(' or nextNexttoken=='.':
                self.go_back()
                self.go_back()
                write_xml+=self.compileSubroutineCall()
            else:
                write_xml+=Parser.formatTemplate("identifier",next_token,"identifier")
                self.go_back()
        write_xml+="</term>\n"
        return write_xml
    

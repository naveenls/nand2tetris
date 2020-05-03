# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 17:11:49 2019

@author: HP
"""

import re

_KEYWORDS = ["class", "method", "function", "constructor", "int", "boolean",
             "char", "void", "var", "static", "field", "let", "do", "if",
             "else", "while", "return", "true", "false", "null", "this"]

_SYMBOLS = ["{", "}", "[", "]", "(", ")", ".", ",", ";", "+", "-", "*", "/",
            "&", "|", "<", ">", "=", "~"]

symbol_set={'<':"&lt;", '>':"&gt;", '\'':"&quot;", '&':"&amp;"}

def _is_keyword(word):
    return word in _KEYWORDS


def _is_symbol(symbol):
    return symbol in _SYMBOLS


def _is_string(word):
    string_regex = re.compile('^\".*\"$')
    return not not string_regex.match(word)


def _is_int(word):
    int_regex = re.compile('^\d+$')
    return not not int_regex.match(word)


def _is_identifier(word):
    identifier_regex = re.compile('^\w+$')
    return not not identifier_regex.match(word)


def _get_token(word):

    if _is_keyword(word):
        return "keyword", word

    elif _is_symbol(word):
        if word in symbol_set:
            return "symbol",symbol_set[word]
        return "symbol", word

    elif _is_string(word):
        return "stringConstant", word

    elif _is_int(word):
        return "integerConstant", word

    elif _is_identifier(word):
        return "identifier", word

def _slice_command(line):
    stripped_line = line.strip()
    if not stripped_line:
        return ''
    is_comment = stripped_line[0] == '*' or stripped_line[0:2] in ['//', '/*']
    if is_comment:
        return ''
    without_comments = line.split('//')[0]
    identifier_regex = '\w+'
    integer_regex = '\d+'
    string_regex = '\".*\"'
    keyword_regex = ('class|method|function|constructor|int|boolean|char|void|'
                     'var|static|field|let|do|if|else|while|return|true|false|'
                     'null|this')
    
    symbol_regex = '{|}|\[|\]|\(|\)|\.|,|;|\+|-|\*|\/|&|\||<|>|=|~'
    composed_regex = r'({}|{}|{}|{}|{})'.format(identifier_regex,
                                                integer_regex,
                                                string_regex,
                                                keyword_regex,
                                                symbol_regex)
    return re.finditer(composed_regex, without_comments)

class Tokenizer:
    def __init__(self,filepath):
        self.file=open(filepath,'r')
        self.xmlfile=open(filepath[:-5]+"T.xml",'w')
        self.tokens=[]
        self.xmlfile.write("<tokens>\n")
        for syntax in self.file:
            command = _slice_command(syntax)
            if not command:
                continue
            for word in command:
                word = word.group().strip()
                if not word:
                    continue
                _type,_token=_get_token(word)
                self.tokens.append([_type,_token])
                _token=_token.replace("\"", "")
                self.xmlfile.write("<{}> {} </{}>\n".format(_type,_token,_type))
        self.xmlfile.write("</tokens>")
        self.xmlfile.close()
            

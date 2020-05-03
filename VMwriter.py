# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 15:47:55 2019

@author: HP
"""

class VMWriter:
  def __init__(self, output_file):
    self.output = output_file

  def writePush(self, segment, index):
    self.output.write('push {} {}\n'.format(segment.lower(), index))

  def writePop(self, segment, index):
    self.output.write('pop {} {}\n'.format(segment.lower(), index))

  def writeArithmetic(self, command):
    self.output.write(command.lower() + '\n')

  def writeLabel(self, label):
    self.output.write('label {}\n'.format(label))

  def writeGoto(self, label):
    self.output.write('goto {}\n'.format(label))

  def writeIf(self, label):
    self.output.write('if-goto {}\n'.format(label))

  def writeCall(self, name, nArgs):
    self.output.write('call {} {}\n'.format(name, nArgs))

  def writeFunction(self, name, nLocals):
    self.output.write('function {} {}\n'.format(name, nLocals))

  def writeReturn(self):
    self.output.write('return\n')

  def close(self):
    self.output.close()

  def write(self, stuff):
    self.output.write(stuff)
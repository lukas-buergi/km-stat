#!/usr/bin/env python3
# coding=utf-8
from anytree import NodeMixin
class a(NodeMixin):
  def __init__(self, lala, parent=None):
    super().__init__()
    self.parent=parent
    self.lala = lala

p=a(1)
c=a(2,p)

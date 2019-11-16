# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 15:04:13 2019

@author: HARSHIT
"""

import clingo
import numpy as np
mapofworld = None
class Map:
    def __init__(self):
        self.size = 5
        self.solution = None
        
        ctl = clingo.Control()
        ctl.load("NewMap.lp")
        ctl.ground([("base", [])])
        ctl.solve(on_model=self.__on_model)
    
    def __on_model(self, m):
        maps = np.array([['None' for i in range(self.size)] for j in range(self.size)], dtype=object)
        for atom in m.symbols(atoms=True):
            if atom.name == "at" and len(atom.arguments) == 2:
                
                x, y = str(atom.arguments[0]), str(atom.arguments[1])
                if maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] == 'None':
                    maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] = y
                else:
                    maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] = maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] + ' + ' + y
            
            if atom.name == "tile" and len(atom.arguments) == 3:
                x, y, z = str(atom.arguments[0]), str(atom.arguments[1]), str(atom.arguments[2])
                
                if maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] == 'None':
                    maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] = z + y
                else:
                    maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] = maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] + ' + ' + z + y
        
        global mapofworld
        mapofworld = np.array([[str(maps[i, j]) for i in range(self.size)] for j in range(self.size)])          
        
Map()

print(mapofworld)
            
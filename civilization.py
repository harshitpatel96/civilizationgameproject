# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 15:04:13 2019

@author: Harshit Patel, Sagar Bajaj
"""

import clingo
import numpy as np
from random import randint
from astropy.table import Table


dictofmaps = dict()
index = 0
randomindex = 0
hiddenmap = None
strm = None
mapofworld = None
probrand = 100000 # this is number of models which we want our asp to output 
n = 0# for randomness in map
listofn = [] # list to save indices of last five maps
moves = {'red':[], 'green':[]}

class Map:
    def __init__(self, mapsize):
        self.size = mapsize
        self.solution = None
        ctl = clingo.Control()
        ctl.load("MAPs.lp")
        
        global n, listofn, probrand, randomindex
        n = randint(1, probrand)
        randomindex = randint(0, n)
        
        ctl.configuration.solve.models = n
        ctl.ground([('base', [])])
        ctl.solve(on_model=self.__on_model)
    
    def __on_model(self, m):
        global strm, dictofmaps, index
        dictofmaps[index] = m
        index += 1
        global randomindex
        
        if randomindex == index-1: 
            maps = np.array([['None' for i in range(self.size)] for j in range(self.size)], dtype=object)
            for atom in dictofmaps[randomindex].symbols(atoms=True):
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
                
                if atom.name == 'move' and len(atom.arguments) == 3:
                    x, y, z = str(atom.arguments[0]), str(atom.arguments[1]), str(atom.arguments[2])
                    
                    global moves
                    if x == 'red':
                        moves[x].append(z)
                    elif x == 'green':
                        moves[x].append(z)
                        
                    
                    
        
            global mapofworld
            mapofworld = np.array([[str(maps[i, j]) for i in range(self.size)] for j in range(self.size)])          
            

def main():
    mapsize = int(input('Enter map size: '))
    f = open('mapgenerator.lp', 'r')
    contents = f.read()
    f.close()
    f = open('MAPs.lp', 'w+')
    f.write("#const width=" + str(mapsize) + '.\n')
    f.close()
    f = open('MAPs.lp', 'a')
    f.write(contents)
    f.close()
    Map(mapsize)

    mowN = np.array([['None' for i in range(mapofworld.shape[0])] for j in range(mapofworld.shape[1])], dtype=object)
    playerpos = [(i, j) for i in range(mapofworld.shape[0]) for j in range(mapofworld.shape[1]) if 'player' in mapofworld[i, j]]
        
    for i in playerpos:
        mowN[i[0],i[1]] = mapofworld[i[0], i[1]]
        try:
            mowN[i[0]+1,i[1]] = mapofworld[i[0]+1, i[1]]
        except:
            None
        try:
            if i[0]-1 >= 0:
                mowN[i[0]-1,i[1]] = mapofworld[i[0]-1, i[1]]
        except:
            None
        try:
            mowN[i[0]+1,i[1]+1] = mapofworld[i[0]+1, i[1]+1]
        except:
            None
        try:
            if i[1]-1 >= 0:
                mowN[i[0]+1,i[1]-1] = mapofworld[i[0]+1, i[1]-1]
        except:
            None
        try:
            if i[0]-1 >= 0 and i[1]-1 >= 0:
                mowN[i[0]-1,i[1]-1] = mapofworld[i[0]-1, i[1]-1]
        except:
            None
        try:
            if i[0]-1 >= 0:
                mowN[i[0]-1,i[1]+1] = mapofworld[i[0]-1, i[1]+1]
        except:
            None
        try:
            mowN[i[0],i[1]+1] = mapofworld[i[0], i[1]+1]
        except:
            None
        try:
            if i[1]-1 >= 0:
                mowN[i[0],i[1]-1] = mapofworld[i[0], i[1]-1]
        except:
            None
    global hiddenmap       
    hiddenmap = np.array([[str(mowN[i, j]) for i in range(mapofworld.shape[0])] for j in range(mapofworld.shape[1])])
    
    # Logic to print hidden map on screen in readable format
    col = [' ']
    for i in range(mapsize):
        col.append(str(i))

    cols = tuple(col)
    
    datatype = tuple('S25' for i in range(mapsize+1))


    rows = []
    for i in range(mapsize):
        temp = []
        for j in range(mapsize):
            if j == 0:
                temp.append(str(i))
            temp.append(mapofworld[j, i])
        rows.append(tuple(temp))
    
    t = Table(names=cols, dtype=datatype)
    for i in range(mapsize):
        t.add_row(rows[i])
    
    print("----------------------------------CURRENT MAP-----------------------------------")
    print(t)
    global moves
    print('\n--------------------------------Available Moves--------------------------------')
    print('Red player can move to one of the following tiles on the map:\n')
    print(moves['red'])
    print('Green player can move to one of the following tiles on the map:\n')
    print(moves['green'])
    
    
    
if __name__ == "__main__":
    main()

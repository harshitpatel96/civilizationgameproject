# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 15:04:13 2019

@author: Harshit Patel, Sagar Bajaj
"""

""" Clingo for map generation
numpy for map visualization
random to create randomness in map
astropy to create tables for visualizing on screen"""

import clingo
import numpy as np
from random import randint
from astropy.table import Table

dictofmaps = dict() #unused # generating random models using clingo api is tough, so we generate "n" number of maps at a time and pick one at random. We store all 
index = 0 # current model index
randomindex = 0 # random index, the one that we would use as our model
hiddenmap = None # stores hidden map of the world 
strm = None # unused
mapofworld = None # stores full map of the world(nothing hidden)
probrand = 100000 # this is number of models which we want our asp to output 
n = 0# for randomness in map
listofn = [] # unused # list to save indices of last five maps
moves = {'red':[], 'green':[]} # two players


""" Map class, generates map and stores it in a numpy array"""
class Map:
    # takes mapsize as an input argument and generates map of that size
    def __init__(self, mapsize):
        self.size = mapsize
        self.solution = None
        ctl = clingo.Control()
        ctl.load("MAPs.lp") # load clingo file
        
        global n, listofn, probrand, randomindex #load global variables
        n = randint(1, probrand) # the number of models that we want our asp to generate
        randomindex = randint(0, n) # index for the model that we want to select
        
        ctl.configuration.solve.models = n # solve n models parameter
        ctl.ground([('base', [])]) # grounding
        ctl.solve(on_model=self.__on_model) # solver
    
    # model takes one input argument that is solved models and runs through each of them one by one but process only the last one
    def __on_model(self, m):
        global dictofmaps, index # load global variables
        #dictofmaps[index] = m
        
        global randomindex # get randomindex
        
        if randomindex == index-1: # when our index is equal to the randomindex (i.e. the model we want to choose) than proceed
            maps = np.array([['None' for i in range(self.size)] for j in range(self.size)], dtype=object) # an empty array of object datatype to store strings of variable length
            
            # loop through all the atoms in model (atoms are nothing but predicates)
            for atom in m.symbols(atoms=True):
                
                # copy atom arguments to other variables (we do this because we cannot print or display them directly because they are of type clingo.symbol)
                if atom.name == "at" and len(atom.arguments) == 2:    
                    x, y = str(atom.arguments[0]), str(atom.arguments[1]) # copy arguments of atom in other variables
                    if maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] == 'None': # (when initially there is nothing at the given location(first argument of at predicate), then store y(second argument, the object at that location) at that location on numpy array)
                        maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] = y
                    else: # (if there is something already over there then in addition to the old thing add y to it (case where a tile contains a player and obviously it would contain a location))
                        maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] = maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] + ' + ' + y
                
                # do this if atom is "tile" predicate (tile are nothing but "at" predicates that contains location and color info for players and resources)
                if atom.name == "tile" and len(atom.arguments) == 3:
                    
                    # copy atom arguments to other variables (we do this because we cannot print or display them directly because they are of type clingo.symbol)
                    x, y, z = str(atom.arguments[0]), str(atom.arguments[1]), str(atom.arguments[2])
                    
                    # (when initially there is nothing at the given location(first argument of at predicate), then store y(second argument, the object at that location) at that location on numpy array)
                    if maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] == 'None':
                        maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] = z + y
                    # (if there is something already over there then in addition to the old thing add y to it (case where a tile contains a player and obviously it would contain a location))
                    else:
                        maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] = maps[int(x[1:x.find(',')]), int(x[x.find(',')+1:x.find(')')])] + ' + ' + z + y
                
                # get initial available moves for each player
                if atom.name == 'move' and len(atom.arguments) == 3:
                    x, y, z = str(atom.arguments[0]), str(atom.arguments[1]), str(atom.arguments[2])
                    
                    global moves # call global variable move
                    if x == 'red': # for red player
                        moves[x].append(z)
                    elif x == 'green': # for green player
                        moves[x].append(z)
                        
                    
                    
        
            global mapofworld # call global variable mapofworld to store our current map
            mapofworld = np.array([[str(maps[i, j]) for i in range(self.size)] for j in range(self.size)])          
        index += 1 # increase index by 1
    

# main function of the program
def main():
    
    mapsize = int(input('Enter map size: ')) # get map size from user
    f = open('mapgenerator.lp', 'r') # open mapgenerator file in read mode(which contains clingo code for map generation)
    contents = f.read() # read its contents and store them to a local variable
    f.close() # close the file
    f = open('MAPs.lp', 'w+') # open a MAPs.lp file if it is not there then create one and open it in write mode
    f.write("#const width=" + str(mapsize) + '.\n') # add a line which defines size of map in clingo syntax
    f.close() # close the file
    f = open('MAPs.lp', 'a') # open the same file in append mode
    f.write(contents) # add contents to it
    f.close() # close it
    
    Map(mapsize) # run map function
    
    # call global variable hiddenmap
    global hiddenmap
    
    # hiddenmap is as it name suggests a  hidden map that shows only 3x3 matrix locations around a player when started (player is at center of that 3x3 matrix)
    hiddenmap = np.array([['None' for i in range(mapofworld.shape[0])] for j in range(mapofworld.shape[1])], dtype=object)
    # playerpos stores current position of player from mapofworld
    playerpos = [(i, j) for i in range(mapofworld.shape[0]) for j in range(mapofworld.shape[1]) if 'player' in mapofworld[i, j]]
        
    # for each player's position show 3x3 matrix around the player's position
    for i in playerpos:
        hiddenmap[i[0],i[1]] = mapofworld[i[0], i[1]]
        try:
            hiddenmap[i[0]+1,i[1]] = mapofworld[i[0]+1, i[1]]
        except:
            None
        try:
            if i[0]-1 >= 0:
                hiddenmap[i[0]-1,i[1]] = mapofworld[i[0]-1, i[1]]
        except:
            None
        try:
            hiddenmap[i[0]+1,i[1]+1] = mapofworld[i[0]+1, i[1]+1]
        except:
            None
        try:
            if i[1]-1 >= 0:
                hiddenmap[i[0]+1,i[1]-1] = mapofworld[i[0]+1, i[1]-1]
        except:
            None
        try:
            if i[0]-1 >= 0 and i[1]-1 >= 0:
                hiddenmap[i[0]-1,i[1]-1] = mapofworld[i[0]-1, i[1]-1]
        except:
            None
        try:
            if i[0]-1 >= 0:
                hiddenmap[i[0]-1,i[1]+1] = mapofworld[i[0]-1, i[1]+1]
        except:
            None
        try:
            hiddenmap[i[0],i[1]+1] = mapofworld[i[0], i[1]+1]
        except:
            None
        try:
            if i[1]-1 >= 0:
                hiddenmap[i[0],i[1]-1] = mapofworld[i[0], i[1]-1]
        except:
            None
   
    # Logic to print hidden map on screen in readable format
    col = [' '] # initial column with empty string (just a space)
    for i in range(mapsize):
        col.append(str(i)) # add all the numbers in range [0, mapsize)

    cols = tuple(col) # convert it to tuple and store it in cols
    
    datatype = tuple('S25' for i in range(mapsize+1)) # datatype is a tuple that contains datatype for each tuple (S25 mins string of length 25, anything above that would cut off)


    rows = [] # empty list of rows to be added in table
    for i in range(mapsize): # run a loop over over the range of mapsize
        temp = [] # temperory list
        for j in range(mapsize): # run a loop over map size (basically it is mapsize X mapsize loop)
            if j == 0: # initially when j is 0 then append i as a string which is nothing but row number
                temp.append(str(i))
            temp.append(hiddenmap[j, i]) # also add element of hiddenmap at that location
        rows.append(tuple(temp)) # append tuple of it to rows list
    
    t = Table(names=cols, dtype=datatype) # feed table generator with columns and datatypes
    for i in range(mapsize): # add all the wros
        t.add_row(rows[i])
    
    print("----------------------------------CURRENT MAP-----------------------------------")
    print(t) # print table t which is nothing but hiddenmap
    global moves
    print('\n--------------------------------Available Moves--------------------------------')
    print('Red player can move to one of the following tiles on the map:\n')
    print(moves['red']) # print moves of red player
    print('Green player can move to one of the following tiles on the map:\n')
    print(moves['green']) # print moves of green player
    
# run main on start
if __name__ == "__main__":
    main()

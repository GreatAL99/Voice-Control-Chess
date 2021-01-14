

#####################################################################################
# Equipe 1 : BENSAID Mohammed 
# 		      GUESSOUSS Imad 
# 		       KARDIDI Abdellatif
#####################################################################################



#Import dependencies:
import pygame #Game library
from pygame.locals import * #For useful variables..for eg QUIT
import copy #Library used to make exact copies of lists.
import pickle #Library used to store dictionaries in a text file and read them from text files.
import random #Used for making random selections
from collections import defaultdict #Used for giving dictionary values default data types.
from collections import Counter #For counting elements in a list effieciently.
import threading #To allow for AI to think simultaneously while the GUI is coloring the board.
import time
import speech_recognition as sr

play_sound=True


class GamePosition:
    def __init__(self,board,player,castling_rights,EnP_Target,HMC,history = {}):

        self.c=Commands()
        self.board = board
        self.player = player
        self.EnP = EnP_Target
        self.castling = castling_rights
        self.HMC = HMC

        self.history = history
        
    def getboard(self):
        return self.board
    def setboard(self,board):
        self.board = board
    def getplayer(self):
        return self.player
    def setplayer(self,player):
        self.player = player
    def getCastleRights(self):
        return self.castling
    def setCastleRights(self,castling_rights):
        self.castling = castling_rights
    def getEnP(self):
        return self.EnP
    def setEnP(self, EnP_Target):
        self.EnP = EnP_Target
    def getHMC(self):
        return self.HMC
    def setHMC(self,HMC):
        self.HMC = HMC
    def checkRepition(self):

        return any(value>=3 for value in self.history.values())
    def addtoHistory(self,position):
       
        key = self.c.pos2key(position)
        
        self.history[key] = self.history.get(key,0) + 1
    def gethistory(self):
        return self.history
    def clone(self):

        clone = GamePosition(copy.deepcopy(self.board),    #  Independent copy
                             self.player,
                             copy.deepcopy(self.castling), #  Independent copy
                             self.EnP,
                             self.HMC)
        return clone


class Shades:

    def __init__(self,image,coord):
        self.image = image
        self.pos = coord
    def getInfo(self):
        return [self.image,self.pos]


class Piece:

    def __init__(self,pieceinfo,chess_coord,square_width, square_height):
       
        piece = pieceinfo[0]
        color = pieceinfo[1]
        
        if piece=='K':
            index = 0
        elif piece=='Q':
            index = 1
        elif piece=='B':
            index = 2
        elif piece == 'N':
            index = 3
        elif piece == 'R':
            index = 4
        elif piece == 'P':
            index = 5
        left_x =square_width*index
        if color == 'w':
            left_y = 0
        else:
            left_y = square_height
        
        self.pieceinfo = pieceinfo

        self.subsection = (left_x,left_y,square_width,square_height)
       
        self.chess_coord = chess_coord
        self.pos = (-1,-1)

    def getInfo(self):
        return [self.chess_coord, self.subsection,self.pos]
    def setpos(self,pos):
        self.pos = pos
    def getpos(self):
        return self.pos
    def setcoord(self,coord):
        self.chess_coord = coord


class Commands:

    def isOccupied(self,board,x,y):

        if board[int(y)][int(x)] == 0:
            return False
        return True

    def isOccupiedby(self,board,x,y,color):
        
        if board[y][x] == 0:
            return False
        if board[y][x][1] == color[0]:
            return True
        return False

    def filterbyColor(self,board,listofTuples,color):
        filtered_list = []
        for pos in listofTuples:
            x = pos[0]
            y = pos[1]
            if x>=0 and x<=7 and y>=0 and y<=7 and not self.isOccupiedby(board,x,y,color):
                filtered_list.append(pos)
        return filtered_list

    def lookfor(self,board,piece):
        
        listofLocations = []
        for row in range(8):
            for col in range(8):
                if board[row][col] == piece:
                    x = col
                    y = row
                    listofLocations.append((x,y))
        return listofLocations

    def isAttackedby(self,position,target_x,target_y,color):
        
        board = position.getboard()
        # Get b from black or w from white
        color = color[0]
        # Get all the squares that are attacked by the particular side:
        listofAttackedSquares = []
        for x in range(8):
            for y in range(8):
                if board[y][x]!=0 and board[y][x][1]==color:
                    listofAttackedSquares.extend(
                        self.findPossibleSquares(position,x,y,True)) #The true argument
                    # prevents infinite recursion.
        # Check if the target square falls under the range of attack by the specified
        # side, and return it:
        return (target_x,target_y) in listofAttackedSquares             

    def findPossibleSquares(self,position,x,y,AttackSearch=False):
       
        # Get individual component data from the position object:
        board = position.getboard()
        player = position.getplayer()
        castling_rights = position.getCastleRights()
        EnP_Target = position.getEnP()

        # In case something goes wrong:
        piece = board[y][x][0] #Pawn, rook, etc.
        color = board[y][x][1] #w or b.

        # Have the complimentary color stored for convenience:
        enemy_color = self.opp(color)
        listofTuples = [] #Holds list of attacked squares.

        if piece == 'P': #The piece is a pawn.
            if color=='w': #The piece is white
                if not self.isOccupied(board,x,y-1) and not AttackSearch:
                    #The piece immediately above is not occupied, append it.
                    listofTuples.append((x,y-1))
                    
                    if y == 6 and not self.isOccupied(board,x,y-2):
                        #If pawn is at its initial position, it can move two squares.
                        listofTuples.append((x,y-2))
                
                if x!=0 and self.isOccupiedby(board,x-1,y-1,'black'):
                    #The piece diagonally up and left of this pawn is a black piece.
                    #Also, this is not an 'a' file pawn (left edge pawn)
                    listofTuples.append((x-1,y-1))
                if x!=7 and self.isOccupiedby(board,x+1,y-1,'black'):
                    #The piece diagonally up and right of this pawn is a black one.
                    #Also, this is not an 'h' file pawn.
                    listofTuples.append((x+1,y-1))
                if EnP_Target!=-1: #There is a possible en pasant target:
                    if EnP_Target == (x-1,y-1) or EnP_Target == (x+1,y-1):
                        #We're at the correct location to potentially perform en
                        #passant:
                        listofTuples.append(EnP_Target)
                
            elif color=='b': #The piece is black, same as above but opposite side.
                if not self.isOccupied(board,x,y+1) and not AttackSearch:
                    listofTuples.append((x,y+1))
                    if y == 1 and not self.isOccupied(board,x,y+2):
                        listofTuples.append((x,y+2))
                if x!=0 and self.isOccupiedby(board,x-1,y+1,'white'):
                    listofTuples.append((x-1,y+1))
                if x!=7 and self.isOccupiedby(board,x+1,y+1,'white'):
                    listofTuples.append((x+1,y+1))
                if EnP_Target == (x-1,y+1) or EnP_Target == (x+1,y+1):
                    listofTuples.append(EnP_Target)

        elif piece == 'R': #The piece is a rook.
            for i in [-1,1]:
               
                kx = x #This variable stores the x coordinate being looked at.
                while True: #loop till break.
                    kx = kx + i #Searching left or right
                    if kx<=7 and kx>=0: #Making sure we're still in board.
                        
                        if not self.isOccupied(board,kx,y):
                            listofTuples.append((kx,y))
                        else:
                            if self.isOccupiedby(board,kx,y,enemy_color):
                                listofTuples.append((kx,y))
                            break
                            
                    else: #We have exceeded the limits of the board
                        break
            for i in [-1,1]:
                ky = y
                while True:
                    ky = ky + i 
                    if ky<=7 and ky>=0: 
                        if not self.isOccupied(board,x,ky):
                            listofTuples.append((x,ky))
                        else:
                            if self.isOccupiedby(board,x,ky,enemy_color):
                                listofTuples.append((x,ky))
                            break
                    else:
                        break
            
        elif piece == 'N': #The piece is a knight.
            
            for dx in [-2,-1,1,2]:
                if abs(dx)==1:
                    sy = 2
                else:
                    sy = 1
                for dy in [-sy,+sy]:
                    listofTuples.append((x+dx,y+dy))
            #Filter the list of tuples so that only valid squares exist.
            listofTuples = self.filterbyColor(board,listofTuples,color)
        elif piece == 'B': # A bishop.

            for dx in [-1,1]: #Allow two directions in x.
                for dy in [-1,1]: #Similarly, up and down for y.
                    kx = x #These varibales store the coordinates of the square being
                           #observed.
                    ky = y
                    while True: #loop till broken.
                        kx = kx + dx #change x
                        ky = ky + dy #change y
                        if kx<=7 and kx>=0 and ky<=7 and ky>=0:
                            if not self.isOccupied(board,kx,ky):
                                #The square is empty, so our bishop can go there.
                                listofTuples.append((kx,ky))
                            else:

                                if self.isOccupiedby(board,kx,ky,enemy_color):
                                    listofTuples.append((kx,ky))

                                break    
                        else:

                            break
        
        elif piece == 'Q': #A queen
            
            board[y][x] = 'R' + color
            list_rook = self.findPossibleSquares(position,x,y,True)
            board[y][x] = 'B' + color
            list_bishop = self.findPossibleSquares(position,x,y,True)
            listofTuples = list_rook + list_bishop
            board[y][x] = 'Q' + color
        elif piece == 'K': # A king!
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    listofTuples.append((x+dx,y+dy))
            listofTuples = self.filterbyColor(board,listofTuples,color)
            if not AttackSearch:
                #Kings can potentially castle:
                right = castling_rights[player]
                #Kingside
                if (right[0] and #has right to castle
                board[y][7]!=0 and #The rook square is not empty
                board[y][7][0]=='R' and #There is a rook at the appropriate place
                not self.isOccupied(board,x+1,y) and #The square on its right is empty
                not self.isOccupied(board,x+2,y) and #The second square beyond is also empty
                not self.isAttackedby(position,x,y,enemy_color) and #The king isn't under atack
                not self.isAttackedby(position,x+1,y,enemy_color) and #Or the path through which
                not self.isAttackedby(position,x+2,y,enemy_color)):#it will move
                    listofTuples.append((x+2,y))
                #Queenside
                if (right[1] and #has right to castle
                board[y][0]!=0 and #The rook square is not empty
                board[y][0][0]=='R' and #The rook square is not empty
                not self.isOccupied(board,x-1,y)and #The square on its left is empty
                not self.isOccupied(board,x-2,y)and #The second square beyond is also empty
                not self.isOccupied(board,x-3,y) and #And the one beyond.
                not self.isAttackedby(position,x,y,enemy_color) and #The king isn't under atack
                not self.isAttackedby(position,x-1,y,enemy_color) and #Or the path through which
                not self.isAttackedby(position,x-2,y,enemy_color)):#it will move
                    listofTuples.append((x-2,y)) #Let castling be an option.

        if not AttackSearch:
            new_list = []
            for tupleq in listofTuples:
                x2 = int(tupleq[0])
                y2 = int(tupleq[1])
                temp_pos = position.clone()
                self.makemove(temp_pos,x,y,x2,y2)
                if not self.isCheck(temp_pos,color):
                    new_list.append(tupleq)
            listofTuples = new_list
        return listofTuples

    def makemove(self,position,x,y,x2,y2):

        x = int(x)
        y = int(y)
        x2 = int(x2)
        y2 = int(y2)
        board = position.getboard()
        piece = board[y][x]
        if piece==0:
            return
        piece=piece[0]
        color = board[y][x][1]
        player = position.getplayer()
        castling_rights = position.getCastleRights()
        EnP_Target = position.getEnP()
        half_move_clock = position.getHMC()
        if self.isOccupied(board,x2,y2) or piece=='P':
            half_move_clock = 0
        else:
            half_move_clock += 1

        #Make the move:
        board[y2][x2] = board[y][x]
        board[y][x] = 0

        if piece == 'K':
            castling_rights[player] = [False,False]
            if abs(x2-x) == 2:
                if color=='w':
                    l = 7
                else:
                    l = 0
                
                if x2>x:
                        board[l][5] = 'R'+color
                        board[l][7] = 0
                else:
                        board[l][3] = 'R'+color
                        board[l][0] = 0
        #Rook:
        if piece=='R':
            if x==0 and y==0:
                castling_rights[1][1] = False
            elif x==7 and y==0:
                castling_rights[1][0] = False
            elif x==0 and y==7:
                castling_rights[0][1] = False
            elif x==7 and y==7:
                castling_rights[0][0] = False
        #Pawn:
        if piece == 'P':
            if EnP_Target == (x2,y2):
                if color=='w':
                    board[y2+1][x2] = 0
                else:
                    board[y2-1][x2] = 0
            if abs(y2-y)==2:
                EnP_Target = (x,(y+y2)/2)
            else:
                EnP_Target = -1
            if y2==0:
                board[y2][x2] = 'Qw'
            elif y2 == 7:
                board[y2][x2] = 'Qb'
        else:
            EnP_Target = -1
        player = 1 - player
        position.setplayer(player)
        position.setCastleRights(castling_rights)
        position.setEnP(EnP_Target)
        position.setHMC(half_move_clock)
    def opp(self,color):

        color = color[0]
        if color == 'w':
            oppcolor = 'b'
        else:
            oppcolor = 'w'
        return oppcolor
    def isCheck(self,position,color):

        board = position.getboard()
        color = color[0]
        enemy = self.opp(color)
        piece = 'K' + color
        x,y = self.lookfor(board,piece)[0]
        return self.isAttackedby(position,x,y,enemy)
    def isCheckmate(self,position,color=-1):

        if color==-1:
            return self.isCheckmate(position,'white') or self.isCheckmate(position,'b')
        color = color[0]
        if self.isCheck(position,color) and self.allMoves(position,color)==[]:
                return True
        return False
    def isStalemate(self,position):

        player = position.getplayer()
        if player==0:
            color = 'w'
        else:
            color = 'b'
        if not self.isCheck(position,color) and self.allMoves(position,color)==[]:

            return True
        return False
    def getallpieces(self,position,color):

        board = position.getboard()
        listofpos = []
        for j in range(8):
            for i in range(8):
                if self.isOccupiedby(board,i,j,color):
                    listofpos.append((i,j))
        return listofpos
    def allMoves(self,position, color):
        if color==1:
            color = 'white'
        elif color ==-1:
            color = 'black'
        color = color[0]
        listofpieces = self.getallpieces(position,color)
        moves = []
        for pos in listofpieces:
            targets = self.findPossibleSquares(position,pos[0],pos[1])
            for target in targets:
                 moves.append([pos,target])
        return moves
    def pos2key(self,position):

        board = position.getboard()
        boardTuple = []
        for row in board:
            boardTuple.append(tuple(row))
        boardTuple = tuple(boardTuple)
        rights = position.getCastleRights()
        tuplerights = (tuple(rights[0]),tuple(rights[1]))
        key = (boardTuple,position.getplayer(),
               tuplerights)
        return key



class AI:

    def __init__(self):
        self.c=Commands()
        
    def negamax( self,position,depth,alpha,beta,colorsign,bestMoveReturn,openings,searched,root=True):
        if root:
            key = self.c.pos2key(position)
            if key in openings:
                bestMoveReturn[:] = random.choice(openings[key])
                return
        
        if depth==0:
            return colorsign*self.evaluate(position)
        moves = self.c.allMoves(position, colorsign)
        if moves==[]:
            return colorsign*self.evaluate(position)
        if root:
            bestMove = moves[0]
        bestValue = -100000
        for move in moves:
            newpos = position.clone()
            self.c.makemove(newpos,move[0][0],move[0][1],move[1][0],move[1][1])
            key = self.c.pos2key(newpos)

            if key in searched:
                value = searched[key]
            else:
                value = -self.negamax(newpos,depth-1, -beta,-alpha,-colorsign,[],openings,searched,False)
                searched[key] = value
            if value>bestValue:
                bestValue = value
                if root:
                    bestMove = move
            alpha = max(alpha,value)
            if alpha>=beta:

                break
        if root:
            searched = {}
            bestMoveReturn[:] = bestMove
            return
        return bestValue
    def evaluate(self,position):
        
        if self.c.isCheckmate(position,'white'):
            return -20000
        if self.c.isCheckmate(position,'black'):
            return 20000
        board = position.getboard()
        flatboard = [x for row in board for x in row]
        c = Counter(flatboard)
        Qw = c['Qw']
        Qb = c['Qb']
        Rw = c['Rw']
        Rb = c['Rb']
        Bw = c['Bw']
        Bb = c['Bb']
        Nw = c['Nw']
        Nb = c['Nb']
        Pw = c['Pw']
        Pb = c['Pb']

        whiteMaterial = 9*Qw + 5*Rw + 3*Nw + 3*Bw + 1*Pw
        blackMaterial = 9*Qb + 5*Rb + 3*Nb + 3*Bb + 1*Pb
        numofmoves = len(position.gethistory())
        gamephase = 'opening'
        if numofmoves>40 or (whiteMaterial<14 and blackMaterial<14):
            gamephase = 'ending'

        Dw = self.doubledPawns(board,'white')
        Db = self.doubledPawns(board,'black')
        Sw = self.blockedPawns(board,'white')
        Sb = self.blockedPawns(board,'black')
        Iw = self.isolatedPawns(board,'white')
        Ib = self.isolatedPawns(board,'black')
        evaluation1 = 900*(Qw - Qb) + 500*(Rw - Rb) +330*(Bw-Bb
                    )+320*(Nw - Nb) +100*(Pw - Pb) +-30*(Dw-Db + Sw-Sb + Iw- Ib
                    )
        evaluation2 = self.pieceSquareTable(flatboard,gamephase)
        evaluation = evaluation1 + evaluation2
        return evaluation
    def pieceSquareTable(self,flatboard,gamephase):
        #Initialize score:
        p=PieceTable()
        score = 0
        for i in range(64):
            if flatboard[i]==0:
                continue
            piece = flatboard[i][0]
            color = flatboard[i][1]
            sign = +1

            if color=='b':
                i = ((7-i)//8)*8 + i%8
                sign = -1
            if piece=='P':
                score += sign*p.pawn_table[i]
            elif piece=='N':
                score+= sign*p.knight_table[i]
            elif piece=='B':
                score+=sign*p.bishop_table[i]
            elif piece=='R':
                score+=sign*p.rook_table[i]
            elif piece=='Q':
                score+=sign*p.queen_table[i]
            elif piece=='K':

                if gamephase=='opening':
                    score+=sign*p.king_table[i]
                else:
                    score+=sign*p.king_endgame_table[i]
        return score  
    def doubledPawns(self,board,color):
        
        color = color[0]
        listofpawns = self.c.lookfor(board,'P'+color)

        repeats = 0
        temp = []
        for pawnpos in listofpawns:
            if pawnpos[0] in temp:
                repeats = repeats + 1
            else:
                temp.append(pawnpos[0])
        return repeats
    def blockedPawns(self,board,color):
        
        color = color[0]
        listofpawns = self.c.lookfor(board,'P'+color)
        blocked = 0
        #Self explanatory:
        for pawnpos in listofpawns:
            if ((color=='w' and self.c.isOccupiedby(board,pawnpos[0],pawnpos[1]-1,
                                           'black'))
                or (color=='b' and self.c.isOccupiedby(board,pawnpos[0],pawnpos[1]+1,
                                           'white'))):
                blocked = blocked + 1
        return blocked
    def isolatedPawns(self,board,color):
       
        color = color[0]
        listofpawns = self.c.lookfor(board,'P'+color)
        xlist = [x for (x,y) in listofpawns]
        isolated = 0
        for x in xlist:
            if x!=0 and x!=7:
                if x-1 not in xlist and x+1 not in xlist:
                    isolated+=1
            elif x==0 and 1 not in xlist:
                isolated+=1
            elif x==7 and 6 not in xlist:
                isolated+=1
        return isolated

#Initialize the board:

class Board:
    def __init__(self):
        self.create_board()
    
    def create_board(self):
        self.chess=[[0]*8 for i in range(8)]
        list_w=['Rw','Nw','Bw','Qw','Kw','Bw','Nw','Rw']
        list_b=['Rb','Nb','Bb','Qb','Kb','Bb','Nb','Rb']
        for i in range(2):
            for j in range (8):
                if i==0:
                    self.chess[i][j]=list_b[j]
                else:
                    self.chess[i][j]='Pb'
        for i in range(6,8):
            for j in range (8):
                if i==7:
                    self.chess[i][j]=list_w[j]
                else:
                    self.chess[i][j]='Pw'
    def getChess(self):
        return self.chess


class PieceTable:

    def __init__(self):

        self.pawn_table = [  0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
         5,  5, 10, 25, 25, 10,  5,  5,
         0,  0,  0, 20, 20,  0,  0,  0,
         5, -5,-10,  0,  0,-10, -5,  5,
         5, 10, 10,-20,-20, 10, 10,  5,
         0,  0,  0,  0,  0,  0,  0,  0]

        self.knight_table = [-50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-90,-30,-30,-30,-30,-90,-50]

        self.bishop_table = [-20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-90,-10,-10,-90,-10,-20]

        self.rook_table = [0,  0,  0,  0,  0,  0,  0,  0,
          5, 10, 10, 10, 10, 10, 10,  5,
         -5,  0,  0,  0,  0,  0,  0, -5,
         -5,  0,  0,  0,  0,  0,  0, -5,
         -5,  0,  0,  0,  0,  0,  0, -5,
         -5,  0,  0,  0,  0,  0,  0, -5,
         -5,  0,  0,  0,  0,  0,  0, -5,
          0,  0,  0,  5,  5,  0,  0,  0]

        self.queen_table = [-20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
         -5,  0,  5,  5,  5,  5,  0, -5,
          0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, 70, -5,-10,-10,-20]

        self.king_table = [-30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
         20, 20,  0,  0,  0,  0, 20, 20,
         20, 30, 10,  0,  0, 10, 30, 20]

        self.king_endgame_table = [-50,-40,-30,-20,-20,-30,-40,-50,
        -30,-20,-10,  0,  0,-10,-20,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 30, 40, 40, 30,-10,-30,
        -30,-10, 20, 30, 30, 20,-10,-30,
        -30,-30,  0,  0,  0,  0,-30,-30,
        -50,-30,-30,-30,-30,-30,-30,-50]


class GUI:

    def __init__(self):
        self.board = Board().getChess()
        self.c = Commands()
        self.a = AI()
        self.player = 0 #This is the player that makes the next move. 0 is white, 1 is black
        self.castling_rights = [[True, True],[True, True]]
        self.En_Passant_Target = -1 
        self.half_move_clock = 0 
        self.position = GamePosition(self.board,self.player,self.castling_rights,self.En_Passant_Target
                                ,self.half_move_clock)

        
        pygame.init()

        self.size = (800, 640)


        


        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Chess Game")
        self.game_icon = pygame.image.load('newMedia/ChessImage.png')
        pygame.display.set_icon(self.game_icon)

        self.media()

        self.bg = (49, 60, 43)

        self.startPage = pygame.Surface(self.size)
        self.startPage.fill(self.bg)

        self.diffPage = pygame.Surface(self.size)
        self.diffPage.fill(self.bg)



        self.selectPage = pygame.Surface(self.size)
        self.selectPage.fill(self.bg)

        self.colorPage = pygame.Surface(self.size)
        self.colorPage.fill(self.bg)

        self.buttons = {
            1: [0, 0, 800, 640],
            3: [475-275, 380-15, 150, 50],
            4: [775-275, 380-15, 150, 50]
        }

        self.diffMenu = -1
        self.select = -1
        self.level = None
        self.temp = None
        self.box = pygame.image.load('newMedia/menubg.jpg')
        self.box = pygame.transform.scale(self.box, (800, 640))
        
        clock = pygame.time.Clock()
        self.initialize()
        pygame.display.update()
        
        while not self.gameEnded:
            if self.isMenu:
                if self.isAI==-1:
                    self.startMenu()
                elif self.isAI==True:
                    if self.diffMenu == -1:
                    	self.colorsMenu()
                    	# self.diffMenu = 0

                    if self.select == 1 and self.temp == None:
                        self.selectMenu()

                if self.select == 2 :
                    self.call_board()
                    continue
                elif self.select == 3 :
                    self.call_board()
                    pygame.mixer.Sound.play(self.instructions_sound)
                    continue
                if self.temp == -1 :
                    self.call_board()
                    continue
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.gameEnded = True
                      
                        break
                    if event.type == MOUSEBUTTONUP:
                        self.onClick()
                        
                pygame.display.update()

                clock.tick(10)
                continue
           
            self.numm+=1
            if self.isAIThink and self.numm%10==0:
                self.Thinking()
                      
            for event in pygame.event.get():
                if event.type==QUIT:
                    self.gameEnded = True
                    break

                if self.chessEnded or self.isTransition or self.isAIThink:
                    continue
                if self.select<=2:
                    if not self.isDown and event.type == MOUSEBUTTONDOWN:

                        pos = pygame.mouse.get_pos()
                        if pos[0] in range(0,640) and pos[1] in range(0,640):
                            chess_coord = self.pixel_coord_to_chess(pos)
                            x = chess_coord[0]
                            y = chess_coord[1]

                            if not self.c.isOccupiedby(self.board,x,y,'wb'[self.player]):
                                continue

                            dragPiece = self.getPiece(chess_coord)
                            listofTuples = self.c.findPossibleSquares(self.position,x,y)
                            self.createShades(listofTuples)
                            if dragPiece:
                                if ((dragPiece.pieceinfo[0]=='K') and
                                    (self.c.isCheck(self.position,'white') or self.c.isCheck(self.position,'black'))):
                                    None
                                else:
                                    self.listofShades.append(Shades(self.greenbox_image,(x,y)))
                            self.isDown = True
                    if (self.isDown or self.isClicked) and event.type == MOUSEBUTTONUP:
                        self.isDown = False
                        if dragPiece:
                            dragPiece.setpos((-1,-1))
                        pos = pygame.mouse.get_pos()
                        chess_coord = self.pixel_coord_to_chess(pos)
                        x2 = chess_coord[0]
                        y2 = chess_coord[1]
                        self.isTransition = False
                        if (x,y)==(x2,y2): 
                            if not self.isClicked: 
                                self.isClicked = True
                                self.prevPos = (x,y) #Store it so next time we know the origin
                            else: 
                                x,y = self.prevPos
                                if (x,y)==(x2,y2): 
                                    self.isClicked = False
                                    self.createShades([])
                                else:
                                    if self.c.isOccupiedby(self.board,x2,y2,'wb'[self.player]):

                                        self.isClicked = True
                                        self.prevPos = (x2,y2) #Store it
                                    else:
                                        self.isClicked = False
                                        self.createShades([])
                                        self.isTransition = True #Possibly if the move was valid.


                        if not (x2,y2) in listofTuples:
                            self.isTransition = False
                            continue
                        if self.isRecord:
                            key = self.c.pos2key(self.position)
                            if [(x,y),(x2,y2)] not in self.openings[key]:
                                self.openings[key].append([(x,y),(x2,y2)])

                        self.c.makemove(self.position,x,y,x2,y2)
                        self.prevMove = [x,y,x2,y2]
                        self.player = self.position.getplayer()
                        if self.player == 1:
                             pygame.mixer.Sound.play(self.piece_sound)
                        else:
                             pygame.mixer.Sound.play(self.piece_sound)
                        self.position.addtoHistory(self.position)
                        HMC = self.position.getHMC()
                        if HMC>=100 or self.c.isStalemate(self.position) or self.position.checkRepition():
                            self.isDraw = True
                            self.chessEnded = True
                        if self.c.isCheckmate(self.position,'white'):
                            self.winner = 'b'
                            self.chessEnded = True
                        if self.c.isCheckmate(self.position,'black'):
                            self.winner = 'w'
                            self.chessEnded = True
                        if self.isAI and not self.chessEnded:
                            if self.player==0:
                                colorsign = 1
                            else:
                                colorsign = -1
                            self.bestMoveReturn = []
                            self.move_thread = threading.Thread(target = self.a.negamax,
                                        args = (self.position,self.level,-1000000,1000000,colorsign,self.bestMoveReturn,self.openings,self.searched))
                            self.move_thread.start()
                            self.isAIThink = True

                        dragPiece.setcoord((x2,y2))
                        if not self.isTransition:
                            self.listofWhitePieces,self.listofBlackPieces = self.createPieces(self.board)
                        else:
                            movingPiece = dragPiece
                            origin = self.chess_coord_to_pixels((x,y))
                            destiny = self.chess_coord_to_pixels((x2,y2))
                            movingPiece.setpos(origin)
                            step = (destiny[0]-origin[0],destiny[1]-origin[1])

                        self.createShades([])
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                        if self.player==1:
                            self.letters_dict = {'a': 7, 'b': 6, 'c': 5, 'd': 4, 'e': 3, 'f': 2, 'g': 1, 'h': 0}
                            self.numbers_dict = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7}
                        with sr.Microphone() as source:
                            self.r.adjust_for_ambient_noise(source)
                            time.sleep(1.5)
                            try:
                                audio = self.r.listen(source,timeout=2,phrase_time_limit=2)
                                print("Recognizing...")
                                query = self.r.recognize_google(audio)
                                print(f"User said: {query}\n")
                                voice = query.lower()
                                if voice=='avon':
                                    voice='a1'
                                elif voice == 'heetu' or voice=='hetu' or voice=='a 2' or voice=='do' or voice =='tattoo' or voice =='airport' or voice =='tetu' or voice =='edu':
                                    voice='a2'
                                elif voice == 'a tree' or voice=='83':
                                    voice='a3'
                                elif voice == 'krrish 4':
                                    voice='a4'
                                elif voice=='before':
                                    voice='b4'
                                elif voice=='bittu' or voice=='titu':
                                    voice='b2'
                                elif voice=='ba' or voice=='b.ed':
                                    voice='b8'
                                elif voice=='shivan' or voice=='shiva' or voice=='civil':
                                    voice='c1'
                                elif voice=='ceat':
                                    voice='c8'
                                elif voice=='deewan' or voice=='d 1' or voice=='devon' or voice=='devil':
                                    voice='d1'
                                elif voice=='even' or voice=='evil' or voice=='evan' or voice=='yuvan' or voice=='t1':
                                    voice='e1'
                                elif voice=='youtube' or voice=='tu':
                                    voice='e2'
                                elif voice=='mi 4':
                                    voice='e4'
                                elif voice=='mi 5':
                                    voice='e5'
                                elif voice=='8':
                                    voice='e8'
                                elif voice=='jivan':
                                    voice='g1'
                                elif voice=='jeetu' or voice=='jitu':
                                    voice='g2'
                                elif voice=='zefo':
                                    voice='g4'
                                elif voice=='it\'s true' or voice=='issue' or voice=='h 2' or voice=='h2':
                                	voice='h2'
                                elif voice=='quit' or voice =='end' or voice == 'close' or voice=='stop' or voice=='friend' or voice=='top' or voice=='finish' or voice=='and':
                                    self.gameEnded=True
                                if len(voice) == 2:
                                    letter = voice[0]
                                    number = voice[1]
                                    if letter=='v':
                                        letter='b'
                                    elif letter=='s':
                                        letter='h'
                                    if letter in self.letters_dict.keys() and number in self.numbers_dict.keys():
                                        print(self.letters_dict[letter], self.numbers_dict[number])
                                        chess_coord = (self.letters_dict[letter], self.numbers_dict[number])
                                        x = chess_coord[0]
                                        y = chess_coord[1]
                                        if not self.c.isOccupiedby(self.board, x, y, 'wb'[self.player]):
                                            continue
                                        dragPiece = self.getPiece(chess_coord)
                                        listofTuples = self.c.findPossibleSquares(self.position, x, y)
                                        self.createShades(listofTuples)

                                        if dragPiece:
                                            if ((dragPiece.pieceinfo[0] == 'K') and
                                                    (self.c.isCheck(self.position, 'white') or self.c.isCheck(self.position,
                                                                                                              'black'))):
                                                None
                                            else:
                                                self.listofShades.append(Shades(self.greenbox_image, (x, y)))
                                        self.piece_selected_by_voice = True
                            except sr.UnknownValueError:
                                 pygame.mixer.Sound.play(self.repeat_sound)
                            except sr.RequestError:
                                 pygame.mixer.Sound.play(self.requesterror_sound)
                            except Exception:
                                 pygame.mixer.Sound.play(self.repeat_sound)

                        
                    elif self.piece_selected_by_voice and event.type==pygame.MOUSEBUTTONDOWN and event.button==3 :
                        self.piece_selected_by_voice = False
                        with sr.Microphone() as source:
                            while True:
                                self.r.adjust_for_ambient_noise(source)
                                time.sleep(1.5)
                                try:
                                    audio = self.r.listen(source,timeout=2,phrase_time_limit=2)
                                    print("Recognizing...")
                                    query2 = self.r.recognize_google(audio)
                                    print(f"User said: {query2}\n")
                                    voice2 = query2.lower()
                                    if voice2=='avon':
                                        voice2='a1'
                                    elif voice2 == 'heetu' or voice2=='hetu' or voice2=='do' or voice2 =='tattoo' or voice2 =='airport' or voice2 =='tetu' or voice2 =='edu':
                                        voice2='a2'
                                    elif voice2 == 'a tree' or voice2=='83':
                                        voice2='a3'
                                    elif voice2 == 'krrish 4':
                                        voice2='a4'
                                    elif voice2=='before':
                                        voice2='b4'
                                    elif voice2=='bittu' or voice2=='titu':
                                        voice2='b2'
                                    elif voice2=='ba' or voice2=='b.ed':
                                        voice2='b8'
                                    elif voice2=='shivan' or voice2=='shiva' or voice2=='civil':
                                        voice2='c1'
                                    elif voice2=='ceat':
                                        voice2='c8'
                                    elif voice2=='deewan' or voice2=='d 1' or voice2=='devon' or voice2=='devil':
                                        voice2='d1'
                                    elif voice2=='even' or voice2=='evil' or voice2=='evan' or voice2=='yuvan' or voice2=='t1':
                                        voice='e1'
                                    elif voice2=='youtube' or voice2=='tu':
                                        voice2='e2'
                                    elif voice2=='mi 4':
                                        voice2='e4'
                                    elif voice2=='mi 5':
                                        voice2='e5'
                                    elif voice2=='8':
                                        voice2='e8'
                                    elif voice2=='jivan':
                                        voice2='g1'
                                    elif voice2=='jeetu' or voice2=='jitu':
                                        voice2='g2'
                                    elif voice2=='zefo':
                                        voice2='g4'
                                    elif voice2 == 'quit' or voice2 == 'end' or voice2 == 'close' or voice2=='stop' or voice2=='friend' or voice2=='top' or voice2=='finish' or voice2=='and':
                                        
                                        self.gameEnded=True
                                        break
                                    if len(voice2) == 2:
                                        letter = voice2[0]
                                        number = voice2[1]
                                        if letter=='v':
                                            letter='b'
                                        elif letter=='s':
                                            letter='h'
                                        if letter in self.letters_dict.keys() and number in self.numbers_dict.keys():
                                            print(self.letters_dict[letter], self.numbers_dict[number])
                                            chess_coord = (self.letters_dict[letter], self.numbers_dict[number])
                                            x2 = chess_coord[0]
                                            y2 = chess_coord[1]
                                            self.isTransition = False
                                            if not (x2, y2) in listofTuples:
                                                self.isTransition = False
                                                continue
                                            if self.isRecord:
                                                key = self.c.pos2key(self.position)
                                                if [(x, y), (x2, y2)] not in self.openings[key]:
                                                    self.openings[key].append([(x, y), (x2, y2)])

                                            self.c.makemove(self.position, x, y, x2, y2)
                                            self.prevMove = [x, y, x2, y2]
                                            self.player = self.position.getplayer()
                                            if self.player == 1:
                                                 pygame.mixer.Sound.play(self.piece_sound)
                                            else:
                                                 pygame.mixer.Sound.play(self.piece_sound)
                                            self.position.addtoHistory(self.position)
                                            HMC = self.position.getHMC()
                                            if HMC >= 100 or self.c.isStalemate(self.position) or self.position.checkRepition():
                                                self.isDraw = True
                                                self.chessEnded = True
                                            if self.c.isCheckmate(self.position, 'white'):
                                                self.winner = 'b'
                                                self.chessEnded = True
                                            if self.c.isCheckmate(self.position, 'black'):
                                                self.winner = 'w'
                                                self.chessEnded = True
                                            if self.isAI and not self.chessEnded:
                                                if self.player == 0:
                                                    colorsign = 1
                                                else:
                                                    colorsign = -1
                                                self.bestMoveReturn = []
                                                self.move_thread = threading.Thread(target=self.a.negamax,
                                                                                    args=(self.position, self.level, -1000000, 1000000,
                                                                                          colorsign,
                                                                                          self.bestMoveReturn, self.openings,
                                                                                          self.searched))
                                                self.move_thread.start()
                                                self.isAIThink = True

                                            dragPiece.setcoord((x2, y2))
                                            if not self.isTransition:
                                                self.listofWhitePieces, self.listofBlackPieces = self.createPieces(self.board)
                                            else:
                                                movingPiece = dragPiece
                                                origin = self.chess_coord_to_pixels((x, y))
                                                destiny = self.chess_coord_to_pixels((x2, y2))
                                                movingPiece.setpos(origin)
                                                step = (destiny[0] - origin[0], destiny[1] - origin[1])

                                            self.createShades([])
                                            break

                                except sr.UnknownValueError:
                                     pygame.mixer.Sound.play(self.repeat_sound)
                                except sr.RequestError:
                                     pygame.mixer.Sound.play(self.requesterror_sound)
                                except Exception:
                                     pygame.mixer.Sound.play(self.repeat_sound)



            if self.isTransition:
                p,q = movingPiece.getpos()
                dx2,dy2 = destiny
                n= 30.0
                if abs(p-dx2)<=abs(step[0]/n) and abs(q-dy2)<=abs(step[1]/n):
                    movingPiece.setpos((-1,-1))
                    self.listofWhitePieces,self.listofBlackPieces = self.createPieces(self.board)
                    self.isTransition = False
                    self.createShades([])
                else:
                    movingPiece.setpos((p+step[0]/n,q+step[1]/n))
            if self.isDown:
                m,k = pygame.mouse.get_pos()
                if dragPiece:
                    dragPiece.setpos((m-self.square_width/2,k-self.square_height/2))
            if self.isAIThink and not self.isTransition:
                if not self.move_thread.is_alive():
                    self.isAIThink = False
                    self.createShades([])
                    if len(self.bestMoveReturn)==2:
                        [x,y],[x2,y2] = self.bestMoveReturn
                    else:
                        self.c.allMoves(self.position,color)
                    self.c.makemove(self.position,x,y,x2,y2)
                    self.prevMove = [x,y,x2,y2]
                    self.player = self.position.getplayer()
                    HMC = self.position.getHMC()
                    self.position.addtoHistory(self.position)
                    if HMC>=100 or self.c.isStalemate(self.position) or self.position.checkRepition():
                        self.isDraw = True
                        self.chessEnded = True
                    if self.c.isCheckmate(self.position,'white'):
                        self.winner = 'b'
                        self.chessEnded = True
                    if self.c.isCheckmate(self.position,'black'):
                        self.winner = 'w'
                        self.chessEnded = True
                    #Animate the movement:
                    self.isTransition = True
                    movingPiece = self.getPiece((x,y))
                    origin = self.chess_coord_to_pixels((x,y))
                    destiny = self.chess_coord_to_pixels((x2,y2))
                    movingPiece.setpos(origin)
                    step = (destiny[0]-origin[0],destiny[1]-origin[1])

            self.drawBoard()
            pygame.display.update()

            clock.tick(60)

        time.sleep(2)
        pygame.quit()
        if self.isRecord:
            file_handle.seek(0)
            pickle.dump(self.openings,file_handle)
            file_handle.truncate()
            file_handle.close()

    def DisplayPage(self, pageName):
        self.SurfacesAtTop = self.SurfacesAtTop.fromkeys(self.SurfacesAtTop, False)
        self.screen.blit(self.Surfaces[pageName], (0, 0))
        self.SurfacesAtTop[pageName] = True

    def chess_coord_to_pixels(self,chess_coord):
        x,y = chess_coord



        if self.isAI:
            if self.AIPlayer==0:
                return ((7-x)*self.square_width, (7-y)*self.square_height)
            else:
                return (x*self.square_width, y*self.square_height)


        if self.player==0 ^ self.isTransition:
            return (x*self.square_width, y*self.square_height)
        else:
            return ((7-x)*self.square_width, (7-y)*self.square_height)
    def pixel_coord_to_chess(self,pixel_coord):
        if pixel_coord[0] in range(0,640) and pixel_coord[1] in range(0,640):
            x,y = (pixel_coord[0])//self.square_width, (pixel_coord[1])//self.square_height



            if self.isAI:
                if self.AIPlayer==0:
                    return (7-x,7-y)
                else:
                    return (x,y)
            if self.player==0 ^ self.isTransition:
                return (x,y)
            else:
                return (7-x,7-y)
    def getPiece(self,chess_coord):
        for piece in self.listofWhitePieces+self.listofBlackPieces:



            if piece.getInfo()[0] == chess_coord:
                return piece
    def createPieces(self,board):
        self.listofWhitePieces = []
        self.listofBlackPieces = []
        for i in range(8):
            for k in range(8):
                if board[i][k]!=0:
                    p = Piece(board[i][k],(k,i), self.square_width, self.square_height)

                    if board[i][k][1]=='w':
                        self.listofWhitePieces.append(p)
                    else:
                        self.listofBlackPieces.append(p)
        return [self.listofWhitePieces,self.listofBlackPieces]
    def createShades(self,listofTuples):
        
        
        self.listofShades = []
        if self.isTransition:
            return
        if self.isDraw:


            coord = self.c.lookfor(self.board,'Kw')[0]
            shade = Shades(self.circle_image_yellow,coord)
            self.listofShades.append(shade)
            coord = self.c.lookfor(self.board,'Kb')[0]
            shade = Shades(self.circle_image_yellow,coord)
            self.listofShades.append(shade)

            return
        if self.chessEnded:



            coord = self.c.lookfor(self.board,'K'+self.winner)[0]
            shade = Shades(self.circle_image_green_big,coord)
            self.listofShades.append(shade)
            if self.winner=='w':
                 pygame.mixer.Sound.play(self.whitewin_sound)
            else:
                 pygame.mixer.Sound.play(self.blackwin_sound)


        if self.c.isCheck(self.position,'white'):
            coord = self.c.lookfor(self.board,'Kw')[0]
            shade = Shades(self.circle_image_red,coord)
            self.listofShades.append(shade)
        if self.c.isCheck(self.position,'black'):
            coord = self.c.lookfor(self.board,'Kb')[0]
            shade = Shades(self.circle_image_red,coord)
            self.listofShades.append(shade)

        for pos in listofTuples:

            if self.c.isOccupied(self.board,pos[0],pos[1]):
                img = self.circle_image_capture
            else:
                img = self.circle_image_green
            shade = Shades(img,pos)
            #Append:
            self.listofShades.append(shade)
    def drawBoard(self):
        self.screen.blit(self.background,(0,0))



        if self.player==1:
            order = [self.listofWhitePieces,self.listofBlackPieces]
        else:
            order = [self.listofBlackPieces,self.listofWhitePieces]
        if self.isTransition:

            order = list(reversed(order))



        if self.isDraw or self.chessEnded or self.isAIThink:
            #Shades
            for shade in self.listofShades:
                img,chess_coord = shade.getInfo()
                pixel_coord = self.chess_coord_to_pixels(chess_coord)
                self.screen.blit(img,pixel_coord)

        if self.prevMove[0]!=-1 and not self.isTransition:
            x,y,x2,y2 = self.prevMove
            self.screen.blit(self.yellowbox_image,self.chess_coord_to_pixels((x,y)))
            self.screen.blit(self.yellowbox_image,self.chess_coord_to_pixels((x2,y2)))



        for piece in order[0]:
            
            chess_coord,subsection,pos = piece.getInfo()
            pixel_coord = self.chess_coord_to_pixels(chess_coord)
            if pos==(-1,-1):
                self.screen.blit(self.pieces_image,pixel_coord,subsection)
            else:
                self.screen.blit(self.pieces_image,pos,subsection)

        if not (self.isDraw or self.chessEnded or self.isAIThink):
            for shade in self.listofShades:
                img,chess_coord = shade.getInfo()
                pixel_coord = self.chess_coord_to_pixels(chess_coord)
                self.screen.blit(img,pixel_coord)

        for piece in order[1]:
            chess_coord,subsection,pos = piece.getInfo()
            pixel_coord = self.chess_coord_to_pixels(chess_coord)
            if pos==(-1,-1):
                
                self.screen.blit(self.pieces_image,pixel_coord,subsection)
            else:
                self.screen.blit(self.pieces_image,pos,subsection)

    def media(self):


        self.background = pygame.image.load('Media\\board2.png').convert()

        pieces_image = pygame.image.load('Media\\Chess_Pieces_Sprite.png').convert_alpha()
        circle_image_green = pygame.image.load('Media\\green_circle_small.png').convert_alpha()
        circle_image_capture = pygame.image.load('Media\\green_circle_neg.png').convert_alpha()
        circle_image_red = pygame.image.load('Media\\red_circle_big.png').convert_alpha()
        greenbox_image = pygame.image.load('Media\\green_box.png').convert_alpha()
        circle_image_yellow = pygame.image.load('Media\\yellow_circle_big.png').convert_alpha()
        circle_image_green_big = pygame.image.load('Media\\green_circle_big.png').convert_alpha()
        yellowbox_image = pygame.image.load('Media\\yellow_box.png').convert_alpha()

        withfriend_pic = pygame.image.load('Media\\withfriend.png').convert_alpha()
        withAI_pic = pygame.image.load('Media\\withAI.png').convert_alpha()
        playwhite_pic = pygame.image.load('Media\\playWhite.png').convert_alpha()
        playblack_pic = pygame.image.load('Media\\playBlack.png').convert_alpha()
        flipEnabled_pic = pygame.image.load('Media\\flipEnabled.png').convert_alpha()
        flipDisabled_pic = pygame.image.load('Media\\flipDisabled.png').convert_alpha()


        self.size_of_bg = self.background.get_rect().size

        self.square_width = self.size_of_bg[0]//8
        self.square_height = self.size_of_bg[1]//8



        self.pieces_image = pygame.transform.scale(pieces_image,
                                              (self.square_width*6,self.square_height*2))
        self.circle_image_green = pygame.transform.scale(circle_image_green,
                                              (self.square_width, self.square_height))
        self.circle_image_capture = pygame.transform.scale(circle_image_capture,
                                              (self.square_width, self.square_height))
        self.circle_image_red = pygame.transform.scale(circle_image_red,
                                              (self.square_width, self.square_height))
        self.greenbox_image = pygame.transform.scale(greenbox_image,
                                              (self.square_width, self.square_height))
        self.yellowbox_image = pygame.transform.scale(yellowbox_image,
                                              (self.square_width, self.square_height))
        self.circle_image_yellow = pygame.transform.scale(circle_image_yellow,
                                                     (self.square_width, self.square_height))
        self.circle_image_green_big = pygame.transform.scale(circle_image_green_big,
                                                     (self.square_width, self.square_height))
        self.withfriend_pic = pygame.transform.scale(withfriend_pic,
                                              (self.square_width*4,self.square_height*4))
        self.withAI_pic = pygame.transform.scale(withAI_pic,
                                              (self.square_width*4,self.square_height*4))
        self.playwhite_pic = pygame.transform.scale(playwhite_pic,
                                              (self.square_width*4,self.square_height*4))
        self.playblack_pic = pygame.transform.scale(playblack_pic,
                                              (self.square_width*4,self.square_height*4))
        self.flipEnabled_pic = pygame.transform.scale(flipEnabled_pic,
                                              (self.square_width*4,self.square_height*4))
        self.flipDisabled_pic = pygame.transform.scale(flipDisabled_pic,
                                              (self.square_width*4,self.square_height*4))

        #Loading Sounds
        self.checkmate_sound = pygame.mixer.Sound("Voice\check.wav")
        self.draw_sound = pygame.mixer.Sound("Voice\draw.wav")
        self.whitewin_sound = pygame.mixer.Sound("Voice\whitewins.wav")
        self.blackwin_sound = pygame.mixer.Sound("Voice\Blackwins.wav")
        self.blackturn_sound = pygame.mixer.Sound("Voice\Blackturn.wav")
        self.whiteturn_sound = pygame.mixer.Sound("Voice\whiteturn.wav")
        self.piece_sound=pygame.mixer.Sound("Voice\piecehit.wav")
        self.destination_sound=pygame.mixer.Sound("Voice\destination.wav")
        self.instructions_sound = pygame.mixer.Sound("Voice\instructions.wav")
        self.repeat_sound = pygame.mixer.Sound("Voice\Repeat.wav")
        self.selectpiece_sound = pygame.mixer.Sound("Voice\selectpiece.wav")
        self.requesterror_sound = pygame.mixer.Sound("Voice\Requesterror.wav")



    def initialize(self):

        
        self.listofWhitePieces,self.listofBlackPieces = self.createPieces(self.board)

        self.listofShades = []
        self.isDown = False  
        self.isClicked = False 
        self.isTransition = False #Keeps track of whether or not a piece is being animated.
        self.isDraw = False #Will store True if the game ended with a draw
        self.chessEnded = False #Will become True once the chess game ends by checkmate, stalemate, etc.
        self.isRecord = False #Set this to True if you want to record moves to the Opening Book. Do not
        
        self.isAIThink = False #Stores whether or not the AI is calculating the best move to be played.
       
        self.openings = defaultdict(list)

        try:
            file_handle = open('openingTable.txt','r')
            self.openings = pickle.loads(file_handle.read())
        except:
            if self.isRecord:
                file_handle = open('openingTable.txt','w')

        self.letters_dict = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}#dictionary for voice
        self.numbers_dict = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}#dictionary for voice
        self.piece_selected_by_voice=False
        self.r = sr.Recognizer()#speechrecognition class object
        self.r.dynamic_energy_threshold = False
        self.r.energy_threshold = 400
        self.searched = {} #Global variable that allows negamax to keep track of nodes that have
        self.prevMove = [-1,-1,-1,-1] #Also a global varible that stores the last move played, to 

        self.ax,self.ay=0,0
        self.numm = 0
        self.isMenu = True
        self.isAI = -1
        self.AIPlayer = -1
        self.gameEnded = False

    def startMenu(self):

        self.player1 = pygame.image.load('newMedia/image.png')
        self.player1 = pygame.transform.scale(self.player1, (800, 640))


        self.startPage.blit(self.box,(0,0))

        self.startPage.blit(self.player1, (0, 0))

        self.screen.blit(self.startPage, (0, 0))

    def colorsMenu(self):
    	self.medfont = pygame.font.Font("newMedia/Roboto-Black.ttf", 50)
    	self.selectcolor = self.medfont.render('Select Color', False, (220, 90, 10))
    	self.playasblack = self.medfont.render('Black', False, (0, 0, 0))
    	self.playaswhite = self.medfont.render('White', False, (255, 255, 255))
    	self.colorPage.blit(self.box,(0,0))
    	self.colorPage.blit(self.selectcolor, (550-275, 180-15))
    	self.colorPage.blit(self.playasblack, (475-275, 380-15))
    	self.colorPage.blit(self.playaswhite, (775-275, 380-15))
    	self.screen.blit(self.colorPage, (0, 0))




    def selectMenu(self):
    	self.medfont = pygame.font.Font("newMedia/Roboto-Black.ttf", 50)
    	self.selectmode = self.medfont.render('Select Mode', False, (220, 90, 10))
    	self.bymouse = self.medfont.render('Mouse', False, (255, 255, 255))
    	self.byvoice = self.medfont.render('Voice', False, (255, 255, 255))
    	self.selectPage.blit(self.box, (0, 0))
    	self.selectPage.blit(self.selectmode, (550-275, 180-15))
    	self.selectPage.blit(self.bymouse, (475-275, 380-15))
    	self.selectPage.blit(self.byvoice, (775-275, 380-15))
    	self.screen.blit(self.selectPage, (0, 0))


    def call_board(self):

        self.drawBoard()
        self.isMenu = False

        if self.isAI and self.AIPlayer==0:
            colorsign=1
            self.bestMoveReturn = []
            self.move_thread = threading.Thread(target = self.a.negamax,
                        args = (self.position,self.level,-1000000,1000000,colorsign,self.bestMoveReturn,self.openings,self.searched))
            self.move_thread.start()
            self.isAIThink = True

    def onClick(self):


        posx, posy = pygame.mouse.get_pos()

        if self.buttons[1][0] < posx < self.buttons[1][0] + self.buttons[1][2]:
            if self.buttons[1][1] < posy < self.buttons[1][1] + self.buttons[1][3] and self.isAI == -1 :
                self.isAI = True
                posx , posy = (0 , 0)


        if self.buttons[3][0] < posx < self.buttons[3][0] + self.buttons[3][2]:
            if self.buttons[3][1] < posy < self.buttons[3][1] + self.buttons[3][3]:
                if self.isAI == True:
                    if self.diffMenu == -1:
                        self.AIPlayer = 0
                        self.diffMenu = 1
                        posx, posy = (0, 0)
                        self.level = 1
                        self.select = 1
                    elif self.isAI == True and self.select == 1:
                        self.select = 2
                        self.temp = 1
                        posx, posy = (0, 0)
                        print("Mouse Operated")
                elif self.isAI == False:
                    self.temp = -1
                    posx, posy = (0, 0)
        if self.buttons[4][0] < posx < self.buttons[4][0] + self.buttons[4][2]:
            if self.buttons[4][1] < posy < self.buttons[4][1] + self.buttons[4][3]:
                if self.isAI == True:
                    if self.diffMenu == -1:
                        self.AIPlayer = 1
                        self.diffMenu = 1
                        self.level = 1
                        self.select = 1
                        posx, posy = (0, 0)
                    elif self.isAI == True and self.select == 1:
                        self.select = 3
                        self.temp = 1
                        posx, posy = (0, 0)
                        print("Voice Operated")
                elif self.isAI == False:
                    self.isFlip = False
                    self.temp = -1
                    posx, posy = (0, 0)


    def Thinking(self):
        self.ax+=1
        if self.ax==8:
            self.ay+=1
            self.ax=0
        if self.ay==8:
            self.ax,self.ay=0,0
        if self.ax%4==0:
            self.createShades([])
        if self.AIPlayer==0:
            self.listofShades.append(Shades(self.greenbox_image,(7-self.ax,7-self.ay)))
        else:
            self.listofShades.append(Shades(self.greenbox_image,(self.ax,self.ay)))

GUI()



#####################################################################################
# Equipe 1 : BENSAID Mohammed 
# 		      GUESSOUSS Imad 
# 		       KARDIDI Abdellatif
#####################################################################################
#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#    DomoControl Source Management Solution
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU GPLv3 License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU GPLv3 General Public License for more details.
#
#    You should have received a copy of the GNU GPLv3 General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import webiopi
import datetime
import sqlite3
import json
import urllib
from webiopi.devices.digital.pcf8574 import PCF8574

def NOW(): 
    return datetime.datetime.now()    
    
def debug(x):
    webiopi.debug("==>> %s  %s \n" % (NOW(), x))

    
LOG = '/home/pi/domocontrol/test.log'
DATABASE = '/home/pi/domocontrol/db/db.sqlite'

#server = webiopi.Server(port=8080, login="webiopi", password="webiopi")
#~ server.addMacro(myMacroWithArgs)
#~ server.addMacro(myMacroWithoutArgs)

P = {} #Array dove inserire lo stato delle variabili
M = {1:1, 2:2, 3:4, 4:8, 5:16, 6:32, 7:64} #Mapping IO and OUT pin
R = {} #Create dict to put element to send to Status Menu
Q = {} #Create dict to put element to send to Status Menu
GPIO = webiopi.GPIO
TIMER = {} #Dizionario con il valore di tutti i timer


#~ so = PCF8574(32)
#~ si = PCF8574(33)

#~ debug(dir(so))


def logFile(x):
    file = open(LOG, 'a')
    file.write(str(x))
    file.write('\n')
    
def conn(q):
    try:
        c = sqlite3.connect(DATABASE)
        c.row_factory = sqlite3.Row
        c.execute(q)
        c.commit()
        debug("Total number of rows updated : %s" %c.total_changes)
        return c.total_changes
    except Exception as e:
        c.rollback()
        raise e
    finally:
        # Close the db connection
        c.close()

def dict_factory(cursor, row): #funzione abbinata a query()
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def query(q): #return list with dictionary
    #~ debug(q)
    con = sqlite3.connect(DATABASE)
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute(q)
    return cur.fetchall()
    
def setBoard(): #Setta l'indirizzo delle board
    q = "SELECT id, address, board_type FROM pi_board WHERE address > 0 "
    res = query(q) 
    #~ debug(res)
    P['board'] = {}
    P['pcb'] = {}
    for r in res:
        if r['board_type'] == 1: #Board I2C
            #~ P['board']['board_id'] = {'board' : PCF8574(int(r['board_address']))}
            P['board'].update({r['id'] : r})
            P['pcb'].update({r['id'] : PCF8574(int(r['address']))})
            
        elif r['board_type'] == 2: #Board RS485
            pass
        else:
            pass
    
def setBoardIO():
    q = "SELECT * FROM pi_board_io"
    res = query(q) 
    P['board_io'] = {}
    for r in res:
        P['board_io'].update({r['id'] : r})

    q = "SELECT * FROM pi_board"
    res = query(q) 
    P['board'] = {}
    for r in res:
        P['board'].update({r['id'] : r})

    q = "SELECT * FROM pi_type"
    res = query(q) 
    P['type'] = {}
    for r in res:
        P['type'].update({r['id'] : r})

def getIO(io_id, p_id, All=0): #update IN status in P dict
    #~ debug('io_id=%s  p_id=%s all=%s' %(io_id, p_id, All))
    board_id =  P['board_io'][io_id]['board_id']
    io_address = int(P['board_io'][io_id]['address'])
    
    if io_address > 0 : #Board I2C and io = input
        io = P['pcb'][board_id].portRead()
        #~ debug('============>>>>>>>> io=%s' %io)
        if All == 1:
            return io
        else:
            #~ debug("io=%s  M[io_address]=%s  io & M[io_address]=%s " %(io, M[io_address], io & M[io_address]))
            
            P['program'][p_id].update({'IN' : 1 if io & M[io_address] else 0}) 
            
    elif io_address == 0 : #io = input and input = web touch
        if All == 1:
            return None
        pass

def setProgram(): #Put into P dict all pi_program DB
    q = "SELECT * FROM pi_program WHERE enable=1"
    res = query(q)
    P['program'] = {}
    for r in res:
        P['program'].update({r['id'] : r})        
        #~ P['program'][r['id']].update({'OUT' : getIO(P['program'][r['id']]['out_id'])}) #Inizializza valore OUT
        P['program'][r['id']].update({'OUT' : 0})
        P['program'][r['id']].update({'IN_DELAY' : 0})
        P['program'][r['id']].update({'OUT_DELAY' : 0})
        P['program'][r['id']].update({'IN' : r['in_inverted']})
    #~ debug(P['program'])
             


def setOUT(io_id, p_id, OUT): #Set OUT status
    board_id =  P['board_io'][io_id]['board_id']
    io_address = int(P['board_io'][io_id]['address'])
    io_status = P['pcb'][board_id].portRead()
    
    if OUT == 1:
        out = io_status | M[io_address]
        #~ debug("PRIMA  io_id=%s   p_id=%s  out=%s   OUT=%s   io_status=%s " %(io_id, p_id,  out,  OUT, io_status))
        P['pcb'][board_id].portWrite(out)
        #~ P['program'][p_id].update({'OUT' : '0'})
    elif OUT == 0:
        out = io_status ^ M[io_address] 
        #~ debug("PRIMA  io_id=%s   p_id=%s  out=%s   OUT=%s   io_status=%s " %(io_id, p_id,  out,  OUT, io_status))
        if io_status & M[io_address] > 0:
            P['pcb'][board_id].portWrite(out)
            #~ P['program'][p_id].update({'OUT' : '0'})
        else:
            out = '-'
    #~ debug("DOPO  io_id=%s   p_id=%s  out=%s   OUT=%s   io_status=%s " %(io_id, p_id,  out,  OUT, io_status))
    #~ debug("OUT value (io_id, io_status, io_address, out_value, out):%s  %s  %s  %s  %s" %(io_address, io_status, M[io_address],  OUT, out))
    
def setup():
    
    setBoard() #Create board dict with all parameters
    setBoardIO()
    setProgram()
    destroy() #azzera tutti i port
    #~ destroy() #azzera tutti i port
    
def loop():
    debug("*" * 100)
    
    for r in P['program']:
     
        getIO(P['program'][r]['in_id'],r) #read io status and update IN status in P dict 
        
        if P['program'][r]['type_id'] == 1: #=========>>>>>>>>>>> routine ON/OFF
            in_inverted = 1 if P['program'][r]['in_inverted'] == 1 else 0 
            out_inverted = 0 if P['program'][r]['out_inverted'] == 1 else 1
            if P['program'][r]['IN'] == in_inverted:
                P['program'][r].update({'OUT' : int(out_inverted)})
            else:
                P['program'][r].update({'OUT' : int(not out_inverted)})
                P['program'][r]['IN_DELAY'] = 0
        
        if P['program'][r]['type_id'] == 4: #=========>>>>>>>>>>> Manual (switch by web)
            in_inverted = 1 if P['program'][r]['in_inverted'] == 1 else 0 
            out_inverted = 0 if P['program'][r]['out_inverted'] == 1 else 1
            if int(P['program'][r]['IN']) == in_inverted:
                P['program'][r].update({'OUT' : int(out_inverted)})
            else:
                P['program'][r].update({'OUT' : int(not out_inverted)})
            
        setOUT(P['program'][r]['out_id'], r, P['program'][r]['OUT'])
    webiopi.sleep(1)


def destroy(): #Setta gli I/O come out a zero
    P = {}
    q = "SELECT * FROM pi_board WHERE address > 0"
    res =  query(q) 
    for r in res:
        #~ debug(r)
        if r['board_type'] == 1:
            P[r['id']] = PCF8574(int(r['address']))
            
            q = "SELECT board_id, io_type_id, address FROM pi_board_io WHERE board_id=%s ORDER BY board_id, io_type_id" %r['id']
            res =  query(q) 
            debug(res)
            for r in res:
                debug(r)
                if r['io_type_id'] == 1:
                    P[r['board_id']].portWrite(0xff)
                elif r['io_type_id'] == 2:
                    P[r['board_id']].portWrite(0)
    
#~*************** INIZIO NUOVO DOMOCONTROL *******************
@webiopi.macro 
def invertInput(id):
    #~ debug(P['program'])
    if int(P['program'][int(id)]['IN']) == 1:
        P['program'][int(id)].update({'IN':'0'})
    else:
        P['program'][int(id)].update({'IN':'1'})
    #~ debug(P['program'])

#~ compare = lambda a,b: len(a)==len(b) and len(a)==sum([1 for i,j in zip(a,b) if i==j])

@webiopi.macro 
def getMenuStatus(*args):
    global Q
    global P
    global R
    R.update(P)
    del R['pcb']
    
    if not 'program' in Q:
        #~ debug('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++Q not has program Key')    
        Q = R
    return json.dumps(R)


@webiopi.macro             
def setLogin(*args):
    #~ debug("%s  %s" %(args[0],args[1]))
    q="SELECT id,username,name,surname FROM pi_user WHERE username='%s' AND password='%s'" %(args[0],args[1])
    c = query(q)
    #~ debug(q)
    if len(c) > 0:
        return json.dumps(c)    
    else:
        return "Login_NO"
    
@webiopi.macro             
def setUser(args):
    if args == False:
        return
    user_id = json.loads(args)
    q = "SELECT * FROM pi_user WHERE id = '%s'" %user_id
    user = query(q)
    q = "SELECT * FROM pi_privilege"
    privilege = query(q)
    
    res = json.dumps([user,privilege]) 
    #~ debug(res)
    return res 

@webiopi.macro             
def setUserSave(*args):
    q = "UPDATE pi_user SET "
    i=0;
    for r in args:
        if r[0:3] == 'id=':
            ids=r[3:]
        else:
            q += r[0:r.find('=')] + "='" + r[r.find('=')+1:] + "',"
    q += "timestamp='%s'" %NOW()
    q += " WHERE id=%s" % ids
    debug(q)
    c = conn(q)
    #~ debug("query aggiornate: %s   " %c)

@webiopi.macro             
def setLogt(*args): #Da finire. Serve per tracciare l'IP
    q = "INSERT INTO pi_log (command,ip) VALUES('%s', '%s')" %(args[0],args[1])
    #~ debug(q)
    #~ conn(q)
    
@webiopi.macro             
def setArea(*args):
    q = "SELECT * FROM pi_area"
    debug(q)
    res = query(q)
    debug(res)
    return res 

@webiopi.macro 
def setAreaSave(*args):
    #~ debug(args);
    q = "UPDATE pi_area SET "
    i=0;
    for r in args:
        if r[0:3] == 'id=':
            ids=r[3:]
        else:
            q += r[0:r.find('=')] + "='" + r[r.find('=')+1:] + "',"
    q += "timestamp='%s'" %NOW()
    q += " WHERE id=%s" % ids
    #~ debug(q)
    c = conn(q)

@webiopi.macro 
def setAreaAdd(*args):
    q = "INSERT INTO pi_area (name,description) VALUES ('name','description');"
    conn(q)

@webiopi.macro 
def delAreaSave(*args):
    q = "DELETE FROM pi_area WHERE id="+args[0]
    #~ debug(q)
    conn(q)

#Lang Setup
@webiopi.macro             
def getlang(*args):
    q = "SELECT * FROM pi_lang ORDER BY tag"
    #~ debug(q)
    res = query(q)
    #~ debug(res)
    return res 

@webiopi.macro 
def langSave(*args):
    #~ debug(args);
    q = "UPDATE pi_lang SET "
    i=0;
    for r in args:
        if r[0:3] == 'id=':
            ids=r[3:]
        else:
            q += r[0:r.find('=')] + "='" + r[r.find('=')+1:] + "',"
    q += "timestamp='%s'" %NOW()
    q += " WHERE id=%s" % ids
    #~ debug(q)
    c = conn(q)

@webiopi.macro 
def langAdd(tag):
    debug('Lang tag=%s' %tag)
    if not tag:
        tag='-'
    q = "INSERT INTO pi_lang (tag,en,it) VALUES ('"+tag+"','"+tag+"','"+tag+"');"
    debug(q)
    conn(q)

@webiopi.macro 
def langDelete(*args):
    q = "DELETE FROM pi_lang WHERE id="+args[0]
    debug(q)
    conn(q)

@webiopi.macro     
def getLangDict(lang):
    #global Q #Azzera Q in modo che venga riinviato il dizionario dello stato IO
    #Q.update({'program':''})#Azzera Q in modo che venga riinviato il dizionario dello stato IO
    
    q = "SELECT tag,%s FROM pi_lang" %lang
    #~ debug("query getLangDict=%s" %q)
    res = query(q)
    L = {} #Dict translation
    for r in res:
        #~ debug("%s    %s" %(r['tag'],r[lang]))
        L.update({r['tag']:r[lang]})
    debug(L)
    
    return json.dumps(L)
#End Lang

@webiopi.macro             
def setType(*args):
    q = "SELECT * FROM pi_type"
    debug(q)
    res = query(q)
    debug(res)
    return res

@webiopi.macro 
def setTypeSave(*args):
    #~ debug(args);
    q = "UPDATE pi_type SET "
    i=0;
    for r in args:
        if r[0:3] == 'id=':
            ids=r[3:]
        else:
            q += r[0:r.find('=')] + "='" + r[r.find('=')+1:] + "',"
    q += "timestamp='%s'" %NOW()
    q += " WHERE id=%s" % ids
    debug(q)
    c = conn(q)

@webiopi.macro 
def setTypeAdd(*args):
    q = "INSERT INTO pi_type (name,description) VALUES ('name','description');"
    debug(q)
    conn(q)

@webiopi.macro 
def delTypeSave(*args):
    q = "DELETE FROM pi_type WHERE id="+args[0]
    debug(q)
    conn(q)
#~End Type

@webiopi.macro             
def setPrivilege(*args):
    q = "SELECT * FROM pi_privilege"
    debug(q)
    res = query(q)
    debug(res)
    return res 

@webiopi.macro 
def setPrivilegeSave(*args):
    #~ debug(args);
    q = "UPDATE pi_privilege SET "
    i=0;
    for r in args:
        if r[0:3] == 'id=':
            ids=r[3:]
        else:
            q += r[0:r.find('=')] + "='" + r[r.find('=')+1:] + "',"
    q += "timestamp='%s'" %NOW()
    q += " WHERE id=%s" % ids
    debug(q)
    c = conn(q)

@webiopi.macro 
def setPrivilegeAdd(*args):
    q = "INSERT INTO pi_privilege (name,description) VALUES ('name','description');"
    debug(q)
    conn(q)

@webiopi.macro 
def delPrivilegeSave(*args):
    q = "DELETE FROM pi_privilege WHERE id="+args[0]
    debug(q)
    conn(q)
#~End Privilege

#INPUT setup
@webiopi.macro             
def setInputSetup(*args):
    q = "SELECT * FROM pi_io_type"
    debug(q)
    res = query(q)
    debug(res)
    return res 

@webiopi.macro 
def setInputSetupSave(*args):
    #~ debug(args);
    q = "UPDATE pi_io_type SET "
    i=0;
    for r in args:
        if r[0:3] == 'id=':
            ids=r[3:]
        else:
            q += r[0:r.find('=')] + "='" + r[r.find('=')+1:] + "',"
    q += "timestamp='%s'" %NOW()
    q += " WHERE id=%s" % ids
    debug(q)
    c = conn(q)

@webiopi.macro 
def setInputSetupAdd(*args):
    q = "INSERT INTO pi_io_type (name,description) VALUES ('name','description');"
    debug(q)
    conn(q)

@webiopi.macro 
def delInputSetupSave(*args):
    q = "DELETE FROM pi_io_type WHERE id="+args[0]
    debug(q)
    conn(q)
#~End IO setup

#~ BoardSetup 
@webiopi.macro             
def setBoardSetup():
    q = "SELECT * FROM pi_board"
    board = query(q)    
    res = json.dumps(board) 
    #~ debug(res)
    return res 

@webiopi.macro             
def setBoardSetupSave(*args):
    q = "UPDATE pi_board SET "
    i=0;
    for r in args:
        if r[0:3] == 'id=':
            ids=r[3:]
        else:
            q += r[0:r.find('=')] + "='" + r[r.find('=')+1:] + "',"
    q += "timestamp='%s'" %NOW()
    q += " WHERE id=%s" % ids
    debug(q)
    c = conn(q)
    #~ debug("query aggiornate: %s   " %c)

@webiopi.macro
def addBoardSetup():
    q = "INSERT INTO pi_board (name,description,enable,address) VALUES ('???','???','0', '0');"
    #~ debug(q)
    conn(q)
    
#~ END BoardSetup 

#~ Edit IO
@webiopi.macro             
def setBoardIOSetup(id):
    res = {}
    q = "SELECT b.id bid, b.name bname, b.description bdescription, b.enable benable, i.* FROM pi_board_io AS i LEFT JOIN pi_board AS b ON (b.id=i.board_id) WHERE b.id="+id+" ORDER BY b.id, id;"
    debug(q)
    res['board_io'] = query(q)
    q = "SELECT * FROM pi_io_type;"
    res['io'] = query(q) 
    q = "SELECT * FROM pi_board;"
    res['board'] = query(q) 
    #~ debug(res) 
    return json.dumps(res)
    
@webiopi.macro 
def saveBoardIOSetup(*args):
    debug(args)
    q = "UPDATE pi_board_io SET "
    i=0;
    for r in args:
        if r[0:3] == 'id=':
            ids=r[3:]
        else:
            q += r[0:r.find('=')] + "='" + r[r.find('=')+1:] + "',"
    q += "timestamp='%s'" %NOW()
    q += " WHERE id=%s" % ids
    #~ debug(q)
    c = conn(q)

@webiopi.macro
def addBoardIOSetup(id):
    q = "INSERT INTO pi_board_io (io_type_id, name,description,board_id) VALUES ('1','name','description', "+id+");"
    debug(q)
    conn(q)

@webiopi.macro
def delBoardIOSetup(*args):
    q = "DELETE FROM pi_board_io WHERE id="+args[0]
    #~ debug(q)
    conn(q)

@webiopi.macro
def programSetup(*args):
    res = {}
    q = "SELECT * FROM pi_program"
    res['program'] = query(q)
    #~ debug(res)
    return json.dumps(res)

@webiopi.macro
def getProgramSetup(*args):
    res = {}
    q = "SELECT * FROM pi_program WHERE id="+args[0]
    res['program'] = query(q)
    q = "SELECT i.name ioname, bi.*, b.name bname, b.description bdescription FROM pi_board_io bi, pi_io_type i, pi_board b WHERE bi.io_type_id=i.id AND bi.board_id=b.id AND i.name='in' AND bi.id NOT IN (SELECT p.in_id FROM pi_program p);"
    res['in'] = query(q)
    q = "SELECT i.name ioname, bi.*, b.name bname, b.description bdescription FROM pi_board_io bi, pi_io_type i, pi_board b WHERE bi.io_type_id=i.id AND bi.board_id=b.id AND i.name='out' AND bi.id NOT IN (SELECT p.out_id FROM pi_program p);"
    res['out'] = query(q)
    q = "SELECT * FROM pi_type;"
    res['type'] = query(q)
    #~ debug(res)
    return json.dumps(res)

@webiopi.macro
def deleteProgramSetup(id):
    q = "DELETE FROM pi_program WHERE id="+id
    debug(q)
    conn(q)
    setReloadStatus()

@webiopi.macro
def addProgramSetup():
    q = "INSERT INTO pi_program (in_id, out_id, timer) VALUES ('0','0', '%s');"    
    #~ debug(q)
    conn(q)

@webiopi.macro 
def saveProgramSetup(*args):
    q = "UPDATE pi_program SET "
    i=0;
    for r in args:
        if r[0:3] == 'id=':
            ids=r[3:]
        else:
            q += r[0:r.find('=')] + "='" + r[r.find('=')+1:] + "',"
    q += "timestamp='%s'" %NOW()
    q += " WHERE id=%s" % ids
    debug(q)
    c = conn(q)
    setReloadStatus()
    
@webiopi.macro 
def setReloadStatus():
    setup()

def url(t):
    debug(urllib.parse.unquote(t))
    return urllib.parse.unquote(t)

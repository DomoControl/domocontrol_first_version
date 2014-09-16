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
from array import *


def NOW(): 
    return datetime.datetime.now()    
    
def debug(x):
    webiopi.debug("***************** %s  %s \n" % (NOW(), x))

    
LOG = '/home/pi/domocontrol/test.log'
DATABASE = '/home/pi/domocontrol/db/db.sqlite'

#server = webiopi.Server(port=8080, login="webiopi", password="webiopi")
#~ server.addMacro(myMacroWithArgs)
#~ server.addMacro(myMacroWithoutArgs)


GPIO = webiopi.GPIO
TIMER = {} #Dizionario con il valore di tutti i timer


so = PCF8574(32)
si = PCF8574(33)
pcf = {1:1, 2:2, 3:4, 4:8, 5:16, 6:32, 7:64, 8:256}   #map output port
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
    
    

def dict_factory(cursor, row): #trasforma il risultato di una queri in un dizionario (vedi funzione query())
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

def setIO(n, io):
    """Set IN/OUT GPIO"""
    if io == 1:  # 1 = Input
        GPIO.setFunction(int(n), GPIO.IN)
    elif io == 0:
        GPIO.setFunction(int(n), GPIO.OUT)
    #~ debug('Il port n.%s e settato come %s' % (n, GPIO.getFunctionString(int(n))))

def setState(n, state):
    """Set GPIO to 1 or 0"""
    state = int(state)
    n = int(n)
    if state == 0:
        GPIO.digitalWrite(n, GPIO.LOW)
    elif state == 1:
        GPIO.digitalWrite(n, GPIO.HIGH)
    #debug('Il port n.%s ha il valore: %s' % (n, GPIO.digitalRead(n)))

def portStatus():
    """Query che restituisce lo stato dei BUTTONS"""
    q = """SELECT p.id, p.in_out, p.type_id, p.default_state, p.name, p.timer, p.crono,
                    g.pin,  g.type, g.gpio, g.name as gname,
                    t.name as type_name
        FROM pi_prog p, pi_gpio g, pi_type t 
        WHERE p.gpio_id=g.gpio AND p.type_id=t.id AND  g.type LIKE "%IN/OUT%"
        ORDER BY p.id; """
    #~ debug(q)
    return q

#~ debug(dir(so))

def setup():
    #~ debug('Start Webiopi')
    so.portWrite(0)
    si.portWrite(0xff)
    
    cursor = query(portStatus()) #Richiesta dello stato dei PIN dal DB
    for r in cursor:
        
        setIO(r['gpio'], r['in_out'])  # Setta GPIO come IN/OUT
        
        # Tipo: 1=on/off - 2=Timer - 3=Data - 4=Radiocomando
        if r['type_id'] == 1 and r['in_out'] == 0:
            debug('Settaggio GPIO %s nello stato %s ' % (r['gpio'], 'on/off'))
            setState(r['gpio'], r['default_state'])

        if r['type_id'] == 2 and r['in_out'] == 0:
            debug('Settaggio GPIO %s nello stato %s ' % (r['gpio'], r['timer']))
            TIMER[r['gpio']] = {'timer':int(r['timer']), 'start':0, 'count':int(r['timer'])}
            

        if r['type_id'] == 3 and r['in_out'] == 0:
            debug('Settaggio GPIO %s nello stato %s ' % (r['gpio'],'Data'))

        if r['type_id'] == 4:
            debug('Settaggio GPIO %s nello stato %s ' % (r['gpio'], 'Radiocomando'))


def loop():
    """
    cursor = query(portStatus()) #Richiesta dello stato dei PIN dal DB
    
    for r in cursor:
        #~ debug("%s    %s" %(r['default_state'], GPIO.digitalRead(eval(r['gpio']))))
        if r['type_id'] < 3 and r['default_state'] == GPIO.digitalRead(eval(r['gpio'])):
           
            if(r['type_id'] == 2 and TIMER[r['gpio']]['start'] == 1):
                TIMER[r['gpio']]['count'] = TIMER[r['gpio']]['timer']
        
        elif(r['type_id'] == 1):
            #~ debug("Lo stato ON/OF del PIN %s è cambiato" %r['gpio']) 
            continue
        elif(r['type_id'] == 2):
            TIMER[r['gpio']]['start'] = 1;
            if TIMER[r['gpio']]['count'] == 0:
                TIMER[r['gpio']]['start'] = 0
                TIMER[r['gpio']]['count'] = TIMER[r['gpio']]['timer']
                setState(r['gpio'], r['default_state'])
            if TIMER[r['gpio']]['start'] == 1:
                TIMER[r['gpio']]['count'] -= 1
            
        elif(r['type_id'] == 3):            
            #~ debug("Lo stato CRONO del PIN %s è cambiato" %r['gpio']) 
            crono = {}
            ii = 0
            
            if r['crono'].find(';') > 0:
                crono[r['gpio']] = r['crono'].split(';')
                
                n = "%s:%s" %(NOW().hour,NOW().minute)
                
                for res in crono[r['gpio']] :
                    c = res.split('-')
                    #~ debug(c)
                    #~ debug('Start: %s  End: %s ' %(c[0],c[1]))
                    if(n >= c[0] and n < c[1]):
                        #~ debug('CAMBIATO')
                        setState(r['gpio'], 1-int(r['default_state']))
                        ii += 1
                    
                if (ii == 0):
                    setState(r['gpio'], r['default_state'])
    
            
        elif(r['type_id'] == 4):
            debug("Lo stato RADIOCOMANDO del PIN %s è cambiato" %r['gpio']) 
    """
                
    webiopi.sleep(1)


def destroy():
    so.portWrite(0)
    si.portWrite(0xff)

    # GPIO.digitalWrite(LIGHT, GPIO.LOW)

    #~ logf('''\n\nChiusura programma''') 

@webiopi.macro
def getStatus(): #Ritorna lo stato dei pulsanti attivi
    res = query(portStatus()) 
    #~ debug(res)
    return json.dumps(res)

@webiopi.macro        
def getSetupPort(gpio):
    q="SELECT p.id, p.gpio_id, p.type_id, p.in_out, p.default_state, p.active, p.name, p.timer, p.crono FROM pi_program p, pi_gpio g WHERE p.gpio_id=g.gpio AND g.gpio=%s" %gpio 
    #~ debug(q)
    return json.dumps(query(q))


@webiopi.macro    
def setElements(gpio):
    debug(gpio)
    gpio = gpio[:-2]   
    
    st = gpio.split(';;')
    q = "UPDATE pi_program SET "
    id = ''
    i = 0
    
    for r in st:    
        
        rr = r.split('::')
        if rr[0] == 'id':
            id = rr[1]
        else:
            q += rr[0]+"='%s' ," %rr[1]
        i += 1
    if q[-1] == ',':
        q = q[:-1]
    q += " WHERE id=%s" %id
    debug("Setto lo stato del GPIO den DATABASE  %s" %q)
    conn(q)
    setup()
    
@webiopi.macro
def addBt(): #Ritorna i GPIO che si possono aggiungere
    #~ debug('addButton')
    q = "SELECT gpio, id, name FROM pi_gpio WHERE  gpio <> '' AND active=1 AND gpio NOT IN ( SELECT gpio_id FROM pi_program )  ORDER BY 'CAST(name)'"
    return json.dumps(query(q))

@webiopi.macro             
def addGPIO(gpio): #Ritorna i GPIO che si possono aggiungere
    gpio = gpio[:-2]   
    #~ debug(gpio)
    st = gpio.split(';;')
    id = qk = qv = ''
    i = 0
    for r in st: 
        rr = r.split('::')
        qk += rr[0] + ", "
        qv += "'" + rr[1] + "', "
        i += 1
    
    qk = qk[:-2]
    qv = qv[:-2]
    #~ debug('%s   %s' %(qk, qv))
    q = "INSERT INTO pi_program (" + qk + ") VALUES (" + qv + ");"
    debug(q)    
    conn(q)
    setup()
    
@webiopi.macro             
def getTimer():  
    #~ debug(TIMER) 
    return json.dumps(TIMER)
    

    
#~*************** INIZIO NUOVO DOMOCONTROL *******************

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
    q = "SELECT * FROM pi_privileges"
    privileges = query(q)
    
    res = json.dumps([user,privileges]) 
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
    q = q[:-1]
    q += " WHERE id=%s" % ids
    #~ debug(q)
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
    q = q[:-1]
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

@webiopi.macro             
def setPrivileges(*args):
    q = "SELECT * FROM pi_privileges"
    debug(q)
    res = query(q)
    debug(res)
    return res 

@webiopi.macro 
def setPrivilegesSave(*args):
    #~ debug(args);
    q = "UPDATE pi_privileges SET "
    i=0;
    for r in args:
        if r[0:3] == 'id=':
            ids=r[3:]
        else:
            q += r[0:r.find('=')] + "='" + r[r.find('=')+1:] + "',"
    q = q[:-1]
    q += " WHERE id=%s" % ids
    debug(q)
    c = conn(q)

@webiopi.macro 
def setPrivilegesAdd(*args):
    q = "INSERT INTO pi_privileges (name,description) VALUES ('name','description');"
    debug(q)
    conn(q)

@webiopi.macro 
def delPrivilegesSave(*args):
    q = "DELETE FROM pi_privileges WHERE id="+args[0]
    debug(q)
    conn(q)
#~End Privileges 

#INPUT setup
@webiopi.macro             
def setInputSetup(*args):
    q = "SELECT * FROM pi_io"
    debug(q)
    res = query(q)
    debug(res)
    return res 

@webiopi.macro 
def setInputSetupSave(*args):
    #~ debug(args);
    q = "UPDATE pi_io SET "
    i=0;
    for r in args:
        if r[0:3] == 'id=':
            ids=r[3:]
        else:
            q += r[0:r.find('=')] + "='" + r[r.find('=')+1:] + "',"
    q = q[:-1]
    q += " WHERE id=%s" % ids
    debug(q)
    c = conn(q)

@webiopi.macro 
def setInputSetupAdd(*args):
    q = "INSERT INTO pi_io (name,description) VALUES ('name','description');"
    debug(q)
    conn(q)

@webiopi.macro 
def delInputSetupSave(*args):
    q = "DELETE FROM pi_io WHERE id="+args[0]
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
    q = q[:-1]
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
def setBoardIOSetup():
    res = {}
    q = "SELECT b.id bid, b.name bname, b.description bdescription, b.enable benable, i.* FROM pi_board_io AS i LEFT JOIN pi_board AS b ON (b.id=i.board_id) ORDER BY b.id, id;"
    #~ debug(q)
    res['board_io'] = query(q)
    q = "SELECT * FROM pi_io;"
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
    q = q[:-1]
    q += " WHERE id=%s" % ids
    #~ debug(q)
    c = conn(q)

@webiopi.macro
def addBoardIOSetup():
    q = "INSERT INTO pi_board_io (io_id, name,description,board_id) VALUES ('1','name','description', '1');"
    #~ debug(q)
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
    q = "SELECT i.name ioname, bi.*, b.name bname, b.description bdescription FROM pi_board_io bi, pi_io i, pi_board b WHERE bi.io_id=i.id AND bi.board_id=b.id AND i.name='in';"
    res['in'] = query(q)
    q = "SELECT i.name ioname, bi.*, b.name bname, b.description bdescription FROM pi_board_io bi, pi_io i, pi_board b WHERE bi.io_id=i.id AND bi.board_id=b.id AND i.name='out';"
    res['out'] = query(q)
    q = "SELECT * FROM pi_type;"
    res['type'] = query(q)
    #~ debug(res)
    return json.dumps(res)

@webiopi.macro
def deleteProgramSetup(*args):
    q = "DELETE FROM pi_program WHERE id="+args[0]
    debug(q)
    conn(q)

@webiopi.macro
def addProgramSetup():
    q = "INSERT INTO pi_program (in_id, out_id, timer) VALUES ('0','0', '%s');"    
    #~ debug(q)
    conn(q)

@webiopi.macro 
def saveProgramSetup(*args):
    #~ s = urllib.unquote(args)
    #~ debug(s)
    #~ for r in args:
    
    q = "UPDATE pi_program SET "
    i=0;
    for r in args:
        if r[0:3] == 'id=':
            ids=r[3:]
        else:
            q += r[0:r.find('=')] + "='" + r[r.find('=')+1:] + "',"
    q = q[:-1]
    q += " WHERE id=%s" % ids
    debug(q)
    c = conn(q)

def url(t):
    debug(urllib.parse.unquote(t))
    return urllib.parse.unquote(t)

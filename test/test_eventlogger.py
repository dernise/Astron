#!/usr/bin/env python2
import unittest, time
import socket
import os

from common import *
from testdc import *

import json

DESTINATION = ("localhost", 9090)
OUTPUTFILE = os.getcwd()+"/"+"event-logger-test.log"

CONFIG = """\
messagedirector:
    bind: 127.0.0.1:57123

roles:
    - type: eventlogger
      bind: 0.0.0.0:%d
      output: %s
""" % (DESTINATION[1] , OUTPUTFILE)

NETWORKWAIT = 0.1 #seconds

STANDARD_EVENT = '\x82\xa3bar\xa3baz\xa4type\xa3foo' #contact @shadowcoder or @bobbybee on github for information on generating these
NONSTANDARD_MSGPACK = '{'


class TestEventLogger(unittest.TestCase):
    @classmethod
    def setUpClass(cl):
        cl.daemon = Daemon(CONFIG)
        cl.daemon.start()
        
        cl.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    @classmethod            
    def tearDownClass(cl):
        cl.daemon.stop()
        os.remove(OUTPUTFILE)
    
    def numLinesLog(self):
        log = open(OUTPUTFILE, "r")
        contents = log.read()
        return len(contents.split("\n"))
        
    def test_writesToLog(self):
        numLines1 = self.numLinesLog()
        
        self.socket.sendto(STANDARD_EVENT, DESTINATION)
        time.sleep(NETWORKWAIT) # allow network time    
            
        self.assertEqual(self.numLinesLog(), numLines1 + 1) # exactly one line is added
        
    def test_ignoresNonJSON(self):
        numLines1 = self.numLinesLog()
    
        self.socket.sendto(NONSTANDARD_MSGPACK, DESTINATION)     
        time.sleep(NETWORKWAIT) # allow network time    
            
        self.assertEqual(self.numLinesLog(), numLines1) # log is unchanged
        
    def test_ignoresNonMsgpack(self):
        numLines1 = self.numLinesLog()
        
        self.socket.sendto("123", DESTINATION)
        time.sleep(NETWORKWAIT) # allow network time    
            
        self.assertEqual(self.numLinesLog(), numLines1) # log is unchanged
    
    def test_logMessageFormatted(self):
        self.socket.sendto(STANDARD_EVENT, DESTINATION)
        time.sleep(NETWORKWAIT) # allow network time    
        
        log = open(OUTPUTFILE, "r")
        contents = log.read().split("\n")
        lastLine = contents[len(contents) - 2]
                
        decodedJSON = json.loads(lastLine)
        
        self.assertEqual(decodedJSON["type"], "foo")
        self.assertEqual(decodedJSON["bar"], "baz")
        self.assertIn("_time", decodedJSON)
        
if __name__ == '__main__':
    unittest.main()
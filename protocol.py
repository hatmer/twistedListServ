from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

from email.mime.text import MIMEText
from twisted.mail.smtp import sendmail

from helpers import *
from variables import target

class Listserv(LineReceiver):

    def __init__(self, users):
        self.users = users
        self.source = None
        self.dests = []
        self.state = "ENTRY"
        self.subject = "no subject"
        self.tosend = ""

    def connectionMade(self):
        print "client connected"
        self.sendLine("Connected")

    def connectionLost(self, reason):
        print "client disconnected"

    def lineReceived(self, line):
        print "got a line"
        if self.state == "ENTRY":
            self.handle_ENTRY(line)
        elif self.state == "SOURCE":
            self.handle_SOURCE(line)
        elif self.state == "DEST":
            if line.find("/*") > -1:
                self.state = "DATA"
            else:
                self.handle_DEST(line)
        elif self.state == "DATA":
            self.handle_DATA(line)

    def handle_DATA(self, line):
        print "handling message"
        parts = line.split("\n")
        print "parts: ", parts

        for item in parts:
            if item.find("Subject:") == 0:
                print "setting subject line"
                self.subject = item[9:].strip()
            elif item == ".":
                print "found end of data section"
                self.msg = MIMEText(self.tosend)
                self.msg['Subject'] = self.subject
                self.handle_SEND()
            else:
                print "adding", line, " to tosend"
                self.tosend += line
                self.tosend += "\n"
        return

    def handle_SEND(self):
        print "begin send method"
        print "subject:", self.subject
        print "msg:", self.tosend
        host = "localhost"

        with open('addresses.txt', 'r') as fh:
            addrs = fh.readlines()
            for row in addrs:
                if self.source in row:
                    addr_items = row.split(",")
                    if len(addr_items) == 4:
                        self.source = '"' + addr_items[2] + " " + addr_items[3] + '"' + "<" + self.source + ">"

        self.msg['From'] = self.source
        self.msg['To'] = ", ".join(self.dests)
        print "sending.."
        print "msg:", self.msg.as_string()
        deferred = sendmail(host, self.source, target, self.msg.as_string(), port=25)
        print "sent.\n"

    def handle_ENTRY(self, line):
        res = is_add(line)
        if res[0]:
            with open("addresses.txt", 'a') as fh:
                fh.write(','.join(res[1]))
                fh.write("\n")
            return
        res = is_review(line)
        if res[0]:
            with open("addresses.txt", 'r') as fh:
                addresses = fh.readlines()
                self.sendLine(';',join(addresses))
            return
        res = is_distribute(line)
        if res[0]:
            self.sendLine("Processing distribute of type %i" % res[1])
            self.state = "SOURCE"
            return

    def handle_SOURCE(self, line):
        res = is_addr(line)
        if res[0]:
            print "source is %s" % res[1]
            self.source = res[1]
            self.state = "DEST"
            return

    def handle_DEST(self, line):
        res = is_addr(line)
        if res[0]:
            print "added dest: %s" % res[1]
            self.dests.append(res[1])
        else:
            print "not a valid destination address:", res[1]
        return

    def handle_msg(self, line):
        message = "<%s> %s" % (self.name, message)
        for name, protocol in self.users.iteritems():
            if protocol != self:
                protocol.sendLine(message)


class ListservFactory(Factory):

    def __init__(self):
        self.users = {} 

    def buildProtocol(self, addr):
        return Listserv(self.users)


reactor.listenTCP(1234, ListservFactory())
reactor.run()

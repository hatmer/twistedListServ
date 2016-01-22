
"""
Test client.
"""

from twisted.internet import defer, reactor, protocol


# a client protocol

class EchoClient(protocol.Protocol):
    """Once connected send a message"""
    def connectionMade(self):
        #value = raw_input("Enter a string: ")
        self.speak("DISTRIBUTE MAIL")
        d = defer.Deferred()
        reactor.callLater(1, self.speak, "main test@test.com John Doe")
        reactor.callLater(2, self.speak, "hello@test.com")
        reactor.callLater(3, self.speak, "world@test.com")
        reactor.callLater(4, self.speak, "/*")
        reactor.callLater(5, self.speak, "msg1")
        reactor.callLater(5, self.speak, "msg2")
        reactor.callLater(6, self.speak, "Subject: Hello")
        reactor.callLater(7, self.speak, ".")
        reactor.callLater(10, self.transport.loseConnection)

    def speak(self,msg):
        msg = msg+"\r\n"
        print "speaking\n"
        self.transport.write(msg)

    def dataReceived(self, data):
        print "Server said:", data

    def connectionLost(self, reason):
        print "connection lost"

class EchoFactory(protocol.ClientFactory):
    protocol = EchoClient

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed - goodbye!"
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print "Connection lost - goodbye!"
        reactor.stop()

def main():
    f = EchoFactory()
    reactor.connectTCP("localhost", 1234, f)
    reactor.run()

if __name__ == '__main__':
    main()

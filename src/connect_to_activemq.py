import stomp
import sys


class MyListener(stomp.ConnectionListener):
    message_list = []

    def __init__(self):
        self.message_list = []

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        self.message_list.append(message)


def connect_to_activemq():
    hosts = [('localhost', 61613)]
    conn = stomp.Connection(host_and_ports=hosts)
    conn.set_listener('', MyListener())
    conn.connect('admin', 'admin', wait=True, headers={'client-id': 'clientname'})
    conn.subscribe(destination='messageQueue', id='1', ack='auto', headers={'subscription-type': 'MULTICAST',
                                                                            'durable-subscription-name': 'someValue'})

    conn.send(body=' '.join(sys.argv[1:]), destination='messageQueue')
    conn.disconnect()

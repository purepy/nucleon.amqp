# https://github.com/majek/puka/issues/3
from __future__ import with_statement

import os
import puka
import random

import base


class TestBug3(base.TestCase):
    def test_bug3_wait(self):
        client = puka.Client(self.amqp_url)
        promise = client.connect()
        client.wait(promise)
        qname = 'test%s' % (random.random(),)
        promise = client.queue_declare(queue=qname)
        client.wait(promise)

        for i in range(3):
            promise = client.basic_publish(exchange='',
                                           routing_key=qname,
                                           body='x')
            client.wait(promise)

        consume_promise = client.basic_consume(qname)
        for i in range(3):
            msg = client.wait(consume_promise)
            client.basic_ack(msg)
            self.assertEqual(msg['body'], 'x')

        client.socket().close()
        self._epilogue(qname, 1)

    def _epilogue(self, qname, expected):
        client = puka.Client(self.amqp_url)
        promise = client.connect()
        client.wait(promise)
        promise = client.queue_declare(queue=qname)
        q = client.wait(promise)
        self.assertEqual(q['message_count'], expected)

        promise = client.queue_delete(queue=qname)
        client.wait(promise)

    def test_bug3_loop(self):
        client = puka.Client(self.amqp_url)
        promise = client.connect()
        client.wait(promise)
        qname = 'test%s' % (random.random(),)
        promise = client.queue_declare(queue=qname)
        client.wait(promise)

        for i in range(3):
            promise = client.basic_publish(exchange='',
                                           routing_key=qname,
                                           body='x')
            client.wait(promise)

        i = [0]
        def cb(_, msg):
            client.basic_ack(msg)
            self.assertEqual(msg['body'], 'x')
            i[0] += 1
            if i[0] == 3:
                client.loop_break()
        consume_promise = client.basic_consume(qname, callback=cb)
        client.loop()

        client.socket().close()
        self._epilogue(qname, 0)


if __name__ == '__main__':
    import tests
    tests.run_unittests(globals())


import redis
import threading
import json
import time
import random
class  QuicMqManager:
    def __init__(self,connection_id):
        self.listen_channel = f'/{connection_id}/state'
        self.pub_channel = f'/{connection_id}/action'
        self.redis_client = RedisManager()
        self.states={} # key是seq,v是state
        self.actions={} # key是seq,v是action
        self.seq = -1
        self.FIN = False

        self.redis_client.subscribe_channel(self.listen_channel)

    def read_state(self):
        # 返回state和是否结束
        state = self.redis_client.get_message()
        if 'FIN' in state:
            self.FIN=True
            self._stop_sub_channel(self.listen_channel)
            return None,True
        if not state or self.seq >= state['seq']:
            return None,False
        else:
            self.seq = state['seq']
            self.states[state['seq']] = state
        return state,False
    def pub_action(self,action):
        action_msg = {'seq':self.seq,'action':action}
        self.actions[self.seq]=action
        self.redis_client.publish_message(self.pub_channel,json.dumps(action_msg))
    def _stop_sub_channel(self,channel):
        self.redis_client._stop_sub_channel(channel)

class RedisManager:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_host = host
        self.redis_port = port
        self.redis_db = db
        self.redis_conn = None
        self.pubsub = None
        self.msg = {}
        self.threads_stop={} # {channel:stop_flag}
    def _stop_sub_channel(self,channel):
        self.threads_stop[channel]=True
        self.pubsub.unsubscribe(channel)
        self.pubsub.close()

    def get_message(self):
        return self.msg

    def connect(self):
        self.redis_conn = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)

    def disconnect(self):
        if self.redis_conn:
            self.redis_conn.close()
            self.redis_conn = None

    def publish_message(self, channel, message):
        if not self.redis_conn:
            self.connect()
        self.redis_conn.publish(channel, message)
        print(f"Published message: {message}")

    def handle_message(self, message):
        print(f"Received message: {message['data'].decode('utf-8')}")
        self.msg = json.loads(message['data'].decode('utf-8'))

    def subscribe_channel(self, channel):
        if not self.redis_conn:
            self.connect()
        self.pubsub = self.redis_conn.pubsub()
        self.pubsub.subscribe(channel)
        self.threads_stop[channel]=False
        t = threading.Thread(target=self._listen_messages,args=(channel,))
        t.start()

    def _listen_messages(self,channel):
        while not self.threads_stop[channel]:
            message = self.pubsub.get_message() 
            if message and message['type'] == 'message':
                self.handle_message(message)
            time.sleep(0.001)
        print('stop sub channel:',channel)

if __name__ == '__main__':
    connectionID = 'test1234'
    m = QuicMqManager(connectionID)
    fin =False
    print('rl start')
    while not fin:
        state,fin = m.read_state()
        if not state:
            time.sleep(0.01)
            continue
        print('rl: get state',state)
        time.sleep(0.2)
        action = random.randrange(5)
        m.pub_action(action)
    print('server FIN,exit')

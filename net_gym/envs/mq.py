import redis
import threading
import json
class  QuicMqManager:
    def __init__(self,connection_id):
        self.listen_channel = f'/{connection_id}/state'
        self.pub_channel = f'/{connection_id}/action'
        self.redis_client = RedisManager()
        self.states={} # key是seq,v是state
        self.actions={} # key是seq,v是action
        self.seq = -1

        self.redis_client.subscribe_channel(self.listen_channel)

    def read_state(self):
        # 返回state和是否结束
        state = self.redis_client.get_message()
        if 'FIN' in state:
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
        self.redis_client.publish_message(self.pub_channel,action_msg)

class RedisManager:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_host = host
        self.redis_port = port
        self.redis_db = db
        self.redis_conn = None
        self.pubsub = None
        self.msg = None

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

        t = threading.Thread(target=self._listen_messages)
        t.start()

    def _listen_messages(self):
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                self.handle_message(message)

if __name__ == '__main__':
    # 示例用法
    channel_name = 'my_channel'
    message_text = 'Hello, Redis!'

    redis_manager = RedisManager()
    redis_manager.publish_message(channel_name, message_text)
    redis_manager.subscribe_channel(channel_name)
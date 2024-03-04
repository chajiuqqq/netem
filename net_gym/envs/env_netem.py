import gymnasium as gym
from gymnasium import spaces
import numpy as np
import logging
from monitor import BandwidthCollector
import mq
import time
log = logging.getLogger(__name__)


STATS_DICT = {"cwnd": 0, "rtt":1}
def my_rewards(obs,action):
    return 1
class NetEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self,connection_id):
        # 定义 observation_space
        low = [0, 0]  # 观测空间的最小值，[最小的 cwnd 值, 最小的 rtt 值]
        high = [100, 1000]  # 观测空间的最大值，[最大的 cwnd 值, 最大的 rtt 值]
        self.observation_space = spaces.Box(low=np.array(low), high=np.array(high), dtype=np.int32)
        self.action_space = spaces.Discrete(5)
        self.connection_id = connection_id
        self.mq_client= mq.QuicMqManager(connection_id)
      
    def _get_obs(self):
        obs = None
        fin = False
        while not fin and not obs:
            obs,fin = self.mq_client.read_state()
            if obs:
                print('obs:',obs)
            time.sleep(0.01)
        return obs,fin


    def _get_info(self):
        return {}

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)
        self.mq_client= mq.QuicMqManager(self.connection_id)
        observation,_ = self._get_obs()
        info = self._get_info()

        return observation, info

    def step(self, action):
        self.mq_client.pub_action(action)
        observation,fin = self._get_obs()
        terminated = fin
        info = self._get_info()

        # cal reward
        reward = my_rewards(observation,action)

        return observation, reward, terminated, False, info

    def close(self):
        pass
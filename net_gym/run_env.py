from envs.env_netem import NetEnv


env = NetEnv('id12345')
obs, _ = env.reset()
env.render()

print('obs_space',env.observation_space)
print('action_space',env.action_space)
print('action sample',env.action_space.sample())

n_steps = 100
for step in range(n_steps):
    print(f"Step {step + 1}")
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
    print("obs=", obs, "reward=", reward, "done=", done)
    # env.render()
    if done:
        print("Goal reached!", "reward=", reward)
        break
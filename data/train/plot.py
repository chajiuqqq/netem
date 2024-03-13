import numpy as np
import matplotlib.pyplot as plt

# Generate the data
x = np.linspace(0, 1200, 1200)
y = 1 - np.exp(-x/100)

# Add noise
noise = np.random.normal(0, 0.005, size=1200)
y += noise

# # Add jitter
# jitter = np.random.uniform(-0.01, 0.01, size=1200)
# y += jitter
# Plot the data
plt.plot(x, y)
plt.savefig('result.png')
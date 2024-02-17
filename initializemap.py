from nomic import atlas
import numpy as np

# Randomly generate a set of 10,000 high-dimensional embeddings
num_embeddings = 10000
embeddings = np.random.rand(num_embeddings, 256)

# Create Atlas project
dataset = atlas.map_data(embeddings=embeddings)



import random

import numpy as np
import os
from matplotlib import pyplot as plt

for filename in os.listdir("pictures"):
    array = np.load(os.path.join("pictures", random.choice(os.listdir("pictures"))))
    plt.imshow(array)
    plt.show()

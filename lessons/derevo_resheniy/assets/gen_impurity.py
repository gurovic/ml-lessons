import numpy as np
import matplotlib.pyplot as plt

p = np.linspace(0, 1, 500)
entropy = -p * np.log2(p + 1e-10) - (1-p) * np.log2(1-p + 1e-10)
gini = 2 * p * (1-p)
misclass = 1 - np.maximum(p, 1-p)

plt.figure(figsize=(8, 5))
plt.plot(p, entropy, label='Entropy', linewidth=2)
plt.plot(p, gini, label='Gini', linewidth=2)
plt.plot(p, misclass, label='Misclassification', linewidth=2, linestyle='--')
plt.xlabel('p (доля класса 1)')
plt.ylabel('Impurity')
plt.title('Функции impurity для бинарного случая')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('lessons/derevo_resheniy/assets/impurity_functions.png', dpi=150)
print('Done: impurity_functions.png')
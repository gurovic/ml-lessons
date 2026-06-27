import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

np.random.seed(42)
n = 40
x1 = np.random.uniform(0, 10, n)
x2 = np.random.uniform(0, 10, n)
y = ((x1 > 4) & (x2 > 3)) | ((x1 < 3) & (x2 < 6))
y = y.astype(int)

plt.figure(figsize=(8, 6))
colors = ['blue', 'orange']
markers = ['o', '^']
for c in [0, 1]:
    mask = y == c
    plt.scatter(x1[mask], x2[mask], c=colors[c], marker=markers[c], s=60, label=f'Class {c}')

plt.gca().add_patch(Rectangle((0, 0), 4, 10, alpha=0.1, color='blue'))
plt.gca().add_patch(Rectangle((4, 3), 6, 7, alpha=0.1, color='orange'))
plt.gca().add_patch(Rectangle((4, 0), 6, 3, alpha=0.1, color='blue'))
plt.xlabel('x₁')
plt.ylabel('x₂')
plt.title('Границы решения: дерево глубины 2')
plt.legend()
plt.xlim(0, 10)
plt.ylim(0, 10)
plt.grid(alpha=0.2)
plt.tight_layout()
plt.savefig('lessons/derevo_resheniy/assets/binary_classification_rectangles.png', dpi=150)
print('Done: binary_classification_rectangles.png')
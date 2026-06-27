import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier

np.random.seed(42)
n = 60
x1 = np.random.uniform(0, 10, n)
x2 = np.random.uniform(0, 10, n)
y = np.zeros(n)
y[(x1 > 3) & (x2 > 6)] = 1
y[(x1 < 3) & (x2 > 3)] = 2

clf = DecisionTreeClassifier(max_depth=3, random_state=42)
clf.fit(np.column_stack([x1, x2]), y)

xx, yy = np.meshgrid(np.linspace(0, 10, 200), np.linspace(0, 10, 200))
Z = clf.predict(np.column_stack([xx.ravel(), yy.ravel()])).reshape(xx.shape)

plt.figure(figsize=(8, 6))
plt.contourf(xx, yy, Z, alpha=0.2, levels=[-0.5, 0.5, 1.5, 2.5], colors=['blue', 'orange', 'green'])
colors = ['blue', 'orange', 'green']
markers = ['o', '^', 's']
for c in [0, 1, 2]:
    mask = y == c
    plt.scatter(x1[mask], x2[mask], c=colors[c], marker=markers[c], s=60, label=f'Class {c}')
plt.xlabel('x₁')
plt.ylabel('x₂')
plt.title('Границы решения: дерево глубины 3')
plt.legend()
plt.xlim(0, 10)
plt.ylim(0, 10)
plt.tight_layout()
plt.savefig('lessons/derevo_resheniy/assets/decision_boundary.png', dpi=150)
print('Done: decision_boundary.png')
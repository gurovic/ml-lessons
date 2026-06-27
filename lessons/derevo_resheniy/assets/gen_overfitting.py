import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
depth = np.arange(1, 16)
train_acc = 0.7 + 0.3 * (1 - np.exp(-depth/3))
test_acc = 0.7 + 0.25 * np.exp(-((depth-5)**2)/8)

plt.figure(figsize=(8, 5))
plt.plot(depth, train_acc, 'o-', label='Train accuracy', linewidth=2)
plt.plot(depth, test_acc, 's-', label='Test accuracy', linewidth=2)
plt.axvline(x=5, color='gray', linestyle=':', alpha=0.5)
plt.axvspan(5, 15, alpha=0.1, color='red', label='Overfitting region')
plt.xlabel('Глубина дерева')
plt.ylabel('Accuracy')
plt.title('Переобучение дерева решений')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('lessons/derevo_resheniy/assets/overfitting_curve.png', dpi=150)
print('Done: overfitting_curve.png')
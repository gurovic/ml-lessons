import numpy as np
import matplotlib.pyplot as plt

features = ['Возраст', 'Доход', 'Образование', 'Стаж', 'Пол', 'Город', 'ID']
importance = np.array([0.35, 0.25, 0.15, 0.12, 0.07, 0.04, 0.02])
idx = np.argsort(importance)

plt.figure(figsize=(8, 5))
plt.barh(range(len(features)), importance[idx], color='steelblue')
plt.yticks(range(len(features)), [features[i] for i in idx])
plt.xlabel('Важность')
plt.title('Важность признаков (feature_importances_)')
plt.xlim(0, 0.45)
plt.grid(alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('lessons/derevo_resheniy/assets/feature_importance.png', dpi=150)
print('Done: feature_importance.png')
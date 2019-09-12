"""
Load USDA food ingredient data to explore
"""

import pandas as pd
from tqdm import tqdm
from collections import defaultdict
from parse import parse_ingredients, flatten, leaves
import matplotlib.pyplot as plt
plt.style.use('ggplot')

df = pd.read_csv('usda/Products.csv')
missing_ing = df['ingredients_english'].isnull().sum()
print('Missing ingredients:', missing_ing,
      '({:.1f}%)'.format(missing_ing/len(df) * 100))

ingredients = defaultdict(int)
for row in tqdm(df.itertuples(), total=len(df)):
    if isinstance(row.ingredients_english, float):
        continue
    else:
        for ing in leaves(parse_ingredients(row.ingredients_english)):
            ingredients[ing] += 1

n_ingredients = len(ingredients)
print('Ingredients:', n_ingredients)
one_counts = [ing for ing in ingredients.items() if ing[1] == 1]
two_counts = [ing for ing in ingredients.items() if ing[1] == 2]
print('Appears only once:', len(one_counts),
      '({:.1f}%)'.format(len(one_counts)/n_ingredients * 100))
print('Appears only twice:', len(two_counts),
      '({:.1f}%)'.format(len(two_counts)/n_ingredients * 100))

hist = defaultdict(list)
for i, c in ingredients.items():
    hist[c].append(i)
for k in sorted(hist.keys(), reverse=True)[:10]:
    print(hist[k])
import ipdb; ipdb.set_trace()
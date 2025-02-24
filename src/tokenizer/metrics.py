import matplotlib.pyplot as plt
import numpy as np
import tiktoken
import random

from scipy import stats

def calc_fertility():
    '''
    the fertility is the number of tokens divided by the number of words before been tokenized
    '''

    tn = tiktoken.get_encoding('gpt2')

    l_fertility_en, l_fertility_it = [], []

    i = random.randint(1, 100)

    arr = np.load(f'data/shard_en_{i:03d}.npy')
    arr2 = np.load(f'data/shard_it_{i:03d}.npy')

    for i in range(100):
        # load tokenized data
        i = random.randint(1, 100)

        # generate random start indices (fixing the typo in len(arr2))
        idxs = np.random.randint(0, len(arr) - 20000)
        idxs2 = np.random.randint(0, len(arr2) - 20000)  

        # extract chunks of 20,000 tokens
        chunk_arr = arr[idxs:idxs + 20000]
        chunk_arr2 = arr2[idxs2:idxs2 + 20000]

        # decode token chunks to text
        txt = tn.decode(chunk_arr)
        txt2 = tn.decode(chunk_arr2)

        # count words using whitespace splitting
        n_words = len(txt.split())
        n_words2 = len(txt2.split())

        # re-encode text to get token counts
        enc_txt = tn.encode_ordinary(txt)
        enc_txt2 = tn.encode_ordinary(txt2)

        n_tks = len(enc_txt)
        n_tks2 = len(enc_txt2)

        # calculate fertility
        fertility_en = n_tks / n_words
        fertility_it = n_tks2 / n_words2

        l_fertility_en.append(fertility_en)
        l_fertility_it.append(fertility_it)

    return l_fertility_en, l_fertility_it

l_fertility_en, l_fertility_it = calc_fertility()

# take the most frequent fertility 
mode_en = stats.mode(l_fertility_en).mode
mode_it = stats.mode(l_fertility_it).mode

print(f'fertility en: {mode_en:.2f}')
print(f'fertility it: {mode_it:.2f}')

# plot 
plt.hist(l_fertility_en, label='EN')
plt.hist(l_fertility_it, label='IT')

plt.axvline(mode_en, color='blue', linestyle='--', label=f'Mode EN: {mode_en:.2f}')
plt.axvline(mode_it, color='orange', linestyle='--', label=f'Mode IT: {mode_it:.2f}')

plt.legend()

plt.show()


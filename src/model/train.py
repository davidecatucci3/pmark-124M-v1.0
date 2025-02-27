import sentencepiece as sp
import tiktoken
import torch
import sys
import os

sys.path.append(os.path.abspath('src/dataset/../')) # import files from dataset folder

from dataset.data_loader import DataLoader
from hyperparameters import hyperparams
from model import GPT

# hyperparameters
batch_size = hyperparams['batch_size']
ctx_length = hyperparams['ctx_length']
d_model = hyperparams['d_model']
steps = hyperparams['steps']
lr = hyperparams['lr']

# device 
if torch.cuda.is_available():
    device = 'cuda'
    device_name = torch.cuda.get_device_name()
elif torch.mps.is_available():
    device = 'mps'
    device_name = ''
else:
    device = 'cpu'
    device_name = ''

# data loader
data_loader = DataLoader(batch_size, ctx_length)

# use TF32 instead of FP32 to increase training speed
torch.set_float32_matmul_precision('high')

# model 
model = GPT(device)
model.to(device)
#model = torch.compile(model)

# optimizer
optim = torch.optim.AdamW(model.parameters(), lr=lr)

# info model
n_params = sum(p.numel() for p in model.parameters()) / 1e6

print(f'Number of parameters: {n_params:.2f}M')
print(f'Device: {device} | {device_name}')

# train
for i in range(steps):
    xb, yb = data_loader.get_batch(device=device, mix=True, shuffle=True)

    optim.zero_grad()

    # use BF16 instead of PF16 to increase training speed
    with torch.autocast(device_type=device, dtype=torch.bfloat16):
        probs, loss = model(xb, yb)

    loss.backward()
    optim.step()
    
    if i % (steps * 0.1) == 0 or i == steps - 1:
        print(f'step {i}/{steps} | loss: {loss.item():.3f}')

# eval
model.eval()

inp = "Roma è una città,"

'''
tn = sp.SentencePieceProcessor()

tn.load('data/tokenizer/BPE-200-50527.model')
'''

tn = tiktoken.get_encoding('gpt2')

enc = tn.encode(inp)

tks = torch.tensor(enc, dtype=torch.long).unsqueeze(0).to(device)

res = model.generate(tks, max_tokens=2000)[0].tolist()

dec = tn.decode(res)

print(inp + dec)


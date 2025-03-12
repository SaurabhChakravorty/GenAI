import torch
import torch.nn as nn
import math

# Parameters
vocab_size = 10000
d_model = 512
num_heads = 8
d_ff = 2048
num_layers = 6
seq_len = 32
batch_size = 32

# Positional Encoding
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, :x.size(1), :].to(x.device)

# Transformer Encoder
class TransformerEncoder(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, d_ff, num_layers, max_len=5000):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len)
        encoder_layer = nn.TransformerEncoderLayer(d_model, num_heads, d_ff, batch_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers)

    def forward(self, src, src_mask=None):
        src_emb = self.embedding(src) * math.sqrt(d_model)
        src_emb = self.pos_encoding(src_emb)
        return self.encoder(src_emb, src_key_padding_mask=src_mask)

# Transformer Decoder
class TransformerDecoder(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, d_ff, num_layers, max_len=5000):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, max_len)
        decoder_layer = nn.TransformerDecoderLayer(d_model, num_heads, d_ff, batch_first=True)
        self.transformer_decoder = nn.TransformerDecoder(decoder_layer, num_layers)
        self.fc_out = nn.Linear(d_model, vocab_size)

    def forward(self, tgt, memory, tgt_mask=None, memory_mask=None):
        tgt_emb = self.embedding(tgt) * math.sqrt(d_model)
        tgt_emb = self.pos_encoding(tgt_emb)
        output = self.transformer_decoder(tgt_emb, memory, tgt_mask=tgt_mask, memory_key_padding_mask=memory_mask)
        return self.fc_out(output)

# Initialize models
encoder = TransformerEncoder(vocab_size, d_model, num_heads, d_ff, num_layers, seq_len)
decoder = TransformerDecoder(vocab_size, d_model, num_heads, d_ff, num_layers, seq_len)

# Loss and Optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(list(encoder.parameters()) + list(decoder.parameters()), lr=0.0001)

# Dummy input data
src = torch.randint(0, vocab_size, (batch_size, seq_len))
tgt = torch.randint(0, vocab_size, (batch_size, seq_len))

# Training Loop
num_epochs = 10
for epoch in range(num_epochs):
    encoder.train()
    decoder.train()
    optimizer.zero_grad()

    memory = encoder(src)
    output = decoder(tgt[:, :-1], memory)
    loss = nn.CrossEntropyLoss()(output.reshape(-1, vocab_size), tgt[:, 1:].reshape(-1))

    loss.backward()
    optimizer.step()

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")
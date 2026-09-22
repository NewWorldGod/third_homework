# -*- coding: utf-8 -*-
"""
采样实验（exp6 / 采样分析）：固定基线模型，对比 temperature 与 top_k 的生成效果。
用法：先完成基线训练（python min_llm.py），再运行 python sampling.py
结果保存到 sampling_results.txt
"""
import torch
from min_llm import MiniGPT, CharTokenizer, build_corpus

torch.manual_seed(42)

# 语料与分词器须与基线一致
text = build_corpus()
tok = CharTokenizer(text)
V = tok.vocab_size

ckpt = torch.load("ckpt_L2_E128_lr0.001.pt", map_location="cpu")
model = MiniGPT(V, n_embd=ckpt["n_embd"], n_head=ckpt["n_head"],
                n_layer=ckpt["n_layer"], block_size=ckpt["block_size"],
                use_pos=ckpt["use_pos"])
model.load_state_dict(ckpt["state_dict"])
model.eval()

# 各采样参数组合：temperature 0.5 / 1.0 / 1.5，top_k 5 / 20 / 不限制(=V)
combos = [
    (1.0, 20, "基线"),
    (0.5, 20, "低温"),
    (1.5, 20, "高温"),
    (1.0, 5, "小top_k"),
    (1.0, V, "不限制top_k"),
]

prompt = "春"
lines = []
for temp, top_k, note in combos:
    lines.append("=" * 60)
    lines.append(f"【{note}】temperature={temp}, top_k={top_k}, 提示词「{prompt}」")
    for k in range(3):
        out = model.generate(torch.tensor([tok.encode(prompt)]), 120, temp, top_k)
        sample = tok.decode(out[0].tolist())
        lines.append(f"-- 第{k + 1}段: {sample}")
    lines.append("")

with open("sampling_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("\n".join(lines))
print("已保存sampling_results.txt")

# -*- coding: utf-8 -*-
"""
任务四(b) 进阶：给 generate() 增加重复惩罚，对比前后生成效果。
两种惩罚：
  ① 频率惩罚（软）：生成过的字符按出现次数对 logits 减去 alpha*count；
  ② 3-gram 禁止（硬）：若 (c_{t-2}, c_{t-1}, x) 这个 3 元组已出现过，则 x 被禁止
     （若某上下文下所有候选都被禁，则退回不惩罚，保证不卡死）。
复用基线 checkpoint（ckpt_L2_E128_lr0.001.pt），结果保存 repetition_penalty_results.txt
"""
import torch
import torch.nn.functional as F
from min_llm import MiniGPT, CharTokenizer, build_corpus

torch.manual_seed(42)

text = build_corpus()
tok = CharTokenizer(text)
V = tok.vocab_size

ckpt = torch.load("ckpt_L2_E128_lr0.001.pt", map_location="cpu")
model = MiniGPT(V, n_embd=ckpt["n_embd"], n_head=ckpt["n_head"],
                n_layer=ckpt["n_layer"], block_size=ckpt["block_size"],
                use_pos=ckpt["use_pos"])
model.load_state_dict(ckpt["state_dict"])
model.eval()


@torch.no_grad()
def generate_rp(model, idx, max_new_tokens=120, temperature=1.0, top_k=20,
                freq_alpha=0.0, ban_trigram=False):
    """带重复惩罚的自回归生成：freq_alpha>0 启用频率惩罚；ban_trigram=True 启用3-gram禁止。"""
    seen_tri = {}   # (id1, id2) -> set(下一个id)
    counts = {}     # id -> 出现次数
    seq = idx[0].tolist()
    # 统计初始序列 3-gram 与字频
    for i in range(len(seq) - 2):
        seen_tri.setdefault((seq[i], seq[i + 1]), set()).add(seq[i + 2])
    for c in seq:
        counts[c] = counts.get(c, 0) + 1

    out = idx.clone()
    for _ in range(max_new_tokens):
        idx_cond = out[:, -model.block_size:]
        logits, _ = model(idx_cond)
        logits = logits[:, -1, :] / max(temperature, 1e-8)

        # top-k 截断
        kth = torch.topk(logits, min(top_k, logits.size(-1)))[0][:, -1:]
        logits[logits < kth] = float("-inf")

        # ① 频率惩罚（软）
        if freq_alpha > 0:
            pen = torch.zeros_like(logits)
            for cid, n in counts.items():
                pen[0, cid] = freq_alpha * n
            logits = logits - pen

        # ② 3-gram 禁止（硬）：仅屏蔽仍有效的候选
        if ban_trigram and out.shape[1] >= 2:
            a, b = out[0, -2].item(), out[0, -1].item()
            banned = seen_tri.get((a, b), set())
            valid = (logits > float("-inf")).nonzero(as_tuple=True)[1].tolist()
            blocked = [c for c in valid if c in banned]
            if 0 < len(blocked) < len(valid):   # 全禁则放弃，避免卡死
                for c in blocked:
                    logits[0, c] = float("-inf")

        probs = F.softmax(logits, dim=-1)
        next_id = torch.multinomial(probs, 1)
        out = torch.cat([out, next_id], dim=1)

        nid = next_id[0, 0].item()
        if out.shape[1] >= 3:
            a, b = out[0, -3].item(), out[0, -2].item()
            seen_tri.setdefault((a, b), set()).add(nid)
        counts[nid] = counts.get(nid, 0) + 1
    return out


def repeat_stats(s):
    """统计重复 3-gram 比例与独特字符占比"""
    tris = [s[i:i + 3] for i in range(len(s) - 2)]
    uniq_tri = len(set(tris)) / max(len(tris), 1)
    uniq_ch = len(set(s)) / max(len(s), 1)
    return uniq_tri, uniq_ch


settings = [
    ("原始 generate()", dict(freq_alpha=0.0, ban_trigram=False)),
    ("频率惩罚 alpha=1.5", dict(freq_alpha=1.5, ban_trigram=False)),
    ("3-gram 禁止", dict(freq_alpha=0.0, ban_trigram=True)),
    ("3-gram 禁止 + 频率惩罚1.0", dict(freq_alpha=1.0, ban_trigram=True)),
]

lines = []
for temp in (0.5, 1.0):   # 低温下重复最严重，重点观察
    for prompt in ("春", "月"):
        lines.append("#" * 60)
        lines.append(f"### temperature={temp}, top_k=20, 提示词「{prompt}」")
        for name, kw in settings:
            torch.manual_seed(42)
            out = generate_rp(model, torch.tensor([tok.encode(prompt)]),
                              max_new_tokens=120, temperature=temp, top_k=20, **kw)
            s = tok.decode(out[0].tolist())
            ut, uc = repeat_stats(s)
            lines.append("")
            lines.append(f"--- {name} | 重复3-gram比例 {1 - ut:.1%} | 字符多样性 {uc:.1%}")
            lines.append(s[:150])
        lines.append("")

with open("repetition_penalty_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("\n".join(lines))
print("已保存 repetition_penalty_results.txt")

# -*- coding: utf-8 -*-
"""填写《实验作业三_手搓最小LLM_使用CPU训练_实验报告样板.docx》"""
import docx
from docx.shared import Inches, Pt

BASE = r"d:\作业\大模型作业三\hw3_min_llm"
TPL = r"d:\作业\大模型作业三\作业三_手搓最小LLM_使用CPU训练_实验报告样板.docx"
OUT = r"d:\作业\大模型作业三\2025310291_杨锐_实验作业三.docx"

doc = docx.Document(TPL)
paras = list(doc.paragraphs)
tables = doc.tables


def set_para(p, text):
    for r in list(p.runs):
        r.text = ""
    p.add_run(text)


def del_para(p):
    p._element.getparent().remove(p._element)


def cell_text(cell, text, size=None):
    """清空单元格首段并写入文本（支持多行）"""
    first = cell.paragraphs[0]
    for r in list(first.runs):
        r.text = ""
    lines = text.split("\n")
    run = first.add_run(lines[0])
    if size:
        run.font.size = Pt(size)
    for line in lines[1:]:
        p = cell.add_paragraph()
        run = p.add_run(line)
        if size:
            run.font.size = Pt(size)


def cell_images(cell, paths, width=5.9):
    first = cell.paragraphs[0]
    for r in list(first.runs):
        r.text = ""
    for i, path in enumerate(paths):
        p = first if i == 0 else cell.add_paragraph()
        p.add_run().add_picture(path, width=Inches(width))


# ---------- 封面 ----------
set_para(paras[4], "姓　　名：杨锐")
set_para(paras[5], "学　　号：2025310291")
set_para(paras[6], "班　　级：预计算机2班")
set_para(paras[7], "完成日期：2026 年 9 月 22 日")

# ---------- 1.1 实验目的 ----------
set_para(paras[11],
    "本实验在纯 CPU 环境下，用 PyTorch 从零搭建并训练一个约 50 万参数的字符级最小 GPT"
    "（词嵌入 + 可学习位置编码 + Pre-Norm Transformer 块 + 权重共享），在内置唐诗语料上"
    "以“预测下一个字符”的自监督目标完成训练。目的：①把教材第 5 章 Transformer 的公式"
    "落实为可运行代码，理解字符级分词、上下文窗口截取与“标签错开一位”的实现；②通过 "
    "loss 曲线与自回归生成，直观体会温度与 top-k 采样对生成质量的影响；③以控制变量法"
    "考察学习率、层数、嵌入维度、上下文长度与位置编码的作用，并与参数量手算相互印证；"
    "④在使用 TRAE AI 协作编程的过程中规范记录人机协作过程。")
del_para(paras[12]); del_para(paras[13]); del_para(paras[14])

# ---------- 表1 实验环境 ----------
t = tables[0]
rows = [
    ("Windows 11 家庭版 64 位", "AMD Ryzen 9 8945HX，32 逻辑核心"),
    ("Python 3.14.0（64 位）", "命令行 + TRAE 内置终端运行"),
    ("PyTorch 2.14.0+cpu", "CPU 版，无需 GPU/CUDA"),
    ("matplotlib 3.10.9", "绘制 loss 曲线（Agg 后端）"),
    ("TRAE CN", "使用功能：AI 对话生成代码骨架、代码解释、错误修复、实验方案检查"),
]
for i, (v1, v2) in enumerate(rows):
    cell_text(t.rows[i + 1].cells[1], v1, size=9)
    cell_text(t.rows[i + 1].cells[2], v2, size=9)

# ---------- 2.2 基线结果 ----------
set_para(paras[21],
    "参数量：502,656　　最终 loss：0.0279　　初始 loss：6.5627（≈ ln699 ≈ 6.55，"
    "验证了小方差初始化 N(0, 0.02) 的作用）　　耗时：1.8 min（约 18 it/s）")

# ---------- 表2 基线 loss 曲线图 ----------
cell_images(tables[2].rows[0].cells[0], [BASE + r"\loss_curve_L2_E128_lr0.001.png"])

# ---------- 表3 生成示例 ----------
gen = open(BASE + r"\generated_base_saved.txt", encoding="utf-8").read()
blocks = gen.strip().split("\n\n")
trimmed = []
for b in blocks:
    lines = b.split("\n")
    keep = lines[:4]
    body = "\n".join(keep)
    if len(lines) > 4:
        body += "\n……（后略，完整见 generated_base.txt）"
    trimmed.append(body)
cell_text(tables[3].rows[0].cells[0], "\n\n".join(trimmed), size=9)

# ---------- 表4 参数量手算 ----------
t = tables[4]
cell_text(t.rows[1].cells[2], "89,472", size=9)
cell_text(t.rows[2].cells[2], "16,384", size=9)
cell_text(t.rows[3].cells[2], "393,216", size=9)
cell_text(t.rows[4].cells[2],
          "499,072（打印值 502,656，误差 3,584/502,656 ≈ 0.71% < 1%，"
          "差值来自偏置与 LayerNorm 参数）", size=9)
for ri in (1, 2, 3, 4):
    c = t.rows[ri].cells[3]
    cell_text(c, "☑ 一致" + ("（打印值 502,656）" if ri == 4 else ""), size=9)

# ---------- 表5 对照实验 ----------
t = tables[5]
exp_rows = [
    ("1e-2：0.0664；\n1e-4：0.6444", "1e-2：★★；\n1e-4：★",
     "1e-2 前 100 步均值 5.35、曲线震荡，收敛慢且生成开头出现乱字（“春度阴。半钟声到客船。”）；"
     "1e-4 收敛过慢，1000 步仍 0.64，生成不成句；两组初始 loss 均从 ≈6.55 出发"),
    ("1 层：0.0335；\n4 层：0.0256", "1 层：★★★；\n4 层：★★★★",
     "4 层 loss 略优于基线同千步值 0.0267，但千步耗时 1.5 min（1 层仅 0.5 min）；"
     "小语料上加深收益递减"),
    ("64：0.0549；\n256：0.0266", "64：★★；\n256：★★★★",
     "参数量 153K 与 1.79M 相差约 11.7 倍（≈12C²），千步耗时 0.4 min vs 2.0 min；"
     "E64 生成重复明显（“野渡无人，野渡无人”），E256 与基线相当"),
    ("0.1187", "★★★",
     "T=32 放不下两首七绝，长程依赖被截断，loss 显著升高；生成多为整句背诵，"
     "句间衔接与押韵变差；注意力 O(T²)，训练反而最快（65 it/s）"),
    ("0.0318", "★★",
     "loss 仍很低（靠“已见字符集合”区分前缀），但「月」开头生成出现词序混乱："
     "“风急天高楼伤客心，月涌大江滚来急，呼作白玉垒浮云变古今”"),
    ("不重训，仅改采样参数", "0.5：★★★；\n1.5：★★",
     "T=0.5 三段几乎逐字相同（重复端）；T=1.5 出现跨句嫁接与乱字"
     "（“惜沉舟侧畔千帆一曲”“远芳草花落，白不尽”）（胡言端）"),
]
for i, (loss, qual, desc) in enumerate(exp_rows):
    cells = t.rows[i + 1].cells
    cell_text(cells[4], loss, size=9)
    cell_text(cells[5], qual, size=9)
    cell_text(cells[6], desc, size=9)

# ---------- 4.1~4.5 分析 ----------
set_para(paras[33],
    "lr=1e-2：前 100 步均值 5.35（基线 3.61），下降慢且震荡，最终 0.0664——步长过大，"
    "在最优点附近来回跳动，本组未彻底 NaN 但明显劣于基线，生成开头出现“春度阴。半钟声到客船。”"
    "等乱序片段；lr=1e-4：前 100 步均值 5.88，1000 步只降到 0.6444，约为基线同 步 loss 的 "
    "24 倍——步长过小，同样的迭代预算远未收敛，生成“春涧欲人。寒梅著独人城人”不成句。"
    "三组初始 loss 都从 ≈6.55 出发（≈ln699）。结论：1e-3 是该规模下的较优折中。")
del_para(paras[36]); del_para(paras[37])

set_para(paras[39],
    "千步最终 loss：1 层 0.0335、2 层 0.0267、4 层 0.0256——层数翻倍只带来 0.001 量级的改善，"
    "而耗时从 0.5 min 增至 1.5 min（约 3 倍）。语料仅 2163 字，2 层模型的“背诵容量”已经饱和，"
    "继续加深几乎只有成本没有收益：容量必须与数据规模匹配。")
del_para(paras[42]); del_para(paras[43])

set_para(paras[45],
    "参数量约按 12C² 增长：C=64 为 153,024（约基线的 1/3.3），C=256 为 1,791,744（约 3.6 倍），"
    "两者相差约 11.7 倍；千步耗时 0.4 min vs 2.0 min（约 5 倍）。E64 容量不足，生成出现"
    "“小雨晚来急，野渡无人，野渡无人，野渡无人舟自横”式的重复；E256 生成与基线相当（整句"
    "背诵），质量并未同步继续提升——小语料上超过基线容量后收益趋近于零。")
del_para(paras[48]); del_para(paras[49])

set_para(paras[51],
    "T=32 时 loss 0.1187，显著高于其余实验：窗口装不下两首七绝（64 字），模型能学的长程依赖"
    "被硬性截断。生成“春深锁二乔。巴山楚水凄凉地……”仍可整句背诵，但句与句的衔接只能依赖很短"
    "的历史，主题连贯与押韵变差；训练速度反而最快（65 it/s vs 基线 18 it/s），因为注意力计算"
    "量随 T² 下降。")
del_para(paras[54]); del_para(paras[55])

set_para(paras[57],
    "去掉位置编码后参数量 486,272（少了 16,384 个位置参数），loss 仍能降到 0.0318——看似学得"
    "不错，但生成暴露本质：提示「春」时从语料开头逐句背诵尚可；提示「月」时出现“风急天高楼"
    "伤客心，月涌大江滚来急，呼作白玉垒浮云变古今”这类多句嫁接、语序混乱的“诗”。原因：自"
    "注意力对输入排列不变，去掉位置编码后模型只能靠因果掩码造成的“已出现字符集合”区分前缀，"
    "顺序信息大量丢失（详见思考题(1)）。")
del_para(paras[60]); del_para(paras[61])

# ---------- 表6~10 各实验曲线 ----------
cell_images(tables[6].rows[0].cells[0],
            [BASE + r"\loss_curve_L2_E128_lr0.01.png", BASE + r"\loss_curve_L2_E128_lr0.0001.png"], 5.5)
cell_images(tables[7].rows[0].cells[0],
            [BASE + r"\loss_curve_L1_E128_lr0.001.png", BASE + r"\loss_curve_L4_E128_lr0.001.png"], 5.5)
cell_images(tables[8].rows[0].cells[0],
            [BASE + r"\loss_curve_L2_E64_lr0.001.png", BASE + r"\loss_curve_L2_E256_lr0.001.png"], 5.5)
cell_images(tables[9].rows[0].cells[0],
            [BASE + r"\loss_curve_L2_E128_T32_lr0.001.png"], 5.5)
cell_images(tables[10].rows[0].cells[0],
            [BASE + r"\loss_curve_no_pos.png"], 5.5)

# ---------- 表11 采样实验记录 ----------
t = tables[11]
samp_rows = [
    ("春来发几枝。愿君多采撷，此物最相思。／独坐幽篁里，弹琴复长啸。深林人不知，明月来相照。",
     "接近语料原文背诵，三段高度相似；确定性与多样性居中，是基线平衡点"),
    ("春来发几枝。愿君多采撷……（三段几乎逐字相同）；另一段“春色来天地，玉垒浮云变古今。”",
     "分布被压尖→近似贪心，三段几乎相同，重复严重，多样性最低"),
    ("春深锁二乔。巴山楚水凄凉地……怀旧空吟闻笛赋，惜沉舟侧畔千帆一曲，到乡翻翻似烂柯人。"
     "／远芳草花落，白不尽，晴却有，晴。",
     "分布被拉平→低概率字被采到，出现跨句嫁接与生造短语，多样性最高但开始“胡言”"),
    ("春来发几枝。愿君多采撷，此物最相思。……（与基线第 1 段相同）",
     "候选仅剩前 5 个字符，进一步剔除长尾，输出更保守，效果与低温类似：重复↑"),
    ("春色来天地，玉垒浮云变古今。……白云千载空悠。／晴川历历历汉阳树／春来发几枝。愿君任郁孤台镜",
     "不截断长尾，错误候选有机会被采到，出现“空悠”“历历历”“任郁孤台镜”等小错——"
     "top_k 的价值正是屏蔽长尾噪声"),
]
for i, (excerpt, analysis) in enumerate(samp_rows):
    cells = t.rows[i + 1].cells
    cell_text(cells[3], excerpt, size=9)
    cell_text(cells[4], analysis, size=9)

# ---------- 5.2 生成对比分析 ----------
set_para(paras[68],
    "从两个维度看：①确定性↔多样性：温度越低、top_k 越小，采样越接近贪心，输出越确定"
    "（T=0.5 时三段几乎逐字相同）；温度越高、top_k 越大，分布越平，输出越发散多样。"
    "②重复↔胡言：低温/小 top_k 走向“重复”一端（背诵+循环），高温/不截断走向“胡言”一端"
    "（跨句嫁接、生造词，如“惜沉舟侧畔千帆一曲”“晴川历历历汉阳树”）。本任务语料小、模型以"
    "背诵为主，我认为 temperature=1.0 + top_k=20 是最优组合：既保留诗句格式与连贯，又允许"
    "在 top-20 内引入有限随机性避免逐字复读；若要严格复现原文可降到 T=0.5，若要“创作”新句"
    "可升到 T≈1.2，但必须接受少量病句。")
del_para(paras[69]); del_para(paras[70]); del_para(paras[71])

# ---------- 表12 采样生成对比（贴原文） ----------
sample_txt = open(BASE + r"\sampling_results.txt", encoding="utf-8").read()
cell_text(tables[12].rows[0].cells[0],
          "完整生成原文（节选，详见 sampling_results.txt）：\n" + sample_txt[:1800] +
          "\n……（后略）", size=8)

# ---------- 表13 AI 协作记录 ----------
t = tables[13]
ai_rows = [
    ("生成代码骨架",
     "“请按‘数据→分词器→模型→训练→采样’的顺序，逐段生成 min_llm.py 框架，"
     "每段附张量形状说明。”",
     "AI 逐段给出 CharTokenizer、CausalSelfAttention、Block、MiniGPT 与主流程；我逐段核对"
     "教材公式（缩放点积、因果掩码、Pre-Norm 残差、权重共享）后采纳，并自行补充了 checkpoint"
     "保存与「春」「月」各 2 段的批量生成逻辑"),
    ("代码解释",
     "“逐行解释 CausalSelfAttention 中 view/transpose 的多头拆分与 -inf 掩码填充。”",
     "AI 的形状推演 (B,T,C)→(B,H,T,hd) 与我纸面手写一致，采纳；确认了 qkv 一次投影后 "
     "split(C, dim=2) 再拆头的正确性"),
    ("错误修复与实验设计",
     "“Windows 控制台中文乱码怎么处理？请检查表 5 对照实验方案是否满足单一变量原则。”",
     "采纳 chcp 65001 / matplotlib Agg 后端建议；AI 建议 exp1~exp5 统一 --iters 1000、"
     "固定 seed=42 保证语料与初始条件一致，采纳；我另发现脚本曲线命名未含 block_size 会"
     "覆盖基线曲线，自行修改 tag 加入 T32 标识"),
]
for i, (scene, prompt, adoption) in enumerate(ai_rows):
    cells = t.rows[i + 1].cells
    cell_text(cells[1], scene, size=9)
    cell_text(cells[2], prompt, size=9)
    cell_text(cells[3], adoption, size=9)

# ---------- 思考题 ----------
answers = {
    75: (
        "去掉位置编码后模型仍能学到：①字符的统计分布（哪些字高频）；②字符共现/搭配（“春”后常接"
        "“眠/风/来”）；③借助因果掩码造成的“已出现字符集合”近似区分前缀——因此 loss 仍能降到 "
        "0.03 左右，提示「春」时甚至能从语料开头逐句背诵。但“成句”大打折扣：模型无法精确感知"
        "每个字处在第几位，一旦需要区分“相同字符集合的不同排列”（句内语序、接句位置、押韵）就"
        "出错——提示「月」的生成出现“风急天高楼伤客心，月涌大江滚来急，呼作白玉垒浮云变古今”"
        "这种多句嫁接、语序混乱的句子。原因：自注意力对输入顺序排列不变（教材 5.2 节），没有"
        "位置编码，Transformer 退化为“词袋 + 前缀集合”模型——学得到“用什么字”，学不好"
        "“按什么顺序排”。"),
    79: (
        "手算：词嵌入 V×C = 699×256 = 178,944；位置编码 T×C = 128×256 = 32,768；Transformer "
        "块 L×12C² = 3×12×256² = 3×12×65,536 = 2,359,296；合计 ≈ 2,571,008 ≈ 257 万，约为"
        "基线 499,072 的 5.1 倍。实测印证：exp3 中 C=256（L 仍为 2）参数量 1,791,744、千步耗时 "
        "2.0 min（基线约 0.9 min）；exp2 中 L=4 参数量 899,200、千步 1.5 min。可见 C、L 同增后"
        "参数按平方增长、耗时成倍上升，而 loss 在小语料上几乎不再下降（基线 0.0267 vs E256 "
        "0.0266）。结论：容量必须与数据规模匹配，盲目加大模型只增加训练成本而不带来收益——"
        "这正是 Scaling Law 要求模型规模与数据量同步扩大的含义。"),
    83: (
        "T→0：softmax 退化为 one-hot 的贪心解码（argmax），每步必选概率最大的字符，完全确定、"
        "可复现；T→∞：logits 除以无穷大后趋于相同，softmax 退化为词表上的均匀分布，等价于纯"
        "随机采样。低温适合要求正确性与稳定性的任务：事实问答、代码生成、数学推理、数据抽取；"
        "高温适合追求多样性与创意的场景：诗歌/小说创作、头脑风暴、数据增广。exp6 印证：T=0.5 时"
        "三段生成几乎逐字相同（走向“重复”一端）；T=1.5 时出现“惜沉舟侧畔千帆一曲”“远芳草花落，"
        "白不尽”等嫁接乱句（走向“胡言”一端）。"),
    87: (
        "字符级分词：优点——词表极小（本实验 699）、零预处理、永无 OOV、实现简单，能把注意力"
        "集中到架构本身；缺点——同样文本的序列长度远大于子词/词级（单字信息量少）、注意力计算 "
        "O(T²) 开销大、单 token 语义弱、难以利用词法规律（词根、前后缀）。BPE 从字符出发逐步"
        "合并高频相邻对，用“合并次数”这一个旋钮在词表大小与序列长度之间折中：高频词整体编码"
        "（序列短），生僻词拆成子词组合（不 OOV）。真实 LLM 用 BPE 类分词器，因为在万亿 token "
        "语料下它显著缩短序列、节省算力；子词兼具泛化性（可组合出新词）与语义性（高频词整体"
        "编码）；词表 3~15 万在 embedding 参数量（V×C）与计算效率之间取得平衡。"),
    91: (
        "三方面比较——数据量：本实验约 2×10³ 字符 vs 真实 LLM 数万亿 token，相差约 10 个数量级；"
        "参数量：5×10⁵ vs 10¹¹~10¹²，相差 6~7 个数量级；训练目标：同为“下一 token 预测”，但"
        "真实 LLM 还要经过指令微调（SFT，学会听懂并执行指令）和 RLHF（对齐人类偏好），本实验"
        "完全没有这两个阶段。把语料扩大 1000 倍（约 2×10⁶ 字）也得不到“会聊天”的模型：①50 万"
        "参数的容量远不足以建模开放对话，按 Scaling Law 需要参数与数据同步扩大；②语料是诗而"
        "非对话，缺乏“指令—回复”结构，模型只会“背更多诗”；③没有 SFT/RLHF，模型不知道“回答"
        "问题”这一行为模式。预训练教会的只是语言的统计规律（“会说话”），指令微调与 RLHF 才"
        "教会模型“按人的意图说话”（“会聊天”）。"),
    95: (
        "AI 最有价值的环节：①按“数据→分词器→模型→训练→采样”顺序生成骨架代码，节省大量样板"
        "劳动；②解释 view/transpose 多头拆分的形状推演，帮我快速验证纸面推导；③检查对照实验"
        "方案的单一变量原则（统一 iters、固定 seed）。必须自己读懂公式才能改对的环节：①因果"
        "掩码的 -inf 填充——必须在 softmax 之前 masked_fill，若在 softmax 之后置零会错误地丢失"
        "概率质量；②多头 reshape 顺序——必须先 view(B,T,H,hd) 再 transpose(1,2)，顺序颠倒会把"
        "不同头的维度错乱拼接；③权重共享 head.weight = tok_emb.weight 的绑定写法与“参数只计"
        "一次”的含义；④“标签错开一位”——x 取前 T 个、y 取后 T 个，差一位任务就完全不同。这些"
        "点 AI 给的代码大体正确，但一旦自己不理解、改动一处训练就会悄然失效（loss 不降），"
        "这正是“AI 写、人必须懂”的意义。"),
}
for idx, ans in answers.items():
    set_para(paras[idx + 1], ans)
    del_para(paras[idx + 2]); del_para(paras[idx + 3])

doc.save(OUT)
print("saved:", OUT)

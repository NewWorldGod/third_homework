# 依次运行基线与 exp1~exp5 对照实验，日志保存到 logs/
$ErrorActionPreference = "Continue"
New-Item -ItemType Directory -Force -Path logs | Out-Null

function Run-Exp($name, $argList) {
    Write-Host "===== $name ====="
    python min_llm.py @argList 2>&1 | Tee-Object -FilePath "logs\$name.log"
}

# 基线（2000 步）
Run-Exp "baseline" @()
Copy-Item generated_base.txt generated_base_saved.txt -Force

# exp1 学习率
Run-Exp "exp1_lr0.01"   @("--iters", "1000", "--lr", "1e-2")
Run-Exp "exp1_lr1e-4"  @("--iters", "1000", "--lr", "1e-4")
# exp2 层数
Run-Exp "exp2_L1"      @("--iters", "1000", "--n_layer", "1")
Run-Exp "exp2_L4"      @("--iters", "1000", "--n_layer", "4")
# exp3 嵌入维度
Run-Exp "exp3_E64"     @("--iters", "1000", "--n_embd", "64", "--n_head", "2")
Run-Exp "exp3_E256"    @("--iters", "1000", "--n_embd", "256", "--n_head", "8")
# exp4 上下文长度
Run-Exp "exp4_T32"     @("--iters", "1000", "--block_size", "32")
# exp5 位置编码
Run-Exp "exp5_no_pos"  @("--iters", "1000", "--no_pos")
# exp6 采样分析（复用基线模型）
python sampling.py 2>&1 | Tee-Object -FilePath logs\exp6_sampling.log

# 恢复基线生成文件为最终产物
Copy-Item generated_base_saved.txt generated_base.txt -Force
Write-Host "===== ALL DONE ====="

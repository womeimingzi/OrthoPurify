# OrthoPurify

Official implementation of **Purifying Backdoored Large Vision-Language Models by Removing Hijacked Directions**.

[![arXiv](https://img.shields.io/badge/arXiv-2610.09941-b31b1b.svg)](https://arxiv.org/abs/2610.09941)

Pseudo-Benign Orthogonal Projection Purification for VLM Backdoor Defense.

Identifies hijacked weight-update directions in adapter modules via SVD principal angle analysis, then removes them by one-step orthogonal projection. Requires only 64 clean samples and no knowledge of the attack type.

Supported models: LLaVA-1.5-7B/13B, Qwen3-VL-8B/4B-Instruct.

## Directory Structure

```
OrthoPurify/
├── assets/                              # Static resources (trigger images, ISSBA encoder)
├── configs/                             # DeepSpeed configs (ZeRO-2/3)
├── dataset_loaders/                     # HuggingFace dataset scripts (COCO, VQAv2)
├── entrypoints/
│   ├── training/
│   │   ├── train.sh                     # Main training entry (DeepSpeed)
│   │   └── train_lora.sh               # LoRA training wrapper
│   ├── attack_pipelines/                # End-to-end attack+defense pipelines
│   ├── data_download/                   # Dataset download utilities
│   └── tools/                           # Benchmarking & visualization scripts
├── experiments/
│   ├── shared/                          # Core algorithm (SVD, direction extraction, purification)
│   │   ├── projection.py               # Core SVD & projection utilities
│   │   └── multimatrix.py              # Multi-matrix SVD (Qwen3-VL adapter)
│   ├── main_method/orthopurify/         # OrthoPurify (our method)
│   │   ├── purify_llava.py             # LLaVA purification
│   │   ├── purify_qwen3vl.py           # Qwen3-VL purification
│   │   ├── run_ablation_k.py           # k ablation
│   │   └── run_ablation_nsamples.py    # N_samples ablation
│   ├── baseline_methods/                # Defense baselines
│   │   ├── finetune_recovery/           # Clean Fine-tuning
│   │   ├── fine_pruning/                # Fine-Pruning (RAID 2018)
│   │   ├── anp/                         # Adversarial Neuron Pruning (NeurIPS 2021)
│   │   └── clp/                         # Channel Lipschitz Pruning (ECCV 2022)
│   └── analysis_experiments/
│       ├── residual_energy/             # Residual backdoor energy analysis
│       └── backdoor_reconstruction/     # Backdoor reconstruction analysis
├── vlm_backdoor/                        # Core library
│   ├── attacks/                         # Trigger injection (BadNet, WaNet, Blended, ISSBA, etc.)
│   ├── data/                            # Dataset, collators, online poisoning
│   ├── evaluation/                      # Evaluators + metrics (ASR, CIDEr, V-score)
│   ├── training/                        # MetaTrainer, CustomTrainer, TrojVLM, VLOOD
│   └── utils/
├── tests/
└── requirements/
    ├── requirements_llava.txt           # LLaVA env (transformers 4.40.2)
    └── requirements_qwen3.txt           # Qwen3-VL env (transformers >= 5.3)
```

## Installation

```bash
git clone https://github.com/womeimingzi/OrthoPurify.git
cd OrthoPurify
```

Two separate environments are required (incompatible `transformers` versions):

```bash
# LLaVA
pip install -r requirements/requirements_llava.txt

# Qwen3-VL
pip install -r requirements/requirements_qwen3.txt
```

## Usage

All commands assume the repository root (`OrthoPurify/`) as working directory.

### 1. Backdoor Attack Training

```bash
bash entrypoints/training/train.sh <GPUs> <MODEL> <TRAIN_TYPE> <DATASET> <PATCH_TYPE> <PATCH_LOC> <ATTACK_TYPE> <NAME> [PR] [EPOCH]
```

**Positional arguments:**

| #   | Argument    | Values                                                                 |
| --- | ----------- | ---------------------------------------------------------------------- |
| 1   | GPUs        | e.g. `0,1`                                                             |
| 2   | MODEL       | `llava-7b`, `llava-13b`, `qwen3-vl-8b`, `qwen3-vl-4b`, `iblip-7b`      |
| 3   | TRAIN_TYPE  | `adapter`, `use_lora`, `freeze_vision`, `none`                         |
| 4   | DATASET     | `coco`, `vqav2`                                                        |
| 5   | PATCH_TYPE  | `random`, `blended`, `blended_kt`, `warped`, `SIG`, `issba`            |
| 6   | PATCH_LOC   | `random_f`, `four_corners`, `middle`, `blended`, `blended_kt`, `issba` |
| 7   | ATTACK_TYPE | `replace`, `random_insert`, `badtoken`                                 |
| 8   | NAME        | Experiment suffix                                                      |
| 9   | PR          | Poison rate, default `0.1`                                             |
| 10  | EPOCH       | Training epochs, default `2`                                           |

**Key environment variable overrides:** `LR`, `PER_DEVICE_TRAIN_BS`, `GRAD_ACCUM_STEPS`, `DS_CONFIG`, `LOSS` (`lm`/`trojvlm`/`vlood`), `LORA_R`, `LORA_ALPHA`, `IMG_SIZE`, `BF16`.

**Example:**

```bash
bash entrypoints/training/train.sh 0,1 llava-7b adapter coco random random_f replace badnet_0.1pr 0.1 2
```

Output is saved to `model_checkpoint/present_exp/<MODEL>/<DATASET>/<PATCH_TYPE>-<TRAIN_TYPE>-<NAME>/`.

---

### 2. OrthoPurify Defense (Main Method)

#### LLaVA

```bash
python experiments/main_method/orthopurify/purify_llava.py [OPTIONS]
```

| Argument              | Default                  | Description                                   |
| --------------------- | ------------------------ | --------------------------------------------- |
| `--backdoor_dir`      | —                        | Path to backdoor checkpoint directory         |
| `--model_path`        | `models/llava-1.5-7b-hf` | Base model path                               |
| `--k`                 | `10`                     | SVD subspace dimension                        |
| `--n_samples`         | `64`                     | Clean samples for pseudo-benign training      |
| `--num_epochs`        | `2`                      | Pseudo-benign training epochs                 |
| `--pseudo_lr`         | `2e-4`                   | Learning rate                                 |
| `--angle_threshold`   | `50.0`                   | Principal angle threshold (degrees)           |
| `--test_num`          | `512`                    | Evaluation test images                        |
| `--all_directions`    | off                      | Use all directions above threshold            |
| `--skip_ground_truth` | off                      | Skip ground-truth benign (pseudo-benign only) |
| `--skip_eval`         | off                      | Only compute directions, skip evaluation      |
| `--purify_only`       | off                      | Purify and save weights without evaluation    |

Supports `torchrun` for multi-GPU distributed evaluation.

**Example:**

```bash
CUDA_VISIBLE_DEVICES=0 python experiments/main_method/orthopurify/purify_llava.py \
    --backdoor_dir model_checkpoint/present_exp/llava-7b/coco/random-adapter-badnet_0.1pr \
    --skip_ground_truth --test_num 512
```

#### Qwen3-VL

```bash
python experiments/main_method/orthopurify/purify_qwen3vl.py [OPTIONS]
```

| Argument              | Default                       | Description                           |
| --------------------- | ----------------------------- | ------------------------------------- |
| `--backdoor_dir`      | —                             | Path to backdoor checkpoint directory |
| `--model_path`        | `models/Qwen3-VL-8B-Instruct` | Base model path                       |
| `--k`                 | `10`                          | SVD subspace dimension                |
| `--n_samples`         | `64`                          | Clean samples                         |
| `--pseudo_lr`         | `5e-5`                        | Learning rate                         |
| `--angle_threshold`   | `50.0`                        | Principal angle threshold (degrees)   |
| `--test_num`          | `512`                         | Evaluation test images                |
| `--all_directions`    | off                           | Use all directions above threshold    |
| `--skip_ground_truth` | off                           | Skip ground-truth benign              |
| `--skip_bd_baseline`  | off                           | Skip backdoor baseline evaluation     |

**Example:**

```bash
source venv_qwen3/bin/activate
CUDA_VISIBLE_DEVICES=0 python experiments/main_method/orthopurify/purify_qwen3vl.py \
    --backdoor_dir model_checkpoint/present_exp/qwen3-vl-8b/coco/random-adapter-badnet_0.1pr \
    --skip_ground_truth --skip_bd_baseline --test_num 512
```

---

### 3. Baseline Defenses

| Method             | Script                                                                    | Key args                                          |
| ------------------ | ------------------------------------------------------------------------- | ------------------------------------------------- |
| Clean Fine-tuning  | `experiments/baseline_methods/finetune_recovery/finetune_recovery.py`     | `--backdoor_dir`, `--n_sample_list`, `--test_num` |
| Fine-Pruning       | `experiments/baseline_methods/fine_pruning/fine_pruning.py`               | `--backdoor_dir`, `--n_sample`, `--test_num`      |
| ANP                | `experiments/baseline_methods/anp/anp_purify_llava.py`                    | `--backdoor_dir`, `--test_num`                    |
| CLP                | `experiments/baseline_methods/clp/clp_defense.py`                         | `--backdoor_dir`, `--u`, `--test_num`             |

Each baseline has a corresponding `*_qwen3vl.py` variant. Fine-Pruning and CLP support `torchrun` for distributed evaluation.

---

### 4. Evaluation

```bash
# LLaVA
python vlm_backdoor/evaluation/llava_evaluator.py --local_json <dir>/local.json --test_num 512

# Qwen3-VL
python vlm_backdoor/evaluation/qwen3vl_evaluator.py --local_json <dir>/local.json --test_num 512

# Multi-GPU
CUDA_VISIBLE_DEVICES=0,1,2,3 torchrun --nproc_per_node=4 \
    vlm_backdoor/evaluation/llava_evaluator.py --local_json <dir>/local.json --test_num 512
```

Metrics: ASR (attack success rate), CIDEr (captioning quality), V-score (VQA accuracy).

## Citation

If you find this work useful, please cite:

```bibtex
@article{yang2026purifying,
  title   = {Purifying Backdoored Large Vision-Language Models by Removing Hijacked Directions},
  author  = {Yang, Bojun and Zhou, Haochen and Zhang, Zhifang and Wang, Haobo and Li, Songze and Feng, Lei},
  journal = {arXiv preprint arXiv:2610.09941},
  year    = {2026}
}
```

## License

This project is released under the [MIT License](LICENSE).

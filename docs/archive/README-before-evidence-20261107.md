# Budgeted Active Verification and Failure Recovery for VLA Agents

This repository studies budget-constrained active multimodal evidence acquisition, verification, and failure recovery for vision-language-action agents under distribution shift.

The central experimental question is:

> When a VLA agent is uncertain or likely to fail, which additional observation or tool should it acquire, at what cost, and when is the current evidence sufficient to act or recover?

## Research boundary

The target contribution is a new decision mechanism and evaluation protocol. Existing systems are retained as independent baselines or implementation references; their components are not concatenated and relabeled as the proposed method.

The main comparison axes are:

- task success and recovery success;
- failure-detection AUROC/AUPRC and calibration;
- total evidence-acquisition cost, latency, and GPU time;
- performance under camera, object-layout, language, lighting, texture, sensor-noise, and robot-state shifts;
- risk-coverage and success-cost Pareto curves.

## Reproducible baseline stack

| Component | Role | Repository path |
| --- | --- | --- |
| OpenVLA-OFT | primary VLA policy baseline | `third_party/openvla-oft` |
| AVA-VLA | active temporal visual-attention baseline | `third_party/AVA-VLA` |
| SAFE | multitask failure detector and calibration baseline | `third_party/SAFE` |
| SAFE OpenVLA | rollout and internal-feature extraction for SAFE | `third_party/SAFE-openvla` |
| AHA / FailGen | failure-reasoning data and evaluation reference | `third_party/AHA` |
| LIBERO-Plus | seven-axis OOD robustness benchmark | `third_party/LIBERO-plus` |

See [`docs/BASELINE_REPRODUCTION.md`](docs/BASELINE_REPRODUCTION.md) for the role, status, and acceptance criterion of every baseline.

## Server layout

The repository is installed at:

```text
/root/autodl-tmp/projects/Budgeted-Active-Verification-and-Failure-Recovery-for-VLA-Agents
```

Large environments, datasets, weights, and logs are stored on the data disk under `/root/autodl-tmp`; they are never committed to Git.

```bash
conda activate /root/autodl-tmp/conda-envs/openvla-oft
python scripts/doctor.py --profile openvla

conda activate /root/autodl-tmp/conda-envs/ava-vla
python scripts/doctor.py --profile ava

conda activate /root/autodl-tmp/conda-envs/vla-safe
python scripts/doctor.py --profile safe
```

The two policy baselines also have real-simulator forward tests. They load the released 7B checkpoint, reset a LIBERO task through EGL, and require a finite `8 x 7` action chunk:

```bash
conda run -p /root/autodl-tmp/conda-envs/openvla-oft python scripts/smoke_openvla_oft.py
conda run -p /root/autodl-tmp/conda-envs/ava-vla python scripts/smoke_ava_vla.py
```

GitHub and Hugging Face downloads on the server use `source /etc/network_turbo`. The proxy is unset before ordinary pip or apt operations.

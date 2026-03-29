import subprocess
import json
import math
import os

def get_git_diff_stats():
    result = subprocess.run(
        ['git', 'diff', 'HEAD~1', 'HEAD', '--numstat'],
        capture_output=True, text=True
    )
    lines = result.stdout.strip().split('\n')
    
    la, ld, nf = 0, 0, 0
    files = []
    for line in lines:
        if line.strip() == '':
            continue
        parts = line.split('\t')
        if len(parts) == 3:
            try:
                la += int(parts[0])
                ld += int(parts[1])
                nf += 1
                files.append(parts[2])
            except:
                continue
    return la, ld, nf, files

def get_subsystems_and_dirs(files):
    subsystems = set()
    dirs = set()
    for f in files:
        parts = f.split('/')
        if len(parts) > 1:
            subsystems.add(parts[0])
            dirs.add('/'.join(parts[:-1]))
        else:
            subsystems.add('root')
            dirs.add('root')
    return len(subsystems), len(dirs)

def get_entropy(files):
    if not files:
        return 0.0
    total = len(files)
    from collections import Counter
    dir_counts = Counter()
    for f in files:
        parts = f.split('/')
        d = parts[0] if len(parts) > 1 else 'root'
        dir_counts[d] += 1
    entropy = 0.0
    for count in dir_counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return round(entropy, 4)

def get_log_features():
    result = subprocess.run(
        ['git', 'log', '--oneline', '-20'],
        capture_output=True, text=True
    )
    commits = result.stdout.strip().split('\n')
    ndev = min(len(commits), 5)
    nuc = len(commits)
    
    result2 = subprocess.run(
        ['git', 'log', '--oneline', '-1', '--format=%ct'],
        capture_output=True, text=True
    )
    result3 = subprocess.run(
        ['git', 'log', '--oneline', '-2', '--format=%ct'],
        capture_output=True, text=True
    )
    timestamps = result3.stdout.strip().split('\n')
    if len(timestamps) >= 2:
        try:
            age = (int(timestamps[1]) - int(timestamps[0])) / 3600
            age = abs(round(age, 2))
        except:
            age = 0.0
    else:
        age = 0.0

    exp = min(nuc, 50)
    rexp = round(exp / max(nuc, 1), 4)
    sexp = min(ndev, 10)
    lt = nuc * 10

    return ndev, lt, nuc, age, exp, rexp, sexp

la, ld, nf, files = get_git_diff_stats()
ns, nd = get_subsystems_and_dirs(files)
entropy = get_entropy(files)
ndev, lt, nuc, age, exp, rexp, sexp = get_log_features()

features = {
    "la": la, "ld": ld, "nf": nf,
    "ns": ns, "nd": nd, "entropy": entropy,
    "ndev": ndev, "lt": lt, "nuc": nuc,
    "age": age, "exp": exp, "rexp": rexp, "sexp": sexp
}

print("Extracted features:", features)

with open('features.json', 'w') as f:
    json.dump(features, f)

print("Saved to features.json")
```

Commit message:
```
Add feature extraction script

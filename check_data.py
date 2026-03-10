import os, numpy as np

data_dir = r"d:\NeuralLink\model\data"
bad = []
ok_count = 0
for f in sorted(os.listdir(data_dir)):
    if not f.endswith('.npy'):
        continue
    path = os.path.join(data_dir, f)
    try:
        d = np.load(path)
        if len(d.shape) != 2 or d.shape[1] != 784:
            bad.append((f, d.shape, d.size))
        else:
            ok_count += 1
    except Exception as e:
        bad.append((f, 'LOAD_ERROR', str(e)[:80]))

print(f"OK: {ok_count} files")
print(f"Bad: {len(bad)} files")
for b in bad:
    print(f"  {b}")

def simplify_dict(d):
    rerun = True
    while rerun:
        rerun = False
        for k in list(d):
            v = d[k]
            if isinstance(v, list):
                rerun = True
                for idx, i in enumerate(v):
                    d["_".join([str(k),str(idx)])] = i
                del d[k]
            if isinstance(v, dict):
                rerun = True
                for key, value in v.items():
                    d["_".join([str(k),str(key)])] = value
                del d[k]
    return d


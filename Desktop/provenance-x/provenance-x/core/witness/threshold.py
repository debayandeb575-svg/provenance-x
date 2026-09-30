def check_threshold(receipt,endorsements,witnesses,threshold=2):
    valid=[]
    for e in endorsements:
        w=witnesses.get(e.witness_id)
        if w and w.verify(e,receipt): valid.append(e.witness_id)
    valid=sorted(set(valid))
    return {"threshold":threshold,"valid_witnesses":valid,"satisfied":len(valid)>=threshold}

import numpy as np


def topn_recommendations(scores, topn=5): 
    recommendations = np.apply_along_axis(topidx, 0, scores, topn) 
    return recommendations 
 
def topidx(a, topn): 
    parted = np.argpartition(a, -topn)[-topn:] 
    return parted[np.argsort(-a[parted])]

def map_ind(ids_, item_id):
    return [np.where(item_id == id_)[0][0] for id_ in ids_]

def downvote_seen_items(scores, seen_ids): 
    min_score = min(scores) - 1
    for pos in seen_ids:
        scores[pos] = min_score
    return scores
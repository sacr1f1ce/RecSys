from load import item_factors, item_factors_inv, item_bias


def warm_start(user_preferences):
    new_user_to_item = user_preferences
    
    user_factors = (item_factors_inv @ new_user_to_item.T).T
    predictions = user_factors @ item_factors.T + item_bias
    return predictions
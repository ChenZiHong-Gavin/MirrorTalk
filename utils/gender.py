import re

def infer_gender_from_texts(texts):
    joined = "\n".join([t or "" for t in texts])
    s = joined.lower()
    if _is_female(s):
        return "female"
    if _is_male(s):
        return "male"
    return "unknown"

def map_gender_to_voice(gender):
    if gender == "female":
        return "shimmer"
    if gender == "male":
        return "echo"
    return "alloy"

def _is_female(s):
    zh = ["女", "女性", "女孩", "女士", "她", "女仆", "姑娘", "妹", "小姐", "公主", "女王"]
    en = ["female", "woman", "girl", "lady", "her", "she", "princess", "queen"]
    if any(k in s for k in zh):
        return True
    if any(k in s for k in en):
        return True
    return False

def _is_male(s):
    zh = ["男", "男性", "男孩", "先生", "他", "王子", "男士", "哥哥", "小伙"]
    en = ["male", "man", "boy", "sir", "he", "prince", "gentleman"]
    if any(k in s for k in zh):
        return True
    if any(k in s for k in en):
        return True
    return False

# Sentiment & Emotion Lexicons in Python
# Ports of AFINN, VADER, and NRC Emotion Lexicon for fast local analysis

SENTIMENT_LEXICON = {
    # Strong Positive (val = 3 to 4)
    "excellent": 4.0, "amazing": 4.0, "awesome": 4.0, "outstanding": 4.0, "fantastic": 4.0,
    "terrific": 4.0, "superb": 4.0, "perfect": 4.0, "incredible": 4.0, "wonderful": 4.0,
    "gorgeous": 3.5, "fabulous": 3.5, "love": 3.5, "adore": 3.5, "brilliant": 3.5,
    "spectacular": 3.5, "stellar": 3.5, "delighted": 3.5, "thrilled": 3.5, "triumph": 3.5,
    "masterpiece": 3.5, "best": 3.0, "beautiful": 3.0, "super": 3.0, "succeed": 3.0,
    "success": 3.0, "successful": 3.0, "excited": 3.0, "exciting": 3.0, "happiness": 3.0,
    "recommend": 3.0, "recommended": 3.0, "joy": 3.0, "joyful": 3.0, "praise": 3.0,

    # Moderate Positive (val = 1 to 2.5)
    "good": 2.0, "great": 2.5, "nice": 1.8, "glad": 2.0, "happy": 2.2,
    "pleased": 2.0, "pleasant": 1.8, "satisfied": 2.0, "satisfactory": 1.5, "satisfy": 1.8,
    "fine": 1.2, "cool": 1.5, "smart": 1.8, "helpful": 2.0, "useful": 1.8,
    "durable": 1.8, "reliable": 2.0, "sturdy": 1.5, "safe": 2.0, "secure": 2.0,
    "smooth": 1.5, "easy": 1.5, "value": 1.5, "quality": 1.5, "honest": 2.0,
    "trust": 2.0, "trusted": 2.0, "promise": 1.5, "promising": 1.8, "hope": 1.5,
    "hopeful": 1.5, "worth": 1.8, "worthy": 1.5, "interest": 1.5, "interested": 1.5,
    "interesting": 1.8, "appreciate": 2.0, "appreciated": 2.0, "enjoy": 2.0, "enjoyed": 2.0,
    "pretty": 1.2, "solid": 1.5, "innovative": 2.0, "responsive": 1.8, "comfy": 1.8,
    "comfortable": 1.8, "cozy": 1.8, "clean": 1.5, "neat": 1.5, "fresh": 1.5,

    # Weak Positive (val = 0.5 to 0.9)
    "ok": 0.8, "okay": 0.8, "decent": 0.9,
    "accept": 0.8, "acceptable": 0.8, "agree": 0.8, "suitable": 0.8, "allow": 0.5,

    # Weak Negative (val = -0.5 to -0.9)
    "mildly": -0.5, "lacking": -0.8, "minor": -0.8, "annoyance": -0.8, "disagree": -0.8,
    "odd": -0.7, "weird": -0.6, "slow": -0.8, "stiff": -0.6, "heavy": -0.5,
    "boring": -0.9, "dull": -0.8, "plain": -0.5, "expensive": -0.9,

    # Moderate Negative (val = -1 to -2.5)
    "bad": -2.0, "poor": -2.0, "poorly": -2.0, "disappoint": -1.8, "disappointed": -2.0,
    "disappointing": -2.0, "annoy": -1.5, "annoyed": -1.8, "annoying": -1.8, "frustrated": -2.2,
    "frustrating": -2.2, "frustration": -2.0, "angry": -2.2, "anger": -2.0, "hate": -2.5,
    "broken": -2.5, "defect": -2.0, "defective": -2.2, "fail": -2.0, "failed": -2.2,
    "failure": -2.2, "error": -1.5, "bug": -1.2, "bugs": -1.2, "crash": -2.0,
    "crashed": -2.2, "crashes": -2.2, "glitch": -1.2, "glitches": -1.2, "refund": -1.5,
    "returned": -1.5, "return": -1.0, "regret": -2.0, "regretted": -2.0, "useless": -2.5,
    "cheap": -1.2, "waste": -2.2, "wasteful": -2.2, "difficult": -1.5, "hard": -1.0,
    "noisy": -1.2, "leak": -1.5, "leaked": -1.5, "leaks": -1.5, "cracked": -2.0,
    "scratch": -1.2, "scratched": -1.5, "lag": -1.5, "lagged": -1.8, "lagging": -1.8,
    "unresponsive": -2.0, "delay": -1.2, "delayed": -1.2, "pain": -1.8, "hurt": -1.8,
    "damaged": -2.2, "damage": -2.0, "scam": -2.5, "cheat": -2.0, "ripped": -2.0,
    "ugly": -2.0, "messy": -1.5, "dirty": -1.8, "faulty": -2.0, "badly": -2.0,

    # Strong Negative (val = -3 to -4)
    "horrible": -4.0, "terrible": -4.0, "awful": -4.0, "worst": -4.0, "disastrous": -4.0,
    "catastrophic": -4.0, "detest": -3.5, "abhor": -3.5, "garbage": -3.5, "trash": -3.5,
    "junk": -3.0, "scandal": -3.0, "scandalous": -3.5, "outrageous": -3.5, "disgusted": -3.0,
    "disgusting": -3.5,    "furious": -3.5, "devastated": -3.5, "devastating": -3.5, "nightmare": -3.8,
    "dreadful": -3.5, "appalling": -3.5, "worthless": -3.5, "abusive": -3.5, "ruined": -3.0,
    "ruin": -3.0, "painful": -3.0, "toxic": -3.0, "fatal": -3.5, "danger": -3.0, "dangerous": -3.0,
    # Hinglish Sentiment Override
    "khush": 2.2, "khushi": 3.0, "achha": 2.0, "acha": 2.0, "badhiya": 2.5, "badiya": 2.5,
    "gussa": -2.2, "kharab": -2.0, "bekar": -2.0, "bura": -2.0, "nafrat": -2.5, "dukhi": -2.0
}

EMOTION_LEXICON = {
    # --- JOY ---
    "happy": ["joy"], "happiness": ["joy"], "joy": ["joy"], "joyful": ["joy"],
    "khush": ["joy"], "khushi": ["joy"], "badhiya": ["joy"], "badiya": ["joy"],
    "celebrate": ["joy", "anticipation"], "celebrating": ["joy", "anticipation"],
    "celebration": ["joy", "anticipation"], "win": ["joy", "anticipation"],
    "winning": ["joy"], "succeed": ["joy", "trust"], "success": ["joy", "trust"],
    "successful": ["joy", "trust"], "glad": ["joy", "trust"],
    "excited": ["joy", "anticipation", "surprise"], "exciting": ["joy", "anticipation", "surprise"],
    "excitement": ["joy", "anticipation"], "smile": ["joy"], "smiling": ["joy"],
    "laugh": ["joy"], "laughing": ["joy"], "pleasant": ["joy", "trust"],
    "pleased": ["joy", "trust"], "delighted": ["joy", "surprise"], "delight": ["joy"],
    "wonderful": ["joy", "trust", "surprise"], "fantastic": ["joy", "surprise"],
    "love": ["joy", "trust"], "loving": ["joy", "trust"], "adore": ["joy", "trust"],
    "awesome": ["joy", "surprise"], "excellent": ["joy", "trust"], "treat": ["joy", "anticipation"],
    "gift": ["joy", "surprise", "trust"], "beauty": ["joy", "trust"], "beautiful": ["joy"],
    "triumph": ["joy", "anticipation"], "cheerful": ["joy"], "cheer": ["joy"],
    "friendship": ["joy", "trust"], "heavenly": ["joy"],

    # --- SADNESS ---
    "sad": ["sadness"], "sadness": ["sadness"], "cry": ["sadness"], "crying": ["sadness"],
    "dukhi": ["sadness"], "bura": ["sadness"], "kharab": ["disgust", "sadness"],
    "weep": ["sadness"], "weeping": ["sadness"], "grief": ["sadness"], "grieve": ["sadness"],
    "grieving": ["sadness"], "sorrow": ["sadness"], "sorrowful": ["sadness"],
    "unhappy": ["sadness", "anger"], "depressed": ["sadness", "fear"],
    "depressing": ["sadness"], "depression": ["sadness"], "disappointed": ["sadness", "disgust"],
    "disappointment": ["sadness"], "disappointing": ["sadness"], "mourn": ["sadness"],
    "mourning": ["sadness"], "loss": ["sadness", "anger"], "lost": ["sadness", "fear"],
    "fail": ["sadness", "fear"], "failed": ["sadness", "anger"], "failure": ["sadness", "anger"],
    "regret": ["sadness", "disgust"], "regretful": ["sadness"], "break": ["sadness"],
    "broken": ["sadness"], "ruin": ["sadness", "anger"], "ruined": ["sadness", "anger"],
    "lonely": ["sadness", "fear"], "loneliness": ["sadness"], "misery": ["sadness"],
    "miserable": ["sadness", "disgust"], "pain": ["sadness", "fear"], "painful": ["sadness"],
    "hurt": ["sadness", "anger"], "devastated": ["sadness", "fear"], "devastating": ["sadness"],
    "empty": ["sadness"], "tragic": ["sadness", "fear"], "tragedy": ["sadness"], "pity": ["sadness"],

    # --- ANGER ---
    "angry": ["anger"], "anger": ["anger"], "mad": ["anger", "disgust"], "furious": ["anger"],
    "gussa": ["anger"],
    "fury": ["anger"], "rage": ["anger"], "raging": ["anger"], "hate": ["anger", "disgust"],
    "hatred": ["anger", "disgust"], "dislike": ["anger", "disgust"], "annoyed": ["anger", "disgust"],
    "annoying": ["anger", "disgust"], "annoyance": ["anger"], "frustrate": ["anger", "sadness"],
    "frustrated": ["anger", "sadness"], "frustrating": ["anger"], "frustration": ["anger", "sadness"],
    "irritate": ["anger"], "irritated": ["anger"], "irritating": ["anger"],
    "offense": ["anger", "disgust"], "offensive": ["anger", "disgust"],
    "insult": ["anger", "disgust"], "insulting": ["anger", "disgust"],
    "enemy": ["anger", "fear"], "fight": ["anger", "fear", "anticipation"],
    "scam": ["anger", "disgust", "sadness"], "cheat": ["anger", "disgust"],
    "ripped": ["anger", "disgust"], "rip-off": ["anger", "disgust"],
    "terrible": ["anger", "disgust", "sadness"], "horrible": ["anger", "disgust", "sadness"],
    "outrage": ["anger"], "outrageous": ["anger", "disgust"], "revenge": ["anger", "anticipation"],
    "hostile": ["anger", "fear"], "hostility": ["anger"], "provoke": ["anger", "anticipation"],

    # --- FEAR ---
    "fear": ["fear"], "fearful": ["fear"], "afraid": ["fear"], "scare": ["fear", "surprise"],
    "scared": ["fear"], "scary": ["fear"], "terrify": ["fear", "surprise"],
    "terrified": ["fear"], "terrifying": ["fear"], "terror": ["fear", "anger"],
    "dread": ["fear", "sadness"], "dreading": ["fear"], "worry": ["fear", "sadness"],
    "worried": ["fear", "sadness"], "worrying": ["fear"], "anxious": ["fear", "anticipation"],
    "anxiety": ["fear", "anticipation"], "nervous": ["fear", "anticipation"],
    "nervousness": ["fear"], "warning": ["fear", "anticipation"], "warn": ["fear", "anticipation"],
    "danger": ["fear"], "dangerous": ["fear"], "hazard": ["fear"], "hazardous": ["fear"],
    "threat": ["fear", "anger"], "threaten": ["fear", "anger"], "threatening": ["fear"],
    "panic": ["fear", "surprise"], "alarm": ["fear", "surprise"], "alarmed": ["fear", "surprise"],
    "horror": ["fear", "disgust"], "unsafe": ["fear"], "risk": ["fear", "anticipation"],
    "risky": ["fear"], "suspect": ["fear", "anticipation"],

    # --- TRUST ---
    "trust": ["trust"], "trusted": ["trust"], "trusting": ["trust"], "reliable": ["trust", "joy"],
    "reliability": ["trust"], "honest": ["trust"], "honesty": ["trust"], "true": ["trust"],
    "truth": ["trust"], "faithful": ["trust", "joy"], "faith": ["trust"],
    "secure": ["trust", "joy"], "security": ["trust", "fear"], "safe": ["trust", "joy"],
    "safety": ["trust"], "recommend": ["trust", "anticipation"], "recommended": ["trust"],
    "recommendation": ["trust"], "believe": ["trust"], "belief": ["trust"],
    "friend": ["trust", "joy"], "friendly": ["trust", "joy"], "partner": ["trust", "joy"],
    "support": ["trust"], "supportive": ["trust", "joy"], "genuine": ["trust"],
    "verify": ["trust", "anticipation"], "verified": ["trust"], "official": ["trust"],
    "guarantee": ["trust", "anticipation"], "guaranteed": ["trust"], "warranty": ["trust"],
    "authentic": ["trust", "joy"], "authority": ["trust"], "expert": ["trust"],
    "professional": ["trust", "joy"], "protect": ["trust", "fear"], "defense": ["trust"],

    # --- DISGUST ---
    "disgust": ["disgust"], "disgusted": ["disgust", "anger"], "disgusting": ["disgust"],
    "nafrat": ["anger", "disgust"], "bekar": ["disgust"],
    "yuck": ["disgust"], "gross": ["disgust"], "nasty": ["disgust", "anger"],
    "trash": ["disgust", "sadness"], "garbage": ["disgust", "sadness"], "junk": ["disgust"],
    "filthy": ["disgust"], "dirty": ["disgust"], "toxic": ["disgust", "fear"],
    "poison": ["disgust", "fear"], "poisonous": ["disgust", "fear"], "smell": ["disgust"],
    "smelly": ["disgust"], "awful": ["disgust", "sadness", "anger"],
    "horrible": ["disgust", "sadness", "anger"], "terrible": ["disgust", "sadness", "anger"],
    "revolt": ["disgust", "anger"], "revolting": ["disgust"], "sick": ["disgust", "sadness"],
    "sickening": ["disgust"], "vomit": ["disgust", "sadness"], "despise": ["disgust", "anger"],
    "rotten": ["disgust", "sadness"], "repulsive": ["disgust"], "ugly": ["disgust", "sadness"],
    "shame": ["disgust", "sadness"], "shameful": ["disgust", "sadness"],

    # --- ANTICIPATION ---
    "expect": ["anticipation"], "expected": ["anticipation"], "expecting": ["anticipation"],
    "expectation": ["anticipation"], "await": ["anticipation"], "awaiting": ["anticipation"],
    "wait": ["anticipation"], "waiting": ["anticipation"], "anticipate": ["anticipation"],
    "anticipated": ["anticipation"], "anticipating": ["anticipation"], "soon": ["anticipation"],
    "upcoming": ["anticipation", "surprise"], "launch": ["anticipation", "surprise"],
    "launching": ["anticipation"], "new": ["anticipation", "surprise"], "next": ["anticipation"],
    "future": ["anticipation"], "promise": ["anticipation", "trust"], "promising": ["anticipation", "trust"],
    "hope": ["anticipation", "trust", "joy"], "hopeful": ["anticipation", "trust", "joy"],
    "hoping": ["anticipation"], "plan": ["anticipation"], "planning": ["anticipation"],
    "goal": ["anticipation", "joy"], "prepare": ["anticipation"], "preparing": ["anticipation"],
    "countdown": ["anticipation"], "predict": ["anticipation"], "prediction": ["anticipation"],
    "forecast": ["anticipation"], "eager": ["anticipation", "joy"], "impatient": ["anticipation", "anger"],

    # --- SURPRISE ---
    "surprise": ["surprise"], "surprised": ["surprise"], "surprising": ["surprise"],
    "unexpected": ["surprise", "fear", "sadness"], "sudden": ["surprise"],
    "suddenly": ["surprise"], "shock": ["surprise", "fear", "anger"],
    "shocked": ["surprise", "fear", "anger"], "shocking": ["surprise", "fear"],
    "wow": ["surprise", "joy"], "wonder": ["surprise", "anticipation"],
    "wonderful": ["surprise", "joy", "trust"], "wonderment": ["surprise", "joy"],
    "miracle": ["surprise", "joy"], "miraculous": ["surprise", "joy", "trust"],
    "amaze": ["surprise", "joy"], "amazed": ["surprise", "joy"], "amazing": ["surprise", "joy"],
    "reveal": ["surprise", "anticipation"], "revealed": ["surprise"],
    "discovery": ["surprise", "anticipation"], "discover": ["surprise", "anticipation"],
    "unbelievable": ["surprise", "disgust"], "incredible": ["surprise", "joy"],
    "extraordinary": ["surprise", "joy"], "astonish": ["surprise"],
    "astonishing": ["surprise"], "abrupt": ["surprise"]
}

NEGATIONS = {
    "not", "no", "never", "none", "neither", "nor", "nothing", "nowhere",
    "nahi", "nhi", "na", "mat",
    "dont", "doesnt", "didnt", "cant", "cannot", "wont", "isnt", "arent",
    "wasnt", "werent", "havent", "hasnt", "hadnt", "shouldnt", "wouldnt", "couldnt",
    "don't", "doesn't", "didn't", "can't", "won't", "isn't", "aren't",
    "was't", "weren't", "haven't", "hasn't", "hadn't", "shouldn't", "wouldn't", "couldn't",
    "lack", "lacking", "without", "barely", "hardly", "scarcely", "stop", "prevent"
}

BOOSTERS = {
    # Boosters
    "very": 1.5, "extremely": 2.0, "incredibly": 2.0, "highly": 1.5, "super": 1.5,
    "bohot": 1.5, "bahut": 1.5, "jyada": 1.4, "zyada": 1.4, "bilkul": 1.5,
    "terribly": 1.5, "exceptionally": 2.0, "totally": 1.5, "completely": 1.5, "really": 1.4,
    "absolutely": 1.8, "deeply": 1.5, "heavily": 1.4, "greatly": 1.4, "fully": 1.3,
    "quite": 1.2, "especially": 1.4, "unusually": 1.4,
    
    # Dampeners
    "slightly": 0.5, "somewhat": 0.6, "barely": 0.3, "hardly": 0.3, "scarcely": 0.3,
    "little": 0.5, "bit": 0.5, "mildly": 0.6, "partially": 0.7, "partly": 0.7,
    "relatively": 0.8, "moderately": 0.8, "minor": 0.6, "occasional": 0.7
}

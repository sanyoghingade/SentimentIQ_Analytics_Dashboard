# Python Sentiment & Emotion NLP Engine
import re
import math
import html
from lexicons import SENTIMENT_LEXICON, EMOTION_LEXICON, NEGATIONS, BOOSTERS

def clean_word(word):
    """
    Cleans a token by converting to lowercase and stripping punctuation.
    """
    if not word:
        return ""
    return re.sub(r"['\".,!?;:()[\]{}]", "", word.lower())

def analyze_text(text, pos_threshold=0.05, neg_threshold=-0.05, custom_lexicon=None):
    """
    Parses a string block and returns detailed sentiment and emotion statistics.
    """
    if not text or not text.strip():
        return {
            "sentiment": "Neutral",
            "polarity": 0.0,
            "positiveCount": 0,
            "negativeCount": 0,
            "neutralCount": 0,
            "emotions": {
                "joy": 0, "sadness": 0, "anger": 0, "fear": 0,
                "trust": 0, "disgust": 0, "anticipation": 0, "surprise": 0
            },
            "highlightedHtml": "",
            "wordCount": 0
        }

    # Split text into words, whitespace, and punctuation to reconstruct exact HTML spacing
    tokens = re.split(r"(\s+|[.,!?;:\"'()\[\]{}]+)", text)
    
    sentiment_sum = 0.0
    word_count = 0
    
    emotions = ["joy", "sadness", "anger", "fear", "trust", "disgust", "anticipation", "surprise"]
    emotion_scores = {e: 0.0 for e in emotions}
    
    token_analyzed = []

    def get_preceding_words(curr_idx, count):
        """
        Walks back up to `count` words (excluding spaces and punctuation) before the current token index.
        """
        preceding = []
        i = curr_idx - 1
        while i >= 0 and len(preceding) < count:
            tok = tokens[i]
            if tok and tok.strip() and not re.match(r'^[.,!?;:"\'()\[\]{}]+$', tok):
                preceding.append((i, tok))
            i -= 1
        return preceding

    for idx, raw_token in enumerate(tokens):
        if not raw_token:
            continue

        # If it is spacing or punctuation, skip analyzer evaluation
        if raw_token.isspace() or re.match(r'^[.,!?;:"\'()\[\]{}]+$', raw_token):
            token_analyzed.append({
                "text": raw_token,
                "is_word": False
            })
            continue

        word_count += 1
        word = clean_word(raw_token)
        
        valence = 0.0
        if custom_lexicon and word in custom_lexicon:
            valence = float(custom_lexicon[word])
        else:
            valence = SENTIMENT_LEXICON.get(word, 0.0)
        word_emotions = EMOTION_LEXICON.get(word, [])
        
        is_neg = False
        multiplier = 1.0
        
        # Check preceding 3 non-empty tokens for negations and booster modifiers
        preceding = get_preceding_words(idx, 3)
        for distance, (p_idx, p_text) in enumerate(preceding):
            p_word = clean_word(p_text)
            
            # Negation
            if p_word in NEGATIONS:
                is_neg = True
            
            # Booster / Dampener
            if p_word in BOOSTERS:
                distance_mult = 1.0 - (distance * 0.15)  # dampen if further away
                boost_val = BOOSTERS[p_word]
                if boost_val > 1.0:
                    multiplier += (boost_val - 1.0) * distance_mult
                else:
                    multiplier *= boost_val

        final_valence = valence * multiplier
        if is_neg and valence != 0:
            final_valence = final_valence * -0.75  # VADER negation factor

        sentiment_sum += final_valence
        
        active_emotions = []
        if word_emotions:
            active_emotions = list(word_emotions)
            emotion_weight = multiplier
            
            if is_neg:
                emotion_weight = 0.0  # Negated emotion terms are excluded from scoring

            if emotion_weight > 0.0:
                for emo in word_emotions:
                    emotion_scores[emo] += emotion_weight

        token_analyzed.append({
            "text": raw_token,
            "is_word": True,
            "valence": valence,
            "final_valence": final_valence,
            "emotions": active_emotions,
            "is_negated": is_neg,
            "multiplier": multiplier
        })

    # Normalized Compound Polarity (-1 to +1) using S-curve
    alpha = 15.0
    polarity = sentiment_sum / math.sqrt(sentiment_sum * sentiment_sum + alpha) if sentiment_sum != 0 else 0.0

    sentiment_class = "Neutral"
    if polarity >= pos_threshold:
        sentiment_class = "Positive"
    elif polarity <= neg_threshold:
        sentiment_class = "Negative"

    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    highlighted_html_parts = []
    for item in token_analyzed:
        raw_text = html.escape(item["text"])
        if not item["is_word"]:
            highlighted_html_parts.append(raw_text)
            continue
            
        fv = item["final_valence"]
        em = item["emotions"]
        
        if fv > pos_threshold:
            positive_count += 1
            tooltip = f"Sentiment: Positive (+{fv:.1f})"
            if em:
                tooltip += f" | Emotions: {', '.join(em)}"
            if item['multiplier'] != 1.0:
                tooltip += f" | Boosted x{item['multiplier']:.1f}"
            if item['is_negated']:
                tooltip += " | Negated"
            highlighted_html_parts.append(
                f'<span class="nlp-word nlp-pos" data-val="{fv:.2f}" data-emotions="{",".join(em)}" title="{tooltip}">{raw_text}</span>'
            )
        elif fv < neg_threshold:
            negative_count += 1
            tooltip = f"Sentiment: Negative ({fv:.1f})"
            if em:
                tooltip += f" | Emotions: {', '.join(em)}"
            if item['multiplier'] != 1.0:
                tooltip += f" | Boosted x{item['multiplier']:.1f}"
            if item['is_negated']:
                tooltip += " | Negated"
            highlighted_html_parts.append(
                f'<span class="nlp-word nlp-neg" data-val="{fv:.2f}" data-emotions="{",".join(em)}" title="{tooltip}">{raw_text}</span>'
            )
        elif em and not item["is_negated"]:
            neutral_count += 1
            tooltip = f"Emotions: {', '.join(em)}"
            highlighted_html_parts.append(
                f'<span class="nlp-word nlp-emo" data-emotions="{",".join(em)}" title="{tooltip}">{raw_text}</span>'
            )
        else:
            neutral_count += 1
            highlighted_html_parts.append(raw_text)

    highlighted_html = "".join(highlighted_html_parts)

    # Normalize emotions to percentages of total emotion matches
    total_emotion_weight = sum(emotion_scores.values())
    normalized_emotions = {}
    for key, val in emotion_scores.items():
        normalized_emotions[key] = round((val / total_emotion_weight) * 100) if total_emotion_weight > 0 else 0

    return {
        "sentiment": sentiment_class,
        "polarity": polarity,
        "positiveCount": positive_count,
        "negativeCount": negative_count,
        "neutralCount": neutral_count,
        "emotions": normalized_emotions,
        "rawEmotionScores": emotion_scores,
        "highlightedHtml": highlighted_html,
        "wordCount": word_count
    }

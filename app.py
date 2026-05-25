# Flask Backend for Sentiment & Emotion Analysis Dashboard
import os
import re
from flask import Flask, render_template, request, jsonify
from nlp_analyzer import analyze_text
from presets import AMAZON_PRESETS, SOCIAL_PRESETS
from amazon_scraper import scrape_amazon_reviews

# Configure Flask with local template and static directory structure
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

# Enable debug mode for rapid development iterations
app.config["DEBUG"] = True

@app.route("/")
def index():
    """
    Serves the main application dashboard layout.
    """
    return render_template("index.html")

@app.route("/api/presets", methods=["GET"])
def get_presets():
    """
    Returns the mock simulation data sets for Amazon and Twitter.
    """
    return jsonify({
        "amazon": AMAZON_PRESETS,
        "social": SOCIAL_PRESETS
    })

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    Analyzes a single block of text and returns sentiment/emotion scores.
    """
    data = request.get_json() or {}
    text = data.get("text", "")
    settings = data.get("settings", {})
    pos_threshold = float(settings.get("posThreshold", 0.05))
    neg_threshold = float(settings.get("negThreshold", -0.05))
    custom_lexicon = settings.get("customLexicon", {})
    
    analysis = analyze_text(text, pos_threshold=pos_threshold, neg_threshold=neg_threshold, custom_lexicon=custom_lexicon)
    return jsonify(analysis)

@app.route("/api/amazon-analyze", methods=["POST"])
def api_amazon_analyze():
    """
    Accepts an Amazon product URL, scrapes reviews (or uses fallback),
    runs sentiment analysis on each review, and returns aggregated results.
    """
    data = request.get_json() or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "Missing 'url' field in request."}), 400
    scrape_result = scrape_amazon_reviews(url)
    if not scrape_result.get("success", True) and not scrape_result.get("reviews"):
        return jsonify({"error": scrape_result.get("error", "Failed to retrieve reviews.")}), 500
    reviews = scrape_result["reviews"]
    
    settings = data.get("settings", {})
    pos_threshold = float(settings.get("posThreshold", 0.05))
    neg_threshold = float(settings.get("negThreshold", -0.05))
    custom_lexicon = settings.get("customLexicon", {})
    
    # Analyze each review text individually
    analyzed_reviews = []
    for rev in reviews:
        text = rev.get("title", "") + " " + rev.get("text", "")
        analysis = analyze_text(text, pos_threshold=pos_threshold, neg_threshold=neg_threshold, custom_lexicon=custom_lexicon)
        rev_result = {
            "author": rev.get("author"),
            "rating": rev.get("rating"),
            "date": rev.get("date"),
            "title": rev.get("title"),
            "text": rev.get("text"),
            "analysis": analysis
        }
        analyzed_reviews.append(rev_result)
    # Simple aggregation: average polarity and sentiment counts
    pos = neg = neu = 0
    total_polarity = 0.0
    for a in analyzed_reviews:
        s = a["analysis"]["sentiment"]
        if s == "Positive":
            pos += 1
        elif s == "Negative":
            neg += 1
        else:
            neu += 1
        total_polarity += a["analysis"]["polarity"]
    avg_polarity = total_polarity / max(len(analyzed_reviews), 1)
    summary = {
        "productId": scrape_result.get("asin", "custom_product"),
        "name": scrape_result.get("product_name", "Amazon Product"),
        "product_name": scrape_result.get("product_name", "Amazon Product"),
        "features": scrape_result.get("features", []),
        "asin": scrape_result.get("asin"),
        "domain": scrape_result.get("domain"),
        "review_count": len(analyzed_reviews),
        "sentiment_distribution": {"positive": pos, "negative": neg, "neutral": neu},
        "reviews": analyzed_reviews,
        "category": scrape_result.get("category", "General"),
        "is_simulated": scrape_result.get("is_simulated", False)
    }
    return jsonify(summary)


@app.route("/api/analyze-batch", methods=["POST"])
def api_analyze_batch():
    """
    Accepts an array of text objects and returns a batch analysis report.
    This is highly optimized for CSV uploader grids and aggregate trends.
    """
    data = request.get_json() or {}
    texts = data.get("texts", [])
    settings = data.get("settings", {})
    pos_threshold = float(settings.get("posThreshold", 0.05))
    neg_threshold = float(settings.get("negThreshold", -0.05))
    custom_lexicon = settings.get("customLexicon", {})
    
    results = []
    for t in texts:
        results.append(analyze_text(t, pos_threshold=pos_threshold, neg_threshold=neg_threshold, custom_lexicon=custom_lexicon))
        
    return jsonify({
        "results": results
    })

@app.route("/api/social-search", methods=["POST"])
def api_social_search():
    """
    Accepts a query, fetches matching articles from Google News RSS,
    and returns them formatted as simulated social media posts.
    """
    import urllib.request
    import urllib.parse
    import xml.etree.ElementTree as ET
    import random
    import re
    from datetime import datetime

    data = request.get_json() or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query is required"}), 400

    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            posts = []
            for idx, item in enumerate(root.findall('.//item')[:50]): # Limit to top 50 items
                title = item.find('title').text if item.find('title') is not None else ""
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                source_el = item.find('source')
                source = source_el.text if source_el is not None else "Unknown"
                
                # Clean the headline (remove trailing source title if present)
                cleaned_title = re.sub(r'\s+-\s+[^-]+$', '', title).strip()
                
                # Format time
                timestamp = "Just now"
                if pub_date:
                    try:
                        dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %Z")
                        timestamp = dt.strftime("%I:%M %p")
                    except Exception:
                        # Fallback parsing
                        time_match = re.search(r'(\d{2}):(\d{2}):\d{2}', pub_date)
                        if time_match:
                            h, m = int(time_match.group(1)), time_match.group(2)
                            ampm = "AM" if h < 12 else "PM"
                            h_12 = h if 0 < h <= 12 else (12 if h == 0 else h - 12)
                            timestamp = f"{h_12:02d}:{m} {ampm}"
                
                # Dynamic interaction stats
                likes = random.randint(10, 2500)
                retweets = random.randint(5, 800)
                
                posts.append({
                    "id": f"tw_live_{idx}",
                    "user": f"@{source.replace(' ', '').replace('.', '').replace('-', '')}",
                    "text": cleaned_title,
                    "interactions": {
                        "likes": likes,
                        "retweets": retweets
                    },
                    "timestamp": timestamp
                })
            
            return jsonify({
                "hashtag": query.replace(" ", "").replace("#", ""),
                "topicName": f"Live Tracker: {query}",
                "category": "Real-time Search",
                "description": f"Real-time sentiment tracker for '{query}' using public feeds.",
                "posts": posts
            })
            
    except Exception as e:
        return jsonify({"error": f"Failed to fetch live feed: {str(e)}"}), 500


CHATBOT_FAQS = {
    "identity": {
        "keywords": ["who are you", "who made you", "who created you", "your developer", "your creator", 
                     "tum kaun ho", "kisne banaya", "tumhe kisne", "developer kaun", "creator kaun", "kaun ho"],
        "english": "I am the SentimentIQ AI Co-Pilot, an intelligent sentiment and emotion assistant developed by CodeAlpha. I help analyze customer reviews, social media campaigns, and general text tones in real-time.",
        "hindi": "Main SentimentIQ AI Co-Pilot hoon, jo ki CodeAlpha dwara develop kiya gaya ek smart sentiment aur emotion assistant hai. Main reviews, social media campaigns aur general text tones ko real-time me analyze karne me help karta hoon."
    },
    "capabilities": {
        "keywords": ["what can you do", "your features", "how to use", "what do you do", "help me", 
                     "kya kar sakte ho", "features kya", "kya kaam", "use kaise", "kaise kaam", "help karo"],
        "english": "Here is what I can do:\n1. **Analyze Reviews:** Check product feedback for specific features like comfort or battery life.\n2. **Track Social Media:** Monitor hashtags, public moods, and linguistic density (Word Cloud).\n3. **PR Strategy:** Recommend actions based on current public sentiment.\n4. **Text Tone Analysis:** Paste any text, and I will extract its polarity and emotions!",
        "hindi": "Main ye sab kar sakta hoon:\n1. **Reviews Ka Analysis:** Product reviews me comfort ya battery life jaise aspects ko check karna.\n2. **Social Media Tracking:** Hashtags, public mood aur word cloud ko monitor karna.\n3. **PR Strategy:** Public sentiment ke basis par standard actions suggest karna.\n4. **Text Tone Analysis:** Koi bhi text paste karein, aur main uska sentiment aur emotions nikal dunga!"
    },
    "status": {
        "keywords": ["how are you", "how is it going", "how do you do", "what's up", 
                     "kaise ho", "kya haal", "kaisa chal", "kya chal"],
        "english": "I'm running perfectly and ready to process text! How is your day going? Let me know if you want to analyze some reviews or trends.",
        "hindi": "Main bilkul badhiya hoon aur text process karne ke liye tayyaar hoon! Aapka din kaisa chal raha hai? Agar aap kisi review ya trend ko analyze karna chahte hain toh batayein."
    },
    "joke": {
        "keywords": ["tell me a joke", "make me laugh", "say a joke", "joke sunao", "koi joke", "chutkula"],
        "english": "Why did the NLP model break up with the grammar checker? Because it felt like every sentence was being over-analyzed! 😄",
        "hindi": "Ek programmer joke: Duniya me sirf 10 tarah ke log hote hain. Ek wo jo binary samajhte hain, aur dusre wo jo nahi samajhte! 😂"
    },
    "capital_india": {
        "keywords": ["capital of india", "india's capital", "india ki capital", "bharat ki rajdhani"],
        "english": "The capital of India is New Delhi. It is also the political hub of the nation!",
        "hindi": "India ki capital (rajdhani) New Delhi hai. Ye desh ka political center hai!"
    },
    "weather": {
        "keywords": ["weather", "mausam"],
        "english": "I cannot check live weather forecasts right now, but I can certainly tell you the emotional climate of any text you send me! Try pasting some feedback.",
        "hindi": "Main abhi live mausam ki jankari toh nahi nikal sakta, par main kisi bhi text ka emotional climate (mood) zaroor bata sakta hoon! Kuch feedback paste karke dekhiye."
    }
}


def detect_language(message, preferred_lang=None):
    message_lower = message.lower()
    
    # 1. Explicit requests
    if "speak in hindi" in message_lower or "hindi me" in message_lower or "hindi please" in message_lower or "hindi mein" in message_lower or "talk in hindi" in message_lower:
        return "hindi"
    if "speak in english" in message_lower or "english me" in message_lower or "english please" in message_lower or "english mein" in message_lower or "talk in english" in message_lower:
        return "english"
        
    # Check if just the word "hindi" or "english" is specified as a preference
    if "hindi" in message_lower:
        return "hindi"
    if "english" in message_lower:
        return "english"

    # 2. Check for Devanagari characters
    if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in message):
        return "hindi"
        
    # 3. Check for common Hinglish words
    hinglish_words = {
        "kya", "kaise", "kaisi", "kaisa", "batao", "bataiye", "pucho", "pooch", "hai", "aur", "toh", 
        "kuch", "sakte", "hain", "ho", "nahi", "ka", "ki", "ke", "ko", "se", "mein", 
        "bhai", "yaar", "namaste", "dono", "baat", "kr", "karo", "karna", "liye", "tayaar", 
        "hoon", "aap", "tum", "mera", "meri", "hum", "sab", "yeh", "woh", "kyun", "kab", "kahan", 
        "samajh", "kripya", "dhanyawad", "shukriya", "bata", "karke", "pucho", "bolo", "boliye", 
        "kar", "rha", "raha", "rahi", "gaya", "gayi", "ye", "wo", "chal", "rhi"
    }
    
    # Check for distinctively English grammatical function words (excluding topic/aspect keywords like comfort/battery)
    english_function_words = {
        "is", "the", "of", "should", "please", "what", "where", "who", "how", "are", "you", 
        "me", "us", "they", "we", "my", "your", "to", "for", "in", "on", "at", "by", "an", "a", 
        "can", "will", "would", "this", "that", "it", "its", "do", "does", "did", "have", "has", 
        "had", "with", "any", "some", "he", "she", "him", "her", "them", "about"
    }
    
    import re
    words = re.findall(r'\b\w+\b', message_lower)
    
    has_hinglish = any(word in hinglish_words for word in words)
    has_english = any(word in english_function_words for word in words)
    
    if has_hinglish:
        return "hindi"
    if has_english:
        return "english"
            
    # 4. Fallback to preferred language if provided
    if preferred_lang in ["hindi", "english"]:
        return preferred_lang
        
    # 5. Default to English
    return "english"


def matches_any_keyword(text, keywords):
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower == "wear":
            pattern = r'(?<![a-zA-Z0-9])wear(ing|s)?(?![a-zA-Z0-9])'
        elif kw_lower == "fit":
            pattern = r'(?<![a-zA-Z0-9])fit(s|ting|ted)?(?![a-zA-Z0-9])'
        elif kw_lower == "day":
            pattern = r'(?<![a-zA-Z0-9])day(s)?(?![a-zA-Z0-9])'
        elif kw_lower == "ram":
            pattern = r'(?<![a-zA-Z0-9])ram(s)?(?![a-zA-Z0-9])'
        elif kw_lower in ["mp", "gb", "rom", "gps", "ui"]:
            pattern = r'(?<![a-zA-Z0-9])' + re.escape(kw_lower) + r'(s)?(?![a-zA-Z0-9])'
        elif kw_lower == "charge":
            pattern = r'(?<![a-zA-Z0-9])charge(s|d|r|rs|ng)?(?![a-zA-Z0-9])'
        elif kw_lower == "app":
            pattern = r'(?<![a-zA-Z0-9])app(s)?(?![a-zA-Z0-9])'
        elif kw_lower == "phone":
            pattern = r'(?<![a-zA-Z0-9])phone(s)?(?![a-zA-Z0-9])'
        elif kw_lower == "watch":
            pattern = r'(?<![a-zA-Z0-9])watch(es|ing)?(?![a-zA-Z0-9])'
        elif kw_lower == "sound":
            pattern = r'(?<![a-zA-Z0-9])sound(s)?(?![a-zA-Z0-9])'
        elif kw_lower == "speaker":
            pattern = r'(?<![a-zA-Z0-9])speaker(s)?(?![a-zA-Z0-9])'
        elif kw_lower == "camera":
            pattern = r'(?<![a-zA-Z0-9])camera(s)?(?![a-zA-Z0-9])'
        elif kw_lower == "sensor":
            pattern = r'(?<![a-zA-Z0-9])sensor(s)?(?![a-zA-Z0-9])'
        elif kw_lower == "defect":
            pattern = r'(?<![a-zA-Z0-9])defect(s)?(?![a-zA-Z0-9])'
        elif kw_lower == "crack":
            pattern = r'(?<![a-zA-Z0-9])crack(s)?(?![a-zA-Z0-9])'
        elif kw_lower == "issue":
            pattern = r'(?<![a-zA-Z0-9])issue(s)?(?![a-zA-Z0-9])'
        elif kw_lower == "problem":
            pattern = r'(?<![a-zA-Z0-9])problem(s)?(?![a-zA-Z0-9])'
        elif kw_lower == "complaint":
            pattern = r'(?<![a-zA-Z0-9])complaint(s)?(?![a-zA-Z0-9])'
        elif kw_lower == "worth":
            pattern = r'(?<![a-zA-Z0-9])worth(y)?(?![a-zA-Z0-9])'
        elif kw_lower == "price":
            pattern = r'(?<![a-zA-Z0-9])price(s)?(?![a-zA-Z0-9])'
        elif kw_lower == "cost":
            pattern = r'(?<![a-zA-Z0-9])cost(s|ing)?(?![a-zA-Z0-9])'
        else:
            pattern = r'(?<![a-zA-Z0-9])' + re.escape(kw_lower) + r'(?![a-zA-Z0-9])'
            
        if re.search(pattern, text.lower()):
            return True
    return False


def analyze_product_reviews(product, query_message, lang):
    product_name = product.get("name") or product.get("product_name") or "this product"
    reviews = product.get("reviews", [])
            
    def get_polarity(r):
        if "analysis" in r and "polarity" in r["analysis"]:
            return float(r["analysis"]["polarity"])
        text = r.get("title", "") + " " + r.get("text", "")
        return float(analyze_text(text)["polarity"])
        
    def get_sentiment(r):
        if "analysis" in r and "sentiment" in r["analysis"]:
            return r["analysis"]["sentiment"]
        text = r.get("title", "") + " " + r.get("text", "")
        return analyze_text(text)["sentiment"]

    msg_clean = query_message.lower()
    
    worth_keywords = ["worth", "price", "buy", "khareed", "paisa", "paise", "money", "expensive", "cheap", "cost", "value", "vasool"]
    comfort_keywords = ["comfort", "wear", "fitting", "heavy", "soft", "comfy", "fit", "heavy", "weight"]
    battery_keywords = ["battery", "charge", "power", "solar", "last", "hour", "day"]
    neg_keywords = ["negative", "bad", "issue", "problem", "complaint", "worst", "durability", "crap", "waste", "defect", "damage", "crack", "kamiyan", "kami", "kharab", "bekar", "khami"]

    is_worth_query = matches_any_keyword(msg_clean, worth_keywords)
    is_comfort_query = matches_any_keyword(msg_clean, comfort_keywords)
    is_battery_query = matches_any_keyword(msg_clean, battery_keywords)
    is_neg_query = matches_any_keyword(msg_clean, neg_keywords)

    feature_queries = {
        "storage": {
            "keywords": ["storage", "memory", "space", "gb", "rom", "capacity", "internal storage"],
            "name_en": "Storage/Memory",
            "name_hi": "Storage/Memory",
            "fallback_hi": "Is product me category-specific storage specifications officially listed nahi hain, par normal products me 128GB ya 256GB storage options hote hain.",
            "fallback_en": "This product does not have official storage capacity reviews. However, standard versions of such products typically offer 128GB or 256GB internal storage options.",
            "phone_spec_hi": "Is phone me **128GB/256GB storage** options available hain jise expandable memory card se badhaya jaa sakta hai.",
            "phone_spec_en": "This phone features **128GB or 256GB internal storage** options, which can be expanded further via a microSD card.",
            "watch_spec_hi": "Is smartwatch me **4GB/8GB onboard storage** hai, jisme aap songs store kar sakte hain.",
            "watch_spec_en": "This smartwatch comes with **4GB/8GB of onboard storage** which allows you to store songs locally.",
            "audio_spec_hi": "Ye ek audio device hai jisme onboard audio storage standard nahi hai; ye Bluetooth connection ke through play karta hai.",
            "audio_spec_en": "This is an audio device and does not feature internal storage; it plays media over Bluetooth connection."
        },
        "ram": {
            "keywords": ["ram", "processor", "chip", "speed", "performance", "lag", "fast", "slow", "hang"],
            "name_en": "RAM & Performance",
            "name_hi": "RAM aur Performance",
            "fallback_hi": "Is product ke performance reviews me general response positive hai.",
            "fallback_en": "The performance of this product is generally rated highly by users.",
            "phone_spec_hi": "Is smartphone me **8GB/12GB LPDDR5 RAM** aur high-performance octa-core processor hai, jisse multitasking aur gaming fast hoti hai bina kisi lag ke.",
            "phone_spec_en": "This smartphone is powered by **8GB/12GB LPDDR5 RAM** and a high-performance octa-core processor, ensuring lag-free multitasking and fast gaming.",
            "watch_spec_hi": "Is watch me smart fitness processor aur optimizing RAM hai jo navigation aur heart rate tracking ko quick and smooth banati hai.",
            "watch_spec_en": "This smartwatch uses a specialized fitness processor with optimized memory to ensure quick navigation and smooth tracking.",
            "audio_spec_hi": "Is headphones me advanced audio processor chip aur smart noise-cancelling chip hai jo fast connectivity aur crisp audio output deti hai.",
            "audio_spec_en": "These headphones are equipped with an advanced audio processing chip and smart noise-cancelling chip for fast connectivity and crisp sound."
        },
        "display": {
            "keywords": ["display", "screen", "visibility", "fluid", "refresh rate", "brightness", "dim", "glass", "oled", "amoled", "lcd"],
            "name_en": "Display & Screen Quality",
            "name_hi": "Display aur Screen Quality",
            "fallback_hi": "Product ka display and screen visibility users ke mutabik achha hai.",
            "fallback_en": "The display quality and screen visibility are generally appreciated by users.",
            "phone_spec_hi": "Is phone me stunning **120Hz AMOLED display** hai, jise user reviews me fluid screen aur bright sunlight visibility ke liye praise kiya gaya hai.",
            "phone_spec_en": "This smartphone features a stunning **120Hz AMOLED display**, highly praised in user reviews for its fluid screen and bright sunlight visibility.",
            "watch_spec_hi": "Is watch me **1.4-inch display** hai jo outdoor daylight me highly visible hai, par indoors me users ne screen thodi dim hone ki shikayat ki hai.",
            "watch_spec_en": "This smartwatch features a **1.4-inch outdoor-optimized screen**. Users note it is highly visible under direct sunlight, but slightly dim indoors.",
            "audio_spec_hi": "Audio device me traditional screen display nahi hai, ye touch controls aur status indicator LED lights ke sath aata hai.",
            "audio_spec_en": "This audio device does not have a screen display; it features status indicator LED lights and intuitive touch controls."
        },
        "camera": {
            "keywords": ["camera", "lens", "photo", "video", "megapixel", "mp", "click", "shoot", "sensor"],
            "name_en": "Camera Quality",
            "name_hi": "Camera Quality",
            "fallback_hi": "Is category product me dedicated camera sensors standard nahi hain.",
            "fallback_en": "Dedicated camera sensors are not standard in this category of product.",
            "phone_spec_hi": "Is smartphone me **64MP/108MP triple camera setup** hai. Kuch users ne photos ko crisp bataya hai par low-light camera app me minor lag/crashing ki shikayat ki hai.",
            "phone_spec_en": "This smartphone comes with a **64MP/108MP triple camera setup**. While users praise daylight photos, some report slight lag or crashing in the camera app under low light.",
            "watch_spec_hi": "Is smartwatch me built-in camera nahi hai, par isme custom camera remote control features hain jisse aap phone ka camera click kar sakte hain.",
            "watch_spec_en": "This smartwatch does not feature an onboard camera, but supports remote camera shutter control for your connected smartphone.",
            "audio_spec_hi": "Audio device me photo camera nahi hota hai, par calls ke liye background noise cancellation mic system present hai.",
            "audio_spec_en": "This audio device does not feature a camera, but includes a built-in microphone array with noise reduction for clear voice calls."
        },
        "sound": {
            "keywords": ["sound", "audio", "speaker", "bass", "volume", "music", "noise", "mic", "microphone"],
            "name_en": "Sound & Audio Quality",
            "name_hi": "Sound aur Audio Quality",
            "fallback_hi": "Product ka sound quality standards ke hisab se theek hai.",
            "fallback_en": "The sound and speaker quality are considered standard for this device type.",
            "phone_spec_hi": "Is phone me stereo speakers hain jo clear sound deliver karte hain, par heavy bass ke liye speakers slightly quiet lag sakte hain.",
            "phone_spec_en": "This phone features dual stereo speakers providing clear audio, though some users find them slightly quiet for heavy bass.",
            "watch_spec_hi": "Is watch me notifications alerts ke liye small speaker and sound buzzer hai.",
            "watch_spec_en": "This smartwatch features a small built-in speaker and vibration motor for clear call alerts and notifications.",
            "audio_spec_hi": "In headphones me stellar sound profile hai, deep bass aur crisp treble ke sath. Active Noise Cancellation background engine noises ko perfectly block karta hai.",
            "audio_spec_en": "These headphones deliver outstanding audio quality with rich bass and clear highs, combined with supreme active noise cancellation (ANC)."
        },
        "gps": {
            "keywords": ["gps", "map", "navigation", "track", "location", "route"],
            "name_en": "GPS & Location Tracking",
            "name_hi": "GPS aur Location Tracking",
            "fallback_hi": "Is product me physical GPS or navigation tracking standard nahi hai.",
            "fallback_en": "Physical GPS and location tracking are not standard features for this product category.",
            "phone_spec_hi": "Is smartphone me multi-system GPS and Galileo navigation tracking hai, jo maps aur navigation applications me perfectly and accurately run karta hai.",
            "phone_spec_en": "This smartphone features multi-system GPS and Galileo tracking, running smoothly and accurately on Google Maps and other navigation apps.",
            "watch_spec_hi": "Is smartwatch me dedicated GPS chip hai jo deep forests me bhi highly accurate tracking deti hai, halanki connect hone me thoda time le sakti hai.",
            "watch_spec_en": "This smartwatch is equipped with a dedicated multi-band GPS sensor. It provides highly accurate route mapping, though it can take a moment to lock onto signal.",
            "audio_spec_hi": "Is headphones me direct GPS tracking features built-in nahi hote hain.",
            "audio_spec_en": "These headphones do not feature built-in GPS or navigation sensors."
        },
        "apps": {
            "keywords": ["app", "sync", "software", "crashing", "glitch", "crash", "application", "ui", "interface"],
            "name_en": "Software & App Integration",
            "name_hi": "Software aur App Integration",
            "fallback_hi": "Is product ka companion software response theek hai.",
            "fallback_en": "The software integration and performance are standard for this device class.",
            "phone_spec_hi": "Is smartphone me Android/iOS based UI hai. Kuch users report karte hain ki software update me minor UI bugs hain jo apps ko crashing ya laggy banate hain.",
            "phone_spec_en": "This smartphone runs on a customized UI. Users note that while features are rich, software updates can introduce minor bugs, leading to app crashes or lag.",
            "watch_spec_hi": "Is watch ke companion mobile application interface me syncing glitches hain. Users report karte hain ki app frequently crash hota ya sync speed low hai.",
            "watch_spec_en": "This smartwatch is paired with a companion application. However, users report syncing glitches where the mobile app crashes or fails to sync logs.",
            "audio_spec_hi": "Is audio device ko configure karne ke liye smart app setup companion available hai, jisse custom equalizer settings map ki jaa sakti hain.",
            "audio_spec_en": "This audio device supports a companion app that allows users to customize equalizers and map custom control gestures."
        }
    }

    matched_key = None
    for key, info in feature_queries.items():
        if matches_any_keyword(msg_clean, info["keywords"]):
            matched_key = key
            break

    # 1. If a specific spec keyword was matched, process that first (works with or without reviews)
    if matched_key:
        info = feature_queries[matched_key]
        matched_reviews = []
        for r in reviews:
            text_lower = (r.get("title", "") + " " + r.get("text", "")).lower()
            if matches_any_keyword(text_lower, info["keywords"]):
                matched_reviews.append(r)
        
        # Determine the product category/type to show specifications / reviews
        is_phone = any(k in product_name.lower() or k in product.get("category", "").lower() for k in ["phone", "mobile", "samsung", "iphone", "pixel", "oneplus"])
        is_watch = any(k in product_name.lower() or k in product.get("category", "").lower() for k in ["watch", "smartwatch", "fitness", "chrono", "apexfit"])
        is_audio = any(k in product_name.lower() or k in product.get("category", "").lower() for k in ["headphone", "audio", "sound", "earbud", "speaker", "zenith"])
        
        if matched_reviews:
            avg_pol = sum(get_polarity(r) for r in matched_reviews) / len(matched_reviews)
            avg_rating = sum(float(r.get("rating") if r.get("rating") is not None else 4.0) for r in matched_reviews) / len(matched_reviews)
            pos_matches = [r for r in matched_reviews if get_polarity(r) >= 0.05]
            neg_matches = [r for r in matched_reviews if get_polarity(r) <= -0.05]
            
            quotes_html = ""
            if pos_matches:
                best_pos = max(pos_matches, key=lambda r: get_polarity(r))
                quotes_html += f"<li>👍 <em>\"{best_pos.get('text')[:120]}...\"</em></li>"
            if neg_matches:
                worst_neg = min(neg_matches, key=lambda r: get_polarity(r))
                quotes_html += f"<li>👎 <em>\"{worst_neg.get('text')[:120]}...\"</em></li>"
            
            sentiment_word = "positive" if avg_pol >= 0.05 else "negative" if avg_pol <= -0.05 else "mixed"
            sentiment_word_hi = "positive" if avg_pol >= 0.05 else "negative" if avg_pol <= -0.05 else "neutral/mixed"
            
            if lang == "hindi":
                reply = f"**{product_name}** ke **{info['name_hi']}** aspect ke reviews aur specs details ye hain:<br><br>"
                # Add specs if applicable
                if is_phone and "phone_spec_hi" in info:
                    reply += f"**Product Specifications:** {info['phone_spec_hi']}<br><br>"
                elif is_watch and "watch_spec_hi" in info:
                    reply += f"**Product Specifications:** {info['watch_spec_hi']}<br><br>"
                elif is_audio and "audio_spec_hi" in info:
                    reply += f"**Product Specifications:** {info['audio_spec_hi']}<br><br>"
                
                reply += f"**Reviews Consensus:**<br>" \
                         f"<ul>" \
                         f"<li><strong>Average Rating ({info['name_hi']}):</strong> {avg_rating:.1f}★ (Total {len(matched_reviews)} reviews matched)</li>" \
                         f"<li><strong>Sentiment:</strong> User reviews me is feature ko lekar sentiment **{sentiment_word_hi}** hai.</li>" \
                         f"</ul>"
                if quotes_html:
                    reply += f"Customers ka kya kehna hai:<br><ul>{quotes_html}</ul>"
            else:
                reply = f"Here is the review analysis for **{product_name}** regarding **{info['name_en']}**:<br><br>"
                # Add specs if applicable
                if is_phone and "phone_spec_en" in info:
                    reply += f"**Product Specifications:** {info['phone_spec_en']}<br><br>"
                elif is_watch and "watch_spec_en" in info:
                    reply += f"**Product Specifications:** {info['watch_spec_en']}<br><br>"
                elif is_audio and "audio_spec_en" in info:
                    reply += f"**Product Specifications:** {info['audio_spec_en']}<br><br>"
                
                reply += f"**Reviews Consensus:**<br>" \
                         f"<ul>" \
                         f"<li>**Average Rating ({info['name_en']}):** {avg_rating:.1f}★ (based on {len(matched_reviews)} relevant reviews)</li>" \
                         f"<li>**Sentiment:** The tone regarding this feature is majorly **{sentiment_word}**.</li>" \
                         f"</ul>"
                if quotes_html:
                    reply += f"What customers are saying:<br><ul>{quotes_html}</ul>"
        else:
            # Fallback if no specific reviews matched the feature keywords (or reviews is empty)
            if lang == "hindi":
                reply = f"**{product_name}** ke reviews me **{info['name_hi']}** ke baare me koi direct comments nahi mile, par specs details ye hain:<br><br>"
                if is_phone and "phone_spec_hi" in info:
                    reply += f"{info['phone_spec_hi']}"
                elif is_watch and "watch_spec_hi" in info:
                    reply += f"{info['watch_spec_hi']}"
                elif is_audio and "audio_spec_hi" in info:
                    reply += f"{info['audio_spec_hi']}"
                else:
                    reply += f"{info['fallback_hi']}"
            else:
                reply = f"We found no direct mentions of **{info['name_en']}** in the customer reviews for **{product_name}**, but here are the specification details:<br><br>"
                if is_phone and "phone_spec_en" in info:
                    reply += f"{info['phone_spec_en']}"
                elif is_watch and "watch_spec_en" in info:
                    reply += f"{info['watch_spec_en']}"
                elif is_audio and "audio_spec_en" in info:
                    reply += f"{info['audio_spec_en']}"
                else:
                    reply += f"{info['fallback_en']}"
        return reply

    # 2. For other queries (worth, comfort, battery, complaints, summary), reviews must exist.
    if not reviews:
        if lang == "hindi":
            return f"Mujhe **{product_name}** ke reviews nahi mile. Kripya check karein ki reviews loaded hain ya nahi."
        else:
            return f"I couldn't find any reviews for **{product_name}**."

    # 3. Handle other queries
    matched_reviews = []
    
    if is_worth_query:
        for r in reviews:
            text_lower = (r.get("title", "") + " " + r.get("text", "")).lower()
            if matches_any_keyword(text_lower, worth_keywords):
                matched_reviews.append(r)
        
        if not matched_reviews:
            matched_reviews = reviews
            
        avg_pol = sum(get_polarity(r) for r in matched_reviews) / len(matched_reviews)
        avg_rating = sum(float(r.get("rating") if r.get("rating") is not None else 4.0) for r in matched_reviews) / len(matched_reviews)
        
        pos_matches = [r for r in matched_reviews if get_polarity(r) >= 0.05]
        neg_matches = [r for r in matched_reviews if get_polarity(r) <= -0.05]
        
        if avg_rating >= 4.0 or avg_pol >= 0.15:
            verdict_en = "highly worth buying (Value for Money)"
            verdict_hi = "paise vasool aur kharidne ke liye bilkul worth to buy (Value for Money) hai"
        elif avg_rating <= 3.0 or avg_pol < -0.05:
            verdict_en = "not recommended / not worth the price"
            verdict_hi = "price ke hisab se worth buying nahi hai (Not worth the price)"
        else:
            verdict_en = "mixed in value. Some users find it worth it while others feel it's overpriced"
            verdict_hi = "mixed reviews ke sath hai, kuch users isko worth it bolte hain toh kuch overpriced"
            
        quotes_html = ""
        if pos_matches:
            best_pos = max(pos_matches, key=lambda r: get_polarity(r))
            quotes_html += f"<li>👍 <em>\"{best_pos.get('text')[:120]}...\"</em></li>"
        if neg_matches:
            worst_neg = min(neg_matches, key=lambda r: get_polarity(r))
            quotes_html += f"<li>👎 <em>\"{worst_neg.get('text')[:120]}...\"</em></li>"
            
        if lang == "hindi":
            reply = f"**{product_name}** ke price-to-value analysis ke baare me main aapko batata hoon:<br><br>" \
                    f"**Verdict:** Ye product **{verdict_hi}**.<br>" \
                    f"<ul>" \
                    f"<li><strong>Average Rating for Price/Worth mentions:</strong> {avg_rating:.1f}★</li>" \
                    f"<li><strong>Customer Sentiment:</strong> Reviews me price/value ko lekar sentiment majorly { 'positive' if avg_pol >= 0.05 else 'negative' if avg_pol <= -0.05 else 'mixed' } hai.</li>" \
                    f"</ul>"
            if quotes_html:
                reply += f"Customers ka feedback:<br><ul>{quotes_html}</ul>"
        else:
            reply = f"Here is the price-to-value analysis for **{product_name}** based on user reviews:<br><br>" \
                    f"**Verdict:** The product is considered **{verdict_en}**.<br>" \
                    f"<ul>" \
                    f"<li>**Average Rating (Price/Worth mentions):** {avg_rating:.1f}★</li>" \
                    f"<li>**Customer Sentiment:** The overall tone regarding price and worth is { 'positive' if avg_pol >= 0.05 else 'negative' if avg_pol <= -0.05 else 'mixed' }.</li>" \
                    f"</ul>"
            if quotes_html:
                reply += f"What customers are saying:<br><ul>{quotes_html}</ul>"
        return reply

    elif is_comfort_query:
        for r in reviews:
            text_lower = (r.get("title", "") + " " + r.get("text", "")).lower()
            if matches_any_keyword(text_lower, comfort_keywords):
                matched_reviews.append(r)
        
        if not matched_reviews:
            matched_reviews = reviews
            
        avg_pol = sum(get_polarity(r) for r in matched_reviews) / len(matched_reviews)
        pos_matches = [r for r in matched_reviews if get_polarity(r) >= 0.05]
        neg_matches = [r for r in matched_reviews if get_polarity(r) <= -0.05]
        
        quotes_html = ""
        if pos_matches:
            best_pos = max(pos_matches, key=lambda r: get_polarity(r))
            quotes_html += f"<li>👍 <em>\"{best_pos.get('text')[:120]}...\"</em></li>"
        if neg_matches:
            worst_neg = min(neg_matches, key=lambda r: get_polarity(r))
            quotes_html += f"<li>👎 <em>\"{worst_neg.get('text')[:120]}...\"</em></li>"

        if lang == "hindi":
            reply = f"**{product_name}** ke reviews ke mutabik comfort/fitting ko lekar users ka feedback bohot positive hai. " \
                    f"Log keh rahe hain ki ye wear karne me **bohot comfortable hain** aur hours tak bina problem ke pehna jaa sakta hai."
            if quotes_html:
                reply += f"<br><br>Customers ka feedback:<br><ul>{quotes_html}</ul>"
        else:
            reply = f"According to customer reviews, **{product_name}** is extremely **comfortable to wear** for long periods of time."
            if quotes_html:
                reply += f"<br><br>Here are some user comments:<br><ul>{quotes_html}</ul>"
        return reply

    elif is_battery_query:
        for r in reviews:
            text_lower = (r.get("title", "") + " " + r.get("text", "")).lower()
            if matches_any_keyword(text_lower, battery_keywords):
                matched_reviews.append(r)
        
        if not matched_reviews:
            matched_reviews = reviews

        avg_pol = sum(get_polarity(r) for r in matched_reviews) / len(matched_reviews)
        pos_matches = [r for r in matched_reviews if get_polarity(r) >= 0.05]
        neg_matches = [r for r in matched_reviews if get_polarity(r) <= -0.05]
        
        quotes_html = ""
        if pos_matches:
            best_pos = max(pos_matches, key=lambda r: get_polarity(r))
            quotes_html += f"<li>👍 <em>\"{best_pos.get('text')[:120]}...\"</em></li>"
        if neg_matches:
            worst_neg = min(neg_matches, key=lambda r: get_polarity(r))
            quotes_html += f"<li>👎 <em>\"{worst_neg.get('text')[:120]}...\"</em></li>"

        if lang == "hindi":
            reply = f"**{product_name}** ka **battery performance** bohot stellar hai aur ye easily long time tak chalti hai."
            if quotes_html:
                reply += f"<br><br>Kuch customer quotes:<br><ul>{quotes_html}</ul>"
        else:
            reply = f"The **battery performance** for **{product_name}** is highly praised by customers."
            if quotes_html:
                reply += f"<br><br>Here are some customer comments:<br><ul>{quotes_html}</ul>"
        return reply

    elif is_neg_query:
        neg_reviews = [r for r in reviews if get_polarity(r) <= -0.1 or float(r.get("rating") if r.get("rating") is not None else 4.0) <= 3]
        
        if not neg_reviews:
            if lang == "hindi":
                return f"Bohot badhiya! **{product_name}** ke reviews me koi major complaints ya negative points nahi mile hain."
            else:
                return f"Great! There are no significant negative complaints or issues reported for **{product_name}**."
        
        complaints_html = ""
        for r in neg_reviews[:3]:
            title = r.get("title", "")
            text = r.get("text", "")
            complaints_html += f"<li>❌ <strong>{title}:</strong> \"{text[:120]}...\"</li>"
            
        if lang == "hindi":
            reply = f"**{product_name}** ke users dwara report kiye gaye negative points aur issues ye hain:<br><br>" \
                    f"Total complaints scanned: {len(neg_reviews)} reviews.<br>" \
                    f"<ul>{complaints_html}</ul>"
        else:
            reply = f"Here are the negative aspects and complaints reported by customers for **{product_name}**:<br><br>" \
                    f"Total negative reviews processed: {len(neg_reviews)}.<br>" \
                    f"<ul>{complaints_html}</ul>"
        return reply

    else:
        # Default overall summary
        avg_rating = sum(float(r.get("rating") if r.get("rating") is not None else 4.0) for r in reviews) / len(reviews)
        avg_pol = sum(get_polarity(r) for r in reviews) / len(reviews)
        sentiment_distribution = {"positive": 0, "negative": 0, "neutral": 0}
        for r in reviews:
            s = get_sentiment(r)
            if s == "Positive":
                sentiment_distribution["positive"] += 1
            elif s == "Negative":
                sentiment_distribution["negative"] += 1
            else:
                sentiment_distribution["neutral"] += 1
                
        total_revs = len(reviews)
        pos_perc = (sentiment_distribution["positive"] / total_revs) * 100
        neg_perc = (sentiment_distribution["negative"] / total_revs) * 100
        neu_perc = (sentiment_distribution["neutral"] / total_revs) * 100
        
        features_list = product.get("features", [])
        features_str = ", ".join(features_list) if features_list else "None predefined"
        
        if lang == "hindi":
            reply = f"**{product_name}** (Category: {product.get('category', 'General')}) ki overall report:<br><ul>" \
                    f"<li><strong>Average Rating:</strong> {avg_rating:.1f}★ (Total: {total_revs} reviews)</li>" \
                    f"<li><strong>Sentiment Share:</strong> Positive: {pos_perc:.0f}%, Neutral: {neu_perc:.0f}%, Negative: {neg_perc:.0f}%</li>" \
                    f"<li><strong>Overall Mood Polarity:</strong> {avg_pol:.2f} ({'Positive Brand Outlook' if avg_pol >= 0.05 else 'Negative Brand Friction' if avg_pol <= -0.05 else 'Neutral/Mixed'})</li>" \
                    f"<li><strong>Features Mapped:</strong> {features_str}</li>" \
                    f"</ul>Aap is product ke baare me specific aspects jaise comfort, battery, complaints, ya 'worth to buy' ke baare me puch sakte hain!"
        else:
            reply = f"Here is the overall review summary for **{product_name}** (Category: {product.get('category', 'General')}):<br><ul>" \
                    f"<li>**Average Rating:** {avg_rating:.1f}★ (based on {total_revs} reviews)</li>" \
                    f"<li>**Sentiment Share:** Positive: {pos_perc:.0f}%, Neutral: {neu_perc:.0f}%, Negative: {neg_perc:.0f}%</li>" \
                    f"<li>**Overall Sentiment Polarity:** {avg_pol:.2f} ({'Positive Brand Outlook' if avg_pol >= 0.05 else 'Negative Brand Friction' if avg_pol <= -0.05 else 'Neutral/Mixed'})</li>" \
                    f"<li>**Features Mapped:** {features_str}</li>" \
                    f"</ul>Feel free to ask about specific aspects like Comfort, Battery Life, Negative issues, or if it is 'worth to buy'!"
        return reply


def analyze_social_posts(social, query_message, lang):
    hashtag = social.get("hashtag") or "this topic"
    posts = social.get("posts", [])
    topic_name = social.get("topicName") or f"#{hashtag}"
    
    if not posts:
        if lang == "hindi":
            return f"Mujhe **#{hashtag}** ke liye koi posts nahi mile. Kripya check karein ki feed active hai."
        else:
            return f"I couldn't find any posts for **#{hashtag}**."
            
    def get_sentiment(p):
        if "analysis" in p and "sentiment" in p["analysis"]:
            return p["analysis"]["sentiment"]
        return analyze_text(p.get("text", ""))["sentiment"]
        
    def get_polarity(p):
        if "analysis" in p and "polarity" in p["analysis"]:
            return float(p["analysis"]["polarity"])
        return float(analyze_text(p.get("text", ""))["polarity"])

    msg_clean = query_message.lower()
    
    is_strat_query = any(k in msg_clean for k in ["strategy", "action", "pr", "marketing", "solution", "kya karein", "pr advice", "upaye"])
    is_neg_query = any(k in msg_clean for k in ["negative", "bad", "issue", "problem", "complaint", "angry", "panic", "criticism", "crashes", "kharab", "gussa", "complaints"])
    
    pos_posts = [p for p in posts if get_sentiment(p) == "Positive"]
    neg_posts = [p for p in posts if get_sentiment(p) == "Negative"]
    neu_posts = [p for p in posts if get_sentiment(p) == "Neutral"]
    
    total = len(posts)
    pos_ratio = (len(pos_posts) / total) * 100 if total else 0
    neg_ratio = (len(neg_posts) / total) * 100 if total else 0
    
    if is_strat_query:
        if neg_ratio > 40:
            if lang == "hindi":
                reply = f"**#{hashtag}** trend ke liye PR Strategy Advise:<br><ul>" \
                        f"<li>Mentions me negative sentiment elevated (**{neg_ratio:.0f}% negative**) hai.</li>" \
                        f"<li><strong>Action Plan:</strong> PR and customer support teams ko turant official statement release karna chahiye. Customers ki complaints (jaise software bugs, delivery delays) ko patch or resolve karein aur refund processing tez karein.</li>" \
                        f"</ul>"
            else:
                reply = f"PR Strategy Advice for **#{hashtag}**:<br><ul>" \
                        f"<li>Negative sentiment is elevated (**{neg_ratio:.0f}% negative**).</li>" \
                        f"<li>**Action Plan:** Issue a transparent official statement on channels immediately. Prioritize addressing customer complaints (e.g. system bugs or crashes), and speed up service ticket resolutions.</li>" \
                        f"</ul>"
        elif pos_ratio > 50:
            if lang == "hindi":
                reply = f"**#{hashtag}** trend ke liye marketing strategy recommendations:<br><ul>" \
                        f"<li>Public mood bohot positive (**{pos_ratio:.0f}% positive**) hai.</li>" \
                        f"<li><strong>Action Plan:</strong> Marketing team ko top positive customer feedback quotes aur organic posts ko retweet aur amplify karna chahiye. Is viral sentiment ka use search and display ads me social proof ki tarah karein.</li>" \
                        f"</ul>"
            else:
                reply = f"Marketing Strategy Recommendations for **#{hashtag}**:<br><ul>" \
                        f"<li>The public mood is highly positive (**{pos_ratio:.0f}% positive**).</li>" \
                        f"<li>**Action Plan:** The marketing team should immediately amplify organic positive posts. Use these top testimonials as social proof in campaigns to leverage this viral traction.</li>" \
                        f"</ul>"
        else:
            if lang == "hindi":
                reply = f"**#{hashtag}** trend strategy recommendations:<br><ul>" \
                        f"<li>Public response majorly mixed aur neutral hai.</li>" \
                        f"<li><strong>Action Plan:</strong> Interactive campaigns, feedback polls, aur high-engagement updates launch karein taaki audience interest aur brand awareness increase ho sake.</li>" \
                        f"</ul>"
            else:
                reply = f"PR Strategy Recommendations for **#{hashtag}**:<br><ul>" \
                        f"<li>Linguistic indicators show neutral or mixed audience response.</li>" \
                        f"<li>**Action Plan:** Host interactive polls, ask questions, and share updates to engage followers and improve organic brand conversation.</li>" \
                        f"</ul>"
        return reply
        
    elif is_neg_query:
        if not neg_posts:
            if lang == "hindi":
                return f"Bohot achha! **#{hashtag}** ke feed me koi significant negative posts nahi mile."
            else:
                return f"No negative feedback or complaints were found in the active feed for **#{hashtag}**."
                
        complaints_html = ""
        for p in neg_posts[:3]:
            complaints_html += f"<li>💬 <strong>{p.get('user')}:</strong> \"{p.get('text')[:120]}...\"</li>"
            
        if lang == "hindi":
            reply = f"**#{hashtag}** ke feed me negative sentiment aur complaints ye hain:<br><ul>{complaints_html}</ul>"
        else:
            reply = f"Here are the negative comments and criticisms from the feed for **#{hashtag}**:<br><ul>{complaints_html}</ul>"
        return reply
        
    else:
        total_likes = sum(p.get("interactions", {}).get("likes", 0) for p in posts)
        total_rt = sum(p.get("interactions", {}).get("retweets", 0) for p in posts)
        
        best_post_html = ""
        if pos_posts:
            top_pos = max(pos_posts, key=lambda p: get_polarity(p))
            best_post_html = f"<br>Top positive post: <em>\"{top_pos.get('text')}\"</em> by {top_pos.get('user')}"
            
        if lang == "hindi":
            reply = f"**#{hashtag}** ({topic_name}) Social Tracker Report:<br><ul>" \
                    f"<li><strong>Total posts:</strong> {total} parsed posts</li>" \
                    f"<li><strong>Total interactions:</strong> {total_likes:,} Likes, {total_rt:,} Retweets</li>" \
                    f"<li><strong>Sentiment Share:</strong> Positive: {pos_ratio:.0f}%, Neutral: {len(neu_posts)/total*100:.0f}%, Negative: {neg_ratio:.0f}%</li>" \
                    f"</ul>Aap is trend ke PR/marketing advice, negative feedback, ya summary ke baare me specific questions pooch sakte hain!{best_post_html}"
        else:
            reply = f"Here is the social media status report for **#{hashtag}** ({topic_name}):<br><ul>" \
                    f"<li>**Volume:** {total} parsed items</li>" \
                    f"<li>**Interactions:** {total_likes:,} Likes, {total_rt:,} Retweets</li>" \
                    f"<li>**Sentiment Share:** Positive: {pos_ratio:.0f}%, Neutral: {len(neu_posts)/total*100:.0f}%, Negative: {neg_ratio:.0f}%</li>" \
                    f"</ul>**Key Insights:** You can ask about PR recommendations, top complaints, or general user queries!{best_post_html}"
        return reply


@app.route("/api/chatbot", methods=["POST"])
def api_chatbot():
    """
    Intelligent chatbot assistant that answers queries about products and social media topics.
    """
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    active_product_id = data.get("activeProduct", "")
    active_hashtag = data.get("activeHashtag", "")
    preferred_lang = data.get("preferredLanguage", "")
    current_product = data.get("currentProduct")
    current_social = data.get("currentSocial")
    
    if not message:
        return jsonify({
            "reply": "Kuch toh puchiye! Main aapki help karne ke liye taiyaar hoon.",
            "language": "hindi"
        })
    
    lang = detect_language(message, preferred_lang)
    message_lower = message.lower()
    
    # Check if it was an explicit request to switch language
    lang_switch_hi = ["speak in hindi", "hindi me", "hindi mein", "talk in hindi", "hindi please", "hindi language", "hinglish", "hindi"]
    lang_switch_en = ["speak in english", "english me", "english mein", "talk in english", "english please", "english language", "english"]
    
    if matches_any_keyword(message_lower, lang_switch_hi):
        return jsonify({
            "reply": "Theek hai! Ab se main Hindi/Hinglish me baat karunga. Aap active product reviews ya social media trends ke baare me kya poochna chahte hain?",
            "language": "hindi"
        })
    elif matches_any_keyword(message_lower, lang_switch_en):
        return jsonify({
            "reply": "Sure! I will speak in English from now on. What would you like to know about the active product reviews or social media trends?",
            "language": "english"
        })
        
    # Resolve Product
    product = None
    # Check message for preset product matches
    for p in AMAZON_PRESETS:
        keywords = [p["productId"].lower()]
        if "zenith" in p["productId"].lower():
            keywords.append("zenith")
        elif "glow" in p["productId"].lower():
            keywords.append("glowritual")
        elif "apex" in p["productId"].lower():
            keywords.append("apexfit")
        if matches_any_keyword(message_lower, keywords):
            product = p
            break
            
    # Check current_product
    if not product and current_product:
        product = current_product
        
    # Check active_product_id preset fallback
    if not product and active_product_id:
        for p in AMAZON_PRESETS:
            if p["productId"] == active_product_id:
                product = p
                break

    # Resolve Social Topic
    social_topic = None
    for s in SOCIAL_PRESETS:
        keywords = [s["hashtag"].lower(), s["topicName"].lower()]
        if "velo" in s["hashtag"].lower():
            keywords.append("velo")
        elif "crisis" in s["hashtag"].lower():
            keywords.append("crisis")
        elif "wrap" in s["hashtag"].lower():
            keywords.append("wrap")
        if matches_any_keyword(message_lower, keywords):
            social_topic = s
            break
            
    if not social_topic and current_social:
        social_topic = current_social
        
    if not social_topic and active_hashtag:
        for s in SOCIAL_PRESETS:
            if s["hashtag"].lower() == active_hashtag.lower():
                social_topic = s
                break

    # Check Product Queries
    product_keywords = [
        "product", "headphones", "zenith", "serum", "glow", "watch", "apex", "review", "worth", "buy", "khareed", "price", "paisa", "paise", "money", "expensive", "cheap", "cost", "value", "comfort", "fitting", "comfortable", "battery", "charge", "power", "bad", "negative", "issue", "problem", "durability", "crack", "defect", "summary", "storage", "memory", "ram", "display", "screen", "camera", "sensor", "gps", "navigation", "sound", "speaker", "app", "software", "performance", "processor"
    ]
    is_product_related = matches_any_keyword(message_lower, product_keywords)

    # Check Social Media / Hashtag Queries
    social_keywords = [
        "social", "tracker", "hashtag", "trend", "twitter", "public", "velo", "crisis", "bank", "wrap", "post", "strategy", "action", "pr", "marketing", "negative", "angry", "panic", "frustrated", "frustration", "insight", "report", "summary"
    ]
    is_social_related = matches_any_keyword(message_lower, social_keywords)

    # Priority 1: If there is an active product/social topic and it is related to product/social queries
    if product and is_product_related:
        reply = analyze_product_reviews(product, message, lang)
        return jsonify({"reply": reply, "language": lang})
        
    if social_topic and is_social_related:
        reply = analyze_social_posts(social_topic, message, lang)
        return jsonify({"reply": reply, "language": lang})

    # Priority 2: Check general FAQs
    for category, faq in CHATBOT_FAQS.items():
        if matches_any_keyword(message_lower, faq["keywords"]):
            reply = faq["hindi"] if lang == "hindi" else faq["english"]
            reply = reply.replace("\n", "<br>")
            return jsonify({"reply": reply, "language": lang})
    
    # Priority 3: Greet queries
    if matches_any_keyword(message_lower, ["hi", "hello", "hey", "namaste", "good morning", "good evening", "salam"]):
        if lang == "hindi":
            reply = "Hello! Main SentimentIQ AI Co-Pilot hoon. Main active tab ke product reviews ya social media tracker ki summary aur insights de sakta hoon. Aap inme se kisi ke baare me bhi puch sakte hain."
        else:
            reply = "Hello! I am the SentimentIQ AI Co-Pilot. I can provide summaries and key insights for the product reviews or the social media tracker of your active tab. Feel free to ask me anything!"
        return jsonify({"reply": reply, "language": lang})

    # Priority 4: General information about SentimentIQ
    if matches_any_keyword(message_lower, ["sentimentiq", "system", "work", "kaise kaam"]):
        if lang == "hindi":
            reply = "SentimentIQ ek advanced NLP analysis system hai. Ye text me se **polarity** (positive/negative sentiment) aur **8 Plutchik emotions** (Joy, Trust, Fear, Surprise, Sadness, Disgust, Anger, Anticipation) ko identify karta hai. Isme active settings ke mutabik thresholds change kiye jaa sakte hain."
        else:
            reply = "SentimentIQ is an advanced NLP analysis system. It identifies **polarity** (positive/negative sentiment) and the **8 Plutchik emotions** (Joy, Trust, Fear, Surprise, Sadness, Disgust, Anger, Anticipation) from text. You can customize the evaluation thresholds in the settings tab."
        return jsonify({"reply": reply, "language": lang})

    # Priority 5: Fallback to active product/social even if no keywords matched
    if product and active_product_id:
        reply = analyze_product_reviews(product, message, lang)
        return jsonify({"reply": reply, "language": lang})

    if social_topic and active_hashtag:
        reply = analyze_social_posts(social_topic, message, lang)
        return jsonify({"reply": reply, "language": lang})

    # 8. Real-time User Prompt Sentiment Analyzer Fallback
    try:
        analysis = analyze_text(message)
        emotions = analysis.get("emotions", {})
        active_emos = [f"{emo.capitalize()} ({score}%)" for emo, score in emotions.items() if score > 0]
        
        if active_emos:
            emotions_str = ", ".join(active_emos)
        else:
            emotions_str = "None detected" if lang == "english" else "Koi nahi mila"
            
        if lang == "hindi":
            reply = f"Maine aapke message ka real-time sentiment analysis kiya hai:<br><ul>" \
                    f"<li><strong>Sentiment tone:</strong> {analysis['sentiment']}</li>" \
                    f"<li><strong>Compound Polarity:</strong> {analysis['polarity']:.2f} (-1.0 se +1.0 ki range me)</li>" \
                    f"<li><strong>Word Count:</strong> {analysis['wordCount']} words</li>" \
                    f"<li><strong>Detected Emotions:</strong> {emotions_str}</li>" \
                    f"</ul>Aap active reviews ya campaign ke baare me kuch specific puchiye, ya phir koi review paste karke sentiment check karein!"
        else:
            reply = f"I've performed a real-time sentiment analysis on your message:<br><ul>" \
                    f"<li><strong>Sentiment Tone:</strong> {analysis['sentiment']}</li>" \
                    f"<li><strong>Compound Polarity:</strong> {analysis['polarity']:.2f} (ranges from -1.0 to +1.0)</li>" \
                    f"<li><strong>Word Count:</strong> {analysis['wordCount']} words</li>" \
                    f"<li><strong>Detected Emotions:</strong> {emotions_str}</li>" \
                    f"</ul>Ask me about the active product reviews/campaign, or paste any review text here to check its sentiment!"
    except Exception as e:
        if lang == "hindi":
            reply = "Main aapki query puri tarah samajh nahi paaya. Kripya active product reviews ya active social media tracker ke baare me puchiye!"
        else:
            reply = "I could not fully understand your query. Please ask about the active product reviews or the social media tracker!"
            
    return jsonify({"reply": reply, "language": lang})


if __name__ == "__main__":
    print("-------------------------------------------------------")
    print("Starting CodeAlpha Sentiment & Emotion Analysis Server...")
    print("Dashboard: http://127.0.0.1:5001")
    print("-------------------------------------------------------")
    app.run(host="127.0.0.1", port=5001)

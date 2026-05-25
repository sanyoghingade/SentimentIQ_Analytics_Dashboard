# Amazon Product Review Scraper with Category-Specific Mock Fallbacks
import re
import requests
from bs4 import BeautifulSoup

def extract_asin_and_domain(url):
    """
    Parses Amazon URLs to extract the 10-digit ASIN and domain name.
    """
    # Regex to capture ASIN (10 alphanumeric uppercase characters)
    asin_match = re.search(r'/(?:dp|gp/product|gp/aw/d)/([A-Z0-9]{10})', url, re.IGNORECASE)
    if not asin_match:
        asin_match = re.search(r'/([A-Z0-9]{10})(?:[/?]|$)', url, re.IGNORECASE)
    
    asin = asin_match.group(1).upper() if asin_match else None
    
    # Extract domain (e.g. amazon.com, amazon.in, amazon.co.uk)
    domain_match = re.search(r'https?://(?:www\.)?(amazon\.[a-z.]+)', url, re.IGNORECASE)
    domain = domain_match.group(1).lower() if domain_match else "amazon.com"
    
    return asin, domain

def generate_fallback_data(asin, domain, url):
    """
    Generates high-quality mock product reviews and feature listings tailored 
    to keywords found in the parsed URL when live scraping is blocked by captchas.
    """
    url_lower = url.lower()
    reviews = []
    
    # Categorize based on keywords in URL
    if any(k in url_lower for k in ["phone", "mobile", "iphone", "samsung", "pixel", "oneplus"]):
        product_name = f"Flagship Smartphone ({asin})"
        category = "Electronics / Phones"
        features = ["Screen Quality", "Battery Life", "Camera Quality", "Performance", "Build Quality", "Price Value"]
        reviews = [
            {
                "id": "sim_p1", "author": "Ananya S.", "rating": 5, "date": "May 10, 2026",
                "title": "Absolutely gorgeous screen and stellar battery life!",
                "text": "I am completely in love with this phone! The screen is extremely vibrant and fluid, and the battery easily lasts all day. Highly recommend this premium flagship."
            },
            {
                "id": "sim_p2", "author": "Rajiv M.", "rating": 2, "date": "May 12, 2026",
                "title": "Disappointed - camera is laggy and software has bugs",
                "text": "The camera quality is okay but the app is so laggy and crashes. The battery is decent but the software updates have glitches. Not worth the expensive price."
            },
            {
                "id": "sim_p3", "author": "Vikram K.", "rating": 4, "date": "May 14, 2026",
                "title": "Solid daily driver, very fast charging",
                "text": "The charging speed is stellar, gets from 0 to 80 in 20 minutes. Design is comfortable to hold. Safe, clean experience, though speaker is slightly quiet."
            },
            {
                "id": "sim_p4", "author": "Pooja R.", "rating": 1, "date": "May 16, 2026",
                "title": "Terrible display burn-in after 2 days!",
                "text": "Awful! The screen has a terrible defect and developed a burn-in line after just 2 days. The support was slow and unresponsive. Avoid this defective model!"
            }
        ]
    elif any(k in url_lower for k in ["headphone", "earbud", "audio", "speaker", "sound"]):
        product_name = f"Acoustic Pro Wireless Audio ({asin})"
        category = "Electronics / Audio"
        features = ["Sound Quality", "Comfort", "Active Noise Cancellation", "Battery Life", "Durability", "Price Value"]
        reviews = [
            {
                "id": "sim_a1", "author": "Amit P.", "rating": 5, "date": "May 11, 2026",
                "title": "Best sound signature ever, amazing bass!",
                "text": "The audio is beautiful, super clean highs and deep, rich bass. The ANC is outstanding and block out office chat completely. Supreme comfort!"
            },
            {
                "id": "sim_a2", "author": "Divya J.", "rating": 2, "date": "May 13, 2026",
                "title": "Bluetooth connectivity is broken and glitchy",
                "text": "I am disappointed because the bluetooth connection drops constantly. The sound is good, but what use is it if it keeps disconnecting? Frustrating."
            },
            {
                "id": "sim_a3", "author": "Rohan D.", "rating": 4, "date": "May 15, 2026",
                "title": "Very comfortable, average battery life",
                "text": "These are safe and extremely comfortable for long flights. Sound isolation works nicely. Battery is decent, lasts about 15 hours. Good value."
            },
            {
                "id": "sim_a4", "author": "Neha T.", "rating": 1, "date": "May 17, 2026",
                "title": "Worst build quality, headband snapped!",
                "text": "Terrible! The cheap plastic headband snapped after two weeks of normal use. Customer service was awful and refused a refund. Scam product!"
            }
        ]
    elif any(k in url_lower for k in ["watch", "smartwatch", "fitness", "band"]):
        product_name = f"ChronoFit Active Smartwatch ({asin})"
        category = "Wearables / Fitness"
        features = ["GPS Accuracy", "App Syncing", "Battery Life", "Screen Visibility", "Solar Charging", "Comfort"]
        reviews = [
            {
                "id": "sim_w1", "author": "Rahul G.", "rating": 5, "date": "May 09, 2026",
                "title": "Stellar battery life, GPS is spot on!",
                "text": "Unbelievable battery life, lasts 14 days on a single charge. The GPS tracking is extremely accurate and syncs perfectly with my activity apps. Recommended!"
            },
            {
                "id": "sim_w2", "author": "Sneha P.", "rating": 2, "date": "May 11, 2026",
                "title": "App keeps crashing, screen is dim indoors",
                "text": "The smartwatch design is comfortable, but the companion mobile app is garbage and crashes. Indoors the screen is too dim and dark to read."
            },
            {
                "id": "sim_w3", "author": "Karan S.", "rating": 4, "date": "May 13, 2026",
                "title": "Rugged build, very reliable features",
                "text": "A very solid and honest outdoor watch. The face is scratch-resistant and durable. Safe for swimming. Step counter is very consistent."
            },
            {
                "id": "sim_w4", "author": "Meera L.", "rating": 1, "date": "May 15, 2026",
                "title": "Heart rate sensor is totally broken!",
                "text": "Terrible sensor! It says my heart rate is 180 while I am sleeping. Extremely defective and useless. Regret spending money on this junk."
            }
        ]
    elif any(k in url_lower for k in ["serum", "shampoo", "cream", "lotion", "beauty", "face", "skin"]):
        product_name = f"Natura Glow Organic Beauty Blend ({asin})"
        category = "Beauty & Skincare"
        features = ["Skin Brightening", "Moisturization", "Scent", "Texture", "Packaging/Pump", "Skin Sensitivity"]
        reviews = [
            {
                "id": "sim_b1", "author": "Priya N.", "rating": 5, "date": "May 08, 2026",
                "title": "Incredible brightness, my skin is glowing!",
                "text": "Wow! My skin feels incredibly smooth, fresh, and hydrated. The fresh citrus scent is beautiful and lightweight. Safe for my sensitive face."
            },
            {
                "id": "sim_b2", "author": "Aarav V.", "rating": 1, "date": "May 10, 2026",
                "title": "Warning: Caused severe burning and red rashes!",
                "text": "This product is extremely dangerous! It caused a severe burning sensation and broke out in red itchy rashes. Terrified, washed it off immediately. Avoid!"
            },
            {
                "id": "sim_b3", "author": "Kriti M.", "rating": 4, "date": "May 12, 2026",
                "title": "Great moisturisation, but pump leaks",
                "text": "The serum itself is fantastic and makes my face bright. However, the packaging is poor and the pump leaks, wasting a lot. Good product, bad bottle."
            },
            {
                "id": "sim_b4", "author": "Aditi S.", "rating": 2, "date": "May 14, 2026",
                "title": "Feels very sticky, smells like yuck chemicals",
                "text": "I did not like the texture. It is sticky and uncomfortable. The smell is awful, like old metal. Did not see any brightness. Disappointed."
            }
        ]
    else:
        product_name = f"Premium Consumer Product ({asin})"
        category = "General Retail"
        features = ["Price Value", "Build Quality", "Usability", "Customer Service", "Features Quality"]
        reviews = [
            {
                "id": "sim_g1", "author": "Siddharth B.", "rating": 5, "date": "May 10, 2026",
                "title": "Exceptional quality and amazing performance!",
                "text": "This is a genuine high-quality product. It is safe, durable, and performs incredibly well. Absolutely worth every penny, highly recommended!"
            },
            {
                "id": "sim_g2", "author": "Sunita K.", "rating": 2, "date": "May 12, 2026",
                "title": "Poor build, broke after minor use",
                "text": "I am disappointed. The plastic casing cracked. For this price, I expected honest quality, but it feels cheap and weak."
            },
            {
                "id": "sim_g3", "author": "Vijay H.", "rating": 4, "date": "May 14, 2026",
                "title": "Good performance with minor design issues",
                "text": "The item is solid and works fine. The controls are easy to use. The only downside is that it is heavy to hold for long periods."
            },
            {
                "id": "sim_g4", "author": "Rani J.", "rating": 1, "date": "May 16, 2026",
                "title": "Defective piece, terrible support team",
                "text": "Absolutely terrible! The item arrived broken and dead on arrival. Support was extremely rude, unresponsive, and slow. Avoid this product!"
            }
        ]

    # Duplicate reviews to increase sample size (up to 100)
    if len(reviews) > 0:
        multiplier = (100 // len(reviews)) + 1
        reviews = (reviews * multiplier)[:100]
        
    # Try to fetch the actual product title from the product page (even if reviews are blocked)
    try:
        prod_url = f"https://{domain}/dp/{asin}"
        prod_resp = requests.get(prod_url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }, timeout=10)
        prod_soup = BeautifulSoup(prod_resp.text, "html.parser")
        title_el = prod_soup.find(id="productTitle")
        if title_el:
            product_name = title_el.text.strip()
    except Exception:
        # If anything goes wrong we keep the generated placeholder name
        pass
    
    return {
        "success": False,
        "is_simulated": True,
        "asin": asin,
        "domain": domain,
        "product_name": product_name,
        "category": category,
        "features": features,
        "reviews": reviews
    }

def scrape_amazon_reviews(url, max_reviews=100):
    """
    Parses Amazon reviews, fetching multiple pages to collect up to `max_reviews` reviews.
    Falls back to simulated reviews if blocked or insufficient reviews are found.
    """
    asin, domain = extract_asin_and_domain(url)
    if not asin:
        return {
            "success": False,
            "error": "Invalid Amazon URL. Could not parse ASIN. Examples of supported structures: \n- https://www.amazon.com/dp/B0CXDZ2G3D\n- https://www.amazon.in/gp/product/B0CXDZ2G3D",
            "asin": None,
            "product_name": "Invalid Product",
            "reviews": []
        }
    
    # Base reviews URL
    base_reviews_url = f"https://{domain}/product-reviews/{asin}?reviewerType=all_reviews"
    
    # Custom headers mimicking Chrome on Windows
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    all_reviews = []
    page = 1
    while len(all_reviews) < max_reviews and page <= 5:  # limit to 5 pages to avoid endless loops
        try:
            page_url = f"{base_reviews_url}&pageNumber={page}"
            response = requests.get(page_url, headers=headers, timeout=10)
            # Detect captcha / blocking
            if "api-services-support@amazon.com" in response.text or "Robot Check" in response.text or response.status_code == 503:
                # break out and use fallback
                return generate_fallback_data(asin, domain, url)
            soup = BeautifulSoup(response.text, "html.parser")
            review_elements = soup.find_all("div", {"data-hook": "review"})
            if not review_elements:
                # No more reviews on this page
                break
            for el in review_elements:
                if len(all_reviews) >= max_reviews:
                    break
                # Author
                author_el = el.find("span", class_="a-profile-name")
                author = author_el.text.strip() if author_el else "Verified Purchaser"
                # Rating
                rating_el = el.find("i", {"data-hook": "review-star-rating"})
                if not rating_el:
                    rating_el = el.find("i", class_="review-rating")
                rating = 5.0
                if rating_el:
                    rating_str = rating_el.text.strip()
                    r_match = re.search(r'([0-9.]+)', rating_str)
                    if r_match:
                        rating = float(r_match.group(1))
                # Date
                date_el = el.find("span", {"data-hook": "review-date"})
                date = date_el.text.strip() if date_el else "Recently"
                date = date.replace("Reviewed in the United States on ", "").replace("Reviewed in India on ", "")
                # Title
                title_el = el.find("a", {"data-hook": "review-title"})
                if not title_el:
                    title_el = el.find("span", {"data-hook": "review-title"})
                title = ""
                if title_el:
                    title_span = title_el.find("span")
                    title = title_span.text.strip() if title_span else title_el.text.strip()
                # Body text
                body_el = el.find("span", {"data-hook": "review-body"})
                body = ""
                if body_el:
                    body_span = body_el.find("span")
                    body = body_span.text.strip() if body_span else body_el.text.strip()
                if body:
                    all_reviews.append({
                        "id": f"scraped_{len(all_reviews)}",
                        "author": author,
                        "rating": int(rating),
                        "date": date,
                        "title": title,
                        "text": body
                    })
        except Exception:
            # On any error, fallback to simulated data
            return generate_fallback_data(asin, domain, url)
        page += 1
    
    # If we fetched no reviews, fall back to simulated data
    if not all_reviews:
        return generate_fallback_data(asin, domain, url)
    
    # Fetch product name (single request to first page if not already obtained)
    try:
        response = requests.get(base_reviews_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        product_title_el = soup.find("a", {"data-hook": "product-link"})
        product_name = product_title_el.text.strip() if product_title_el else f"Amazon Product ({asin})"
    except Exception:
        product_name = f"Amazon Product ({asin})"
    
    return {
        "success": True,
        "is_simulated": False,
        "asin": asin,
        "domain": domain,
        "product_name": product_name,
        # Match preset format
        "category": "Electronics" if "phone" in url.lower() or "headphone" in url.lower() else "Consumer Goods",
        "features": ["Price Value", "Comfort", "Durability", "Performance"],
        "reviews": all_reviews
    }

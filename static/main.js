// Sentiment & Emotion Analytics Dashboard - Frontend Orchestrator

// Stop words for Word Cloud extraction
const STOP_WORDS = new Set([
  "the", "a", "an", "and", "or", "but", "if", "because", "as", "what", "how", "this", 
  "that", "these", "those", "then", "there", "their", "them", "they", "we", "he", "she", 
  "it", "to", "of", "in", "for", "on", "with", "at", "by", "from", "up", "about", 
  "into", "over", "after", "is", "are", "was", "were", "be", "been", "being", 
  "have", "has", "had", "do", "does", "did", "will", "would", "shall", "should", 
  "can", "could", "may", "might", "must", "us", "your", "my", "me", "i", "its", 
  "so", "our", "out", "just", "very", "also", "than", "here", "like", "only", "well", "get", "any", "some"
]);

// Application State
const state = {
  activePanel: "quick",
  presets: null,
  charts: {},
  currentAmazonProduct: null,
  currentSocialHashtag: null,
  bulkUploadedData: null,
  chatLanguage: "",
  settings: JSON.parse(localStorage.getItem("sentimentiq_settings")) || {
    posThreshold: 0.05,
    negThreshold: -0.05,
    debounceDelay: 300,
    customLexicon: {}
  }
};
// Initialization on load

document.addEventListener("DOMContentLoaded", () => {
  fetchPresets();
  setupQuickAnalyzer();
  setupUploader();
  setupAmazonAnalyzer();
  initSettingsPanel();
});

// Fetch simulated datasets from Flask API
async function fetchPresets() {
  try {
    const response = await fetch("/api/presets");
    const data = await response.json();
    state.presets = data;
    
    // Populate simulators
    populateAmazonSimulator();
    populateSocialSimulator();
  } catch (error) {
    console.error("Error fetching presets:", error);
  }
}

// Sidebar Nav Panel Switching
function switchPanel(panelId) {
  // Hide active panels
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  
  // Show target panel
  const targetPanel = document.getElementById(`panel-${panelId}`);
  if (targetPanel) targetPanel.classList.add("active");
  
  const navItem = document.getElementById(`nav-${panelId}`);
  if (navItem) navItem.classList.add("active");
  
  state.activePanel = panelId;

  // Update Top Bar titles
  const titleMap = {
    quick: { title: "Quick Text Analyzer", desc: "Real-time linguistic analytics engine mapping expressions to actionable insights." },
    amazon: { title: "Amazon Product Reviews Simulator", desc: "Aggregate feedback evaluation, rating distributions, and feature-level metrics." },
    social: { title: "Social Hashtag Tracker", desc: "Real-time public opinion tracker measuring viral sentiment and word frequency clouds." },
    settings: { title: "System Settings", desc: "Configure sentiment analysis thresholds, custom dictionary overrides, and UI options." },
    bulk: { title: "Bulk Ingestion Suite", desc: "Drop customer feedback batches (CSV/TXT) to parse immediate executive reports." }
  };
  
  document.getElementById("main-panel-title").innerText = titleMap[panelId].title;
  document.getElementById("main-panel-desc").innerText = titleMap[panelId].desc;
  
  // Repaint charts if needed
  if (panelId === 'amazon' && state.currentAmazonProduct) {
    loadAmazonProduct(state.currentAmazonProduct);
  } else if (panelId === 'social' && state.currentSocialHashtag) {
    loadSocialHashtag(state.currentSocialHashtag);
  } else if (panelId === 'settings') {
    initSettingsPanel();
  }
}

// ==========================================
// 1. QUICK ANALYZER TAB
// ==========================================

let quickAnalysisTimeout = null;

function setupQuickAnalyzer() {
  const input = document.getElementById("quick-text-input");
  // Run initial analysis on placeholder text
  analyzeQuickText(input.value);
}

function onQuickTextInput() {
  const text = document.getElementById("quick-text-input").value;
  document.getElementById("quick-char-counter").innerText = `${text.length} chars`;
  
  // Debounce API calls (using delay from settings)
  clearTimeout(quickAnalysisTimeout);
  quickAnalysisTimeout = setTimeout(() => {
    analyzeQuickText(text);
  }, state.settings.debounceDelay);
}

async function analyzeQuickText(text) {
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, settings: state.settings })
    });
    const results = await response.json();
    
    // Update word count
    document.getElementById("quick-word-count").innerText = `Words: ${results.wordCount}`;
    
    // Update highlighted panel
    const outputPanel = document.getElementById("quick-highlight-output");
    if (results.highlightedHtml) {
      outputPanel.innerHTML = results.highlightedHtml;
      
      // Bind hover events to nlp-words for custom detail display
      document.querySelectorAll(".nlp-word").forEach(wordEl => {
        wordEl.addEventListener("mouseenter", (e) => {
          const detailBox = document.getElementById("quick-hover-details");
          const val = parseFloat(e.target.dataset.val);
          const emotions = e.target.dataset.emotions;
          
          let content = `<strong>Token:</strong> "${e.target.innerText}"`;
          if (!isNaN(val) && val !== 0) {
            const classLabel = val > 0 ? "Positive" : "Negative";
            content += ` | <strong>Valence:</strong> <span style="color:${val > 0 ? 'var(--color-pos)' : 'var(--color-neg)'}">${val > 0 ? '+' : ''}${val.toFixed(2)} (${classLabel})</span>`;
          }
          if (emotions) {
            content += ` | <strong>Emotions:</strong> <span style="color:var(--accent-secondary)">${emotions.split(',').join(', ')}</span>`;
          }
          
          detailBox.innerHTML = content;
          detailBox.style.display = "block";
        });
        
        wordEl.addEventListener("mouseleave", () => {
          document.getElementById("quick-hover-details").style.display = "none";
        });
      });
      
    } else {
      outputPanel.innerHTML = `<span class="highlight-placeholder">Analysis markup will render here as you type...</span>`;
    }
    
    // Update stats counters
    document.getElementById("quick-stat-pos").innerText = results.positiveCount;
    document.getElementById("quick-stat-neu").innerText = results.neutralCount;
    document.getElementById("quick-stat-neg").innerText = results.negativeCount;
    
    // Render charts
    updatePolarityGauge("quick-polarity-gauge", results.polarity, "quick");
    updateEmotionRadar("quick-emotion-radar", results.emotions, "quick");
    
  } catch (error) {
    console.error("Quick analyze failed:", error);
  }
}

// ==========================================
// 2. AMAZON PRODUCT SIMULATOR
// ==========================================

function populateAmazonSimulator() {
  const container = document.getElementById("amazon-selector-row");
  container.innerHTML = "";
  
  state.presets.amazon.forEach((product, idx) => {
    const btn = document.createElement("button");
    btn.className = `selector-btn ${idx === 0 ? 'active' : ''}`;
    btn.innerText = product.name;
    btn.onclick = (e) => {
      document.querySelectorAll("#amazon-selector-row .selector-btn").forEach(b => b.classList.remove("active"));
      e.target.classList.add("active");
      loadAmazonProduct(product);
    };
    container.appendChild(btn);
  });
  
  if (state.presets.amazon.length > 0) {
    loadAmazonProduct(state.presets.amazon[0]);
  }
}

async function loadAmazonProduct(product) {
  if (!product || !product.reviews) {
    console.error("Invalid product or reviews missing");
    return;
  }
  state.currentAmazonProduct = product;
  
  // Step A: Extract texts and query Flask batch endpoint (combine title and text)
  const texts = product.reviews.map(r => (r.title || "") + " " + (r.text || ""));
  
  try {
    const response = await fetch("/api/analyze-batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texts, settings: state.settings })
    });
    const batchData = await response.json();
    const results = batchData.results;
    
    // Step B: Calculate aggregates and attach analysis results back to reviews
    let totalRating = 0;
    let totalPolarity = 0;
    const aggregatedEmotions = { joy: 0, sadness: 0, anger: 0, fear: 0, trust: 0, disgust: 0, anticipation: 0, surprise: 0 };
    
    product.reviews.forEach((rev, idx) => {
      rev.analysis = results[idx];
      totalRating += rev.rating;
      totalPolarity += results[idx].polarity;
      
      // Accumulate raw emotions
      Object.keys(aggregatedEmotions).forEach(key => {
        aggregatedEmotions[key] += results[idx].rawEmotionScores[key] || 0;
      });
    });
    
    const avgRating = totalRating / product.reviews.length;
    const avgPolarity = totalPolarity / product.reviews.length;
    
    // Step C: Update UI headers
    document.getElementById("amazon-reviews-count").innerText = `${product.reviews.length} reviews parsed`;
    document.getElementById("amazon-avg-rating").innerText = avgRating.toFixed(1);
    document.getElementById("amazon-avg-polarity").innerText = avgPolarity.toFixed(2);
    // Update product name display
    document.getElementById("amazon-product-name").innerText = product.name || product.product_name || 'Amazon Product';
    // Compute sentiment distribution for pie chart
    let posCount = 0, neuCount = 0, negCount = 0;
    results.forEach(r => {
      if (r.sentiment === "Positive") posCount++;
      else if (r.sentiment === "Negative") negCount++;
      else neuCount++;
    });
    // Render sentiment distribution pie chart
    const pieCanvas = document.getElementById("amazon-sentiment-pie");
    if (state.charts["amazon_sentiment_pie"]) state.charts["amazon_sentiment_pie"].destroy();
    state.charts["amazon_sentiment_pie"] = new Chart(pieCanvas.getContext("2d"), {
      type: "pie",
      data: {
        labels: ["Positive", "Neutral", "Negative"],
        datasets: [{
          data: [posCount, neuCount, negCount],
          backgroundColor: [
          // Positive gradient (blue to light blue)
          (function(){
            const grad = pieCanvas.getContext('2d').createLinearGradient(0,0,pieCanvas.width,0);
            grad.addColorStop(0, '#3b82f6');
            grad.addColorStop(1, '#93c5fd');
            return grad;
          })(),
          // Neutral gradient (amber to light amber)
          (function(){
            const grad = pieCanvas.getContext('2d').createLinearGradient(0,0,pieCanvas.width,0);
            grad.addColorStop(0, '#f59e0b');
            grad.addColorStop(1, '#fde68a');
            return grad;
          })(),
          // Negative gradient (red to pink)
          (function(){
            const grad = pieCanvas.getContext('2d').createLinearGradient(0,0,pieCanvas.width,0);
            grad.addColorStop(0, '#ef4444');
            grad.addColorStop(1, '#f9a8d4');
            return grad;
          })()
        ],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "bottom" } }
      }
    });
    // Render stars
    const starsContainer = document.getElementById("amazon-rating-stars");
    starsContainer.innerHTML = "";
    const roundedStars = Math.round(avgRating);
    for (let i = 1; i <= 5; i++) {
      starsContainer.innerHTML += i <= roundedStars ? "★" : "☆";
    }
    
    // Polarity index category label
    const polarityLabel = document.getElementById("amazon-sentiment-label");
    if (avgPolarity >= 0.05) {
      polarityLabel.innerText = "Positive Brand Outlook";
      polarityLabel.style.color = "var(--color-pos)";
    } else if (avgPolarity <= -0.05) {
      polarityLabel.innerText = "Negative Brand Friction";
      polarityLabel.style.color = "var(--color-neg)";
    } else {
      polarityLabel.innerText = "Neutral / Mixed Reviews";
      polarityLabel.style.color = "var(--color-neu)";
    }
    
    // Render Review List log
    const reviewsList = document.getElementById("amazon-reviews-list");
    reviewsList.innerHTML = "";
    
    product.reviews.forEach((rev, idx) => {
      const res = results[idx];
      
      const item = document.createElement("div");
      item.className = "list-item";
      
      let badgeClass = "badge-neu";
      if (res.sentiment === "Positive") badgeClass = "badge-pos";
      else if (res.sentiment === "Negative") badgeClass = "badge-neg";
      
      let ratingStars = "";
      for (let s = 1; s <= 5; s++) {
        ratingStars += s <= rev.rating ? "★" : "☆";
      }

      item.innerHTML = `
        <div class="item-meta">
          <span class="item-author">${rev.author} <span style="color:#fbbf24; margin-left:8px;">${ratingStars}</span></span>
          <span class="badge ${badgeClass}">${res.sentiment}</span>
        </div>
        <div class="item-title">${rev.title}</div>
        <div class="item-snippet">${res.highlightedHtml}</div>
        <div class="item-meta" style="margin-top: 8px; font-size: 11px; margin-bottom: 0;">
          <span class="item-date">Parsed: ${rev.date}</span>
          <span class="item-date">Polarity Score: ${res.polarity.toFixed(2)}</span>
        </div>
      `;
      reviewsList.appendChild(item);
    });

    // Step D: Calculate feature matrix scores (look for keyword triggers in reviews)
    const featureContainer = document.getElementById("amazon-feature-matrix");
    featureContainer.innerHTML = "";
    
    if (product.features && product.features.length > 0) {
      // Match feature keywords
      const featureKeywords = {
        "Sound Quality": ["sound", "audio", "bass", "microphone", "mic", "music"],
        "Comfort": ["comfort", "comfortable", "comfy", "heavy", "bulky", "wear", "wearing"],
        "Active Noise Cancellation": ["noise", "anc", "cancellation", "block", "engine", "isolation"],
        "Battery Life": ["battery", "charge", "charging", "solar", "last", "lasts", "week"],
        "Durability": ["durability", "cracked", "broken", "plastic", "build", "rugged"],
        "Price Value": ["price", "worth", "penny", "expensive", "money", "waste"],
        "Skin Brightening": ["glow", "bright", "brightening", "spots", "skin", "complexion"],
        "Moisturization": ["hydrated", "moisture", "smooth", "moisturization", "dry"],
        "Scent": ["scent", "smell", "citrus", "burnt", "fragrance"],
        "Texture": ["texture", "sticky", "absorbing", "light", "heavy"],
        "Packaging/Pump": ["pump", "bottle", "packaging", "leaks", "stuck", "messy"],
        "Skin Sensitivity": ["rash", "burning", "sensitivity", "itchy", "red", "safe", "gentle"],
        "GPS Accuracy": ["gps", "tracking", "sensor", "coordinates", "signal", "hiking"],
        "App Syncing": ["app", "sync", "syncing", "software", "connection", "connect", "bluetooth", "disconnect"]
      };
      
      product.features.forEach(feat => {
        const keywords = featureKeywords[feat] || feat.toLowerCase().split(/[^a-z0-9]+/i).filter(w => w.length > 2);
        let featValenceSum = 0;
        let featCount = 0;
        
        product.reviews.forEach((rev, revIdx) => {
          const textLower = ((rev.title || "") + " " + (rev.text || "")).toLowerCase();
          keywords.forEach(keyword => {
            if (textLower.includes(keyword)) {
              // we average the polarity score of reviews mentioning these features
              featValenceSum += results[revIdx].polarity;
              featCount++;
            }
          });
        });
        
        // Calculate normalized feature score (0% to 100%)
        // mapped from polarity range [-1.0, 1.0] to [0%, 100%]
        let scorePercentage = 50; // default neutral
        if (featCount > 0) {
          const avgFeatPolarity = featValenceSum / featCount;
          scorePercentage = Math.round(((avgFeatPolarity + 1.0) / 2.0) * 100);
        }
        
        const row = document.createElement("div");
        row.className = "feature-bar-row";
        
        // Determine color coding based on feature polarity
        let barColor = "var(--color-neu)";
        if (scorePercentage >= 58) barColor = "var(--color-pos)";
        else if (scorePercentage <= 42) barColor = "var(--color-neg)";
        
        row.innerHTML = `
          <div class="feature-info">
            <span class="feature-name">${feat}</span>
            <span class="feature-score">${scorePercentage}% Positive Alignment</span>
          </div>
          <div class="feature-bar-outer">
            <div class="feature-bar-inner" style="width: ${scorePercentage}%; background-color: ${barColor};"></div>
          </div>
        `;
        featureContainer.appendChild(row);
      });
    } else {
      featureContainer.innerHTML = `<div class="highlight-placeholder" style="text-align: center; width: 100%;">No feature alignment mapping available for this product.</div>`;
    }

    // Step E: Normalize and Draw Emotion Radar
    const totalEmWeight = Object.values(aggregatedEmotions).reduce((a, b) => a + b, 0);
    const normalizedEmotions = {};
    Object.keys(aggregatedEmotions).forEach(k => {
      normalizedEmotions[k] = totalEmWeight > 0 
        ? Math.round((aggregatedEmotions[k] / totalEmWeight) * 100) 
        : 0;
    });
    
    updateEmotionRadar("amazon-emotion-radar", normalizedEmotions, "amazon");
    
    // Step F: Auto-generate Actionable Business Diagnostics
    generateAmazonDiagnostics(avgPolarity, normalizedEmotions, product.features || [], product.reviews, results);

  } catch (error) {
    console.error("Amazon product loading failed:", error);
  }
}

// Generate SWOT-like Actionable Insight Cards
function generateAmazonDiagnostics(avgPolarity, emotions, features, reviews, results) {
  const insightsBox = document.getElementById("amazon-insights-box");
  insightsBox.innerHTML = "";

  // Identify top negative mentions
  let angerSadnessSum = (emotions.anger || 0) + (emotions.sadness || 0);
  let joyTrustSum = (emotions.joy || 0) + (emotions.trust || 0);

  // Marketing Insights
  const marketingCard = document.createElement("div");
  marketingCard.className = "insight-card insight-marketing";
  marketingCard.innerHTML = `
    <div class="insight-icon">M</div>
    <div class="insight-card-info">
      <div class="insight-card-title">Marketing Strategy Recommendation</div>
      <div class="insight-card-desc">${
        joyTrustSum > 40
          ? `High trust and joy levels (${joyTrustSum}% combined) detected. Leverage core user testimonials in advertising. Highlight product benefits in search campaign headlines.`
          : `Linguistic sentiment is highly volatile. Pause aggressive advertising focus on branding and shift budget to local product trial loops or addressing user complaints.`
      }</div>
    </div>
  `;
  insightsBox.appendChild(marketingCard);

  // Product Development Insights
  const productCard = document.createElement("div");
  productCard.className = "insight-card insight-product";
  
  // Scan reviews for hardware/software complaints
  let issueKeywords = ["software", "app", "pump", "broken", "cracked", "disconnect", "headband", "durability"];
  let matchedIssues = [];
  reviews.forEach((rev, idx) => {
    if (results[idx].polarity < -0.2) {
      issueKeywords.forEach(kw => {
        if (rev.text.toLowerCase().includes(kw) && !matchedIssues.includes(kw)) {
          matchedIssues.push(kw);
        }
      });
    }
  });

  productCard.innerHTML = `
    <div class="insight-icon">P</div>
    <div class="insight-card-info">
      <div class="insight-card-title">Product Design & Quality Control</div>
      <div class="insight-card-desc">${
        matchedIssues.length > 0
          ? `Linguistic flags raised for keywords: <strong>${matchedIssues.join(', ')}</strong>. Engineering teams should prioritize hardware casing inspections or release quick software firmware patches.`
          : `Excellent build and feature satisfaction scores. Keep current manufacturing specifications intact and focus on next-generation features design.`
      }</div>
    </div>
  `;
  insightsBox.appendChild(productCard);

  // Risk Management / PR Insights
  if (avgPolarity < 0.1 || angerSadnessSum > 25) {
    const riskCard = document.createElement("div");
    riskCard.className = "insight-card insight-risk";
    riskCard.innerHTML = `
      <div class="insight-icon">R</div>
      <div class="insight-card-info">
        <div class="insight-card-title">Escalating Reputational Risks</div>
        <div class="insight-card-desc">
          Anger/Sadness indexes are elevated at ${angerSadnessSum}%. Customer support response delays are triggering negative reviews. Immediate escalation of customer refunds requested.
        </div>
      </div>
    `;
    insightsBox.appendChild(riskCard);
  }
}

// ==========================================
// 3. SOCIAL MEDIA TRACKER TAB
// ==========================================

function populateSocialSimulator() {
  const container = document.getElementById("social-selector-row");
  container.innerHTML = "";
  
  state.presets.social.forEach((topic, idx) => {
    const btn = document.createElement("button");
    btn.className = `selector-btn ${idx === 0 ? 'active' : ''}`;
    btn.innerText = `#${topic.hashtag}`;
    btn.onclick = (e) => {
      document.querySelectorAll("#social-selector-row .selector-btn").forEach(b => b.classList.remove("active"));
      e.target.classList.add("active");
      loadSocialHashtag(topic);
    };
    container.appendChild(btn);
  });
  
  if (state.presets.social.length > 0) {
    loadSocialHashtag(state.presets.social[0]);
  }
}

async function loadSocialHashtag(topic) {
  state.currentSocialHashtag = topic;
  const texts = topic.posts.map(p => p.text);
  
  try {
    const response = await fetch("/api/analyze-batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texts, settings: state.settings })
    });
    const batchData = await response.json();
    const results = batchData.results;
    
    let totalInteractions = 0;
    
    // Step A: Update list
    const postsList = document.getElementById("social-posts-list");
    postsList.innerHTML = "";
    
    topic.posts.forEach((post, idx) => {
      post.analysis = results[idx];
      const res = results[idx];
      totalInteractions += (post.interactions.likes + post.interactions.retweets);
      
      const item = document.createElement("div");
      item.className = "social-post";
      
      let badgeClass = "badge-neu";
      if (res.sentiment === "Positive") badgeClass = "badge-pos";
      else if (res.sentiment === "Negative") badgeClass = "badge-neg";

      item.innerHTML = `
        <div class="social-header">
          <span class="social-user">${post.user}</span>
          <span class="badge ${badgeClass}">${res.sentiment}</span>
        </div>
        <div class="social-text">${res.highlightedHtml}</div>
        <div class="social-footer">
          <div class="social-stat">
            <svg viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-dasharray="none" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
            </svg>
            <span>${post.interactions.likes} Likes</span>
          </div>
          <div class="social-stat">
            <svg viewBox="0 0 24 24" width="12" height="12" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="17 1 21 5 17 9"></polyline>
              <path d="M3 11V9a4 4 0 0 1 4-4h14"></path>
              <polyline points="7 23 3 19 7 15"></polyline>
              <path d="M21 13v2a4 4 0 0 1-4 4H3"></path>
            </svg>
            <span>${post.interactions.retweets} Retweets</span>
          </div>
          <span class="social-time">${post.timestamp}</span>
        </div>
      `;
      postsList.appendChild(item);
    });
    
    // Step B: Update Stats
    document.getElementById("social-post-count").innerText = topic.posts.length;
    document.getElementById("social-total-interactions").innerText = totalInteractions.toLocaleString();
    
    // Step B2: Sentiment & Emotion Visualizations
    let posCount = 0, neuCount = 0, negCount = 0;
    const emotionsSum = { joy: 0, trust: 0, fear: 0, surprise: 0, sadness: 0, disgust: 0, anger: 0, anticipation: 0 };
    
    results.forEach(res => {
      if (res.sentiment === "Positive") posCount++;
      else if (res.sentiment === "Negative") negCount++;
      else neuCount++;
      
      const emo = res.emotions || {};
      for (let k in emotionsSum) {
        emotionsSum[k] += (emo[k] || 0);
      }
    });
    
    const totalResults = results.length || 1;
    const averageEmotions = {};
    for (let k in emotionsSum) {
      averageEmotions[k] = Math.round(emotionsSum[k] / totalResults);
    }
    
    // Render sentiment pie chart for social
    const socialPieCanvas = document.getElementById("social-sentiment-pie");
    if (state.charts["social_sentiment_pie"]) {
      state.charts["social_sentiment_pie"].destroy();
    }
    
    const totalCount = posCount + neuCount + negCount || 1;
    const posPercent = Math.round((posCount / totalCount) * 100);
    const neuPercent = Math.round((neuCount / totalCount) * 100);
    const negPercent = Math.round((negCount / totalCount) * 100);

    state.charts["social_sentiment_pie"] = new Chart(socialPieCanvas.getContext("2d"), {
      type: "pie",
      data: {
        labels: [`Positive (${posPercent}%)`, `Neutral (${neuPercent}%)`, `Negative (${negPercent}%)`],
        datasets: [{
          data: [posCount, neuCount, negCount],
          backgroundColor: [
            // Positive gradient (blue to light blue)
            (function(){
              const grad = socialPieCanvas.getContext('2d').createLinearGradient(0,0,socialPieCanvas.width,0);
              grad.addColorStop(0, '#3b82f6');
              grad.addColorStop(1, '#93c5fd');
              return grad;
            })(),
            // Neutral gradient (amber to light amber)
            (function(){
              const grad = socialPieCanvas.getContext('2d').createLinearGradient(0,0,socialPieCanvas.width,0);
              grad.addColorStop(0, '#f59e0b');
              grad.addColorStop(1, '#fde68a');
              return grad;
            })(),
            // Negative gradient (red to pink)
            (function(){
              const grad = socialPieCanvas.getContext('2d').createLinearGradient(0,0,socialPieCanvas.width,0);
              grad.addColorStop(0, '#ef4444');
              grad.addColorStop(1, '#f9a8d4');
              return grad;
            })()
          ],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              color: "#9ca3af",
              font: { family: "Outfit", size: 10 }
            }
          }
        }
      }
    });
    
    // Render emotion radar chart
    updateEmotionRadar("social-emotion-radar", averageEmotions, "social");
    
    // Step C: Generate Word Cloud frequencies
    generateWordCloud(texts);
    
    // Step D: PR Strategies insights
    generateSocialStrategy(topic.hashtag, results);
    
  } catch (error) {
    console.error("Social loading failed:", error);
  }
}

async function trackCustomSocialTopic() {
  const inputEl = document.getElementById("social-custom-query");
  const btnEl = document.getElementById("social-search-btn");
  const query = inputEl ? inputEl.value.trim() : "";
  
  if (!query) {
    alert("Please enter a valid topic or hashtag to search.");
    return;
  }
  
  btnEl.disabled = true;
  const originalText = btnEl.innerText;
  btnEl.innerText = "Tracking Feed...";
  
  try {
    const response = await fetch("/api/social-search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    
    const data = await response.json();
    if (data.error) {
      alert("Error tracking feed: " + data.error);
      return;
    }
    
    if (!data.posts || data.posts.length === 0) {
      alert("No recent feed items found for this topic. Try another keyword.");
      return;
    }
    
    // De-activate current preset buttons
    document.querySelectorAll("#social-selector-row .selector-btn").forEach(b => b.classList.remove("active"));
    
    // Load the custom feed using existing loadSocialHashtag logic, but using the fetched data
    await loadSocialHashtag(data);
    
  } catch (error) {
    console.error("Failed to fetch custom social topic:", error);
    alert("An error occurred while tracking the live feed.");
  } finally {
    btnEl.disabled = false;
    btnEl.innerText = originalText;
  }
}

// Simple HTML/CSS Word Cloud layout generator
function generateWordCloud(texts) {
  const cloudContainer = document.getElementById("social-wordcloud");
  cloudContainer.innerHTML = "";
  
  // Count frequencies
  const frequencies = {};
  texts.forEach(text => {
    // clean words
    const words = text.toLowerCase()
      .replace(/#[a-zA-Z0-9]+/g, "") // remove hashtags
      .replace(/@[a-zA-Z0-9_]+/g, "") // remove handles
      .split(/[^a-zA-Z]+/);
      
    words.forEach(w => {
      if (w.length > 3 && !STOP_WORDS.has(w)) {
        frequencies[w] = (frequencies[w] || 0) + 1;
      }
    });
  });
  
  // Sort frequencies
  const sorted = Object.entries(frequencies)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 15); // Top 15 words
    
  if (sorted.length === 0) {
    cloudContainer.innerHTML = `<span class="highlight-placeholder">No cloud keywords detected</span>`;
    return;
  }
  
  const maxFreq = sorted[0][1];
  
  sorted.forEach(([word, freq]) => {
    // Scale font size from 12px to 32px
    const size = 12 + Math.round((freq / maxFreq) * 20);
    const span = document.createElement("span");
    span.className = "cloud-word";
    span.innerText = word;
    span.style.fontSize = `${size}px`;
    
    // Assign random positions (with safe padding)
    const left = 15 + Math.random() * 70;
    const top = 15 + Math.random() * 70;
    
    span.style.left = `${left}%`;
    span.style.top = `${top}%`;
    
    // Color code based on lexicon sentiment matching
    let color = "var(--text-secondary)";
    const cleanW = word.toLowerCase();
    if (SENTIMENT_LEXICON[cleanW] > 0.1) {
      color = "var(--color-pos)";
    } else if (SENTIMENT_LEXICON[cleanW] < -0.1) {
      color = "var(--color-neg)";
    }
    span.style.color = color;
    span.title = `Frequency: ${freq}`;
    
    cloudContainer.appendChild(span);
  });
}

function generateSocialStrategy(hashtag, results) {
  const insightsBox = document.getElementById("social-insights-box");
  insightsBox.innerHTML = "";
  
  let positiveCount = 0;
  let negativeCount = 0;
  results.forEach(res => {
    if (res.sentiment === "Positive") positiveCount++;
    else if (res.sentiment === "Negative") negativeCount++;
  });
  
  const posRatio = results.length > 0 ? (positiveCount / results.length) * 100 : 0;
  const negRatio = results.length > 0 ? (negativeCount / results.length) * 100 : 0;
  
  const prCard = document.createElement("div");
  prCard.className = "insight-card";
  
  if (negRatio > 40) {
    prCard.className += " insight-risk";
    prCard.innerHTML = `
      <div class="insight-icon">🚨</div>
      <div class="insight-card-info">
        <div class="insight-card-title">Immediate PR Containment Required</div>
        <div class="insight-card-desc">
          Brand mentions for #${hashtag} have crossed a critical risk threshold with <strong>${negRatio.toFixed(0)}% negative sentiment</strong>. Outage panic or pricing criticism is spreading. Release a transparent statement on channels immediately.
        </div>
      </div>
    `;
  } else if (posRatio > 50) {
    prCard.className += " insight-product";
    prCard.innerHTML = `
      <div class="insight-icon">📢</div>
      <div class="insight-card-info">
        <div class="insight-card-title">Amplification Opportunity</div>
        <div class="insight-card-desc">
          Viral excitement for #${hashtag} is strongly positive (<strong>${posRatio.toFixed(0)}% positive sentiment</strong>). Launch a retargeting ad campaign to capture traffic. Promote top positive user quotes on official profiles.
        </div>
      </div>
    `;
  } else {
    prCard.className += " insight-marketing";
    prCard.innerHTML = `
      <div class="insight-icon">📊</div>
      <div class="insight-card-info">
        <div class="insight-card-title">Engagement Strategy</div>
        <div class="insight-card-desc">
          Linguistic indicators show neutral/mixed interest in #${hashtag}. Focus on posting engaging interactive polls or updates to stimulate organic audience growth.
        </div>
      </div>
    `;
  }
  insightsBox.appendChild(prCard);
}

// ==========================================
// 4. SETTINGS & CUSTOM DICTIONARY LOGIC
// ==========================================

function initSettingsPanel() {
  // Load settings into DOM elements
  document.getElementById("setting-pos-threshold").value = state.settings.posThreshold;
  document.getElementById("val-pos-threshold").innerText = state.settings.posThreshold.toFixed(2);

  document.getElementById("setting-neg-threshold").value = state.settings.negThreshold;
  document.getElementById("val-neg-threshold").innerText = state.settings.negThreshold.toFixed(2);

  document.getElementById("setting-debounce-delay").value = state.settings.debounceDelay;
  document.getElementById("val-debounce-delay").innerText = `${state.settings.debounceDelay}ms`;

  document.getElementById("custom-valence-input").value = 1.0;
  document.getElementById("val-custom-valence").innerText = "+1.0";
  document.getElementById("custom-word-input").value = "";

  renderCustomLexiconList();
}

function updateSettingsValues() {
  const posVal = parseFloat(document.getElementById("setting-pos-threshold").value);
  document.getElementById("val-pos-threshold").innerText = posVal.toFixed(2);

  const negVal = parseFloat(document.getElementById("setting-neg-threshold").value);
  document.getElementById("val-neg-threshold").innerText = negVal.toFixed(2);

  const delayVal = parseInt(document.getElementById("setting-debounce-delay").value);
  document.getElementById("val-debounce-delay").innerText = `${delayVal}ms`;
}

function updateCustomValenceLabel() {
  const val = parseFloat(document.getElementById("custom-valence-input").value);
  const prefix = val > 0 ? "+" : "";
  document.getElementById("val-custom-valence").innerText = `${prefix}${val.toFixed(1)}`;
}

function saveSettings() {
  state.settings.posThreshold = parseFloat(document.getElementById("setting-pos-threshold").value);
  state.settings.negThreshold = parseFloat(document.getElementById("setting-neg-threshold").value);
  state.settings.debounceDelay = parseInt(document.getElementById("setting-debounce-delay").value);
  
  localStorage.setItem("sentimentiq_settings", JSON.stringify(state.settings));
  
  // Apply visual changes by re-running active analyses
  if (state.currentAmazonProduct) {
    loadAmazonProduct(state.currentAmazonProduct);
  }
  if (state.currentSocialHashtag) {
    loadSocialHashtag(state.currentSocialHashtag);
  }
  if (state.bulkUploadedData) {
    reprocessBulkData();
  }
  
  const quickInput = document.getElementById("quick-text-input");
  if (quickInput) {
    analyzeQuickText(quickInput.value);
  }
  
  alert("Settings saved and applied successfully!");
}

function resetSettings() {
  if (confirm("Are you sure you want to reset all settings to defaults?")) {
    state.settings = {
      posThreshold: 0.05,
      negThreshold: -0.05,
      debounceDelay: 300,
      customLexicon: {}
    };
    localStorage.removeItem("sentimentiq_settings");
    initSettingsPanel();
    saveSettings();
  }
}

function addCustomWord() {
  const wordInput = document.getElementById("custom-word-input");
  const word = wordInput.value.trim().toLowerCase();
  
  if (!word) {
    alert("Please enter a valid word or token.");
    return;
  }
  
  if (word.split(/\s+/).length > 1) {
    alert("Please enter a single word. Multi-word phrases are not supported in the word-level lexicon.");
    return;
  }

  const valence = parseFloat(document.getElementById("custom-valence-input").value);
  
  state.settings.customLexicon[word] = valence;
  localStorage.setItem("sentimentiq_settings", JSON.stringify(state.settings));
  
  wordInput.value = "";
  document.getElementById("custom-valence-input").value = 1.0;
  updateCustomValenceLabel();
  
  renderCustomLexiconList();
  
  // Re-run active analyses to reflect changes immediately
  saveSettings();
}

function removeCustomWord(word) {
  if (state.settings.customLexicon[word] !== undefined) {
    delete state.settings.customLexicon[word];
    localStorage.setItem("sentimentiq_settings", JSON.stringify(state.settings));
    renderCustomLexiconList();
    saveSettings();
  }
}

function renderCustomLexiconList() {
  const listEl = document.getElementById("custom-lexicon-list");
  listEl.innerHTML = "";
  
  const entries = Object.entries(state.settings.customLexicon);
  if (entries.length === 0) {
    listEl.innerHTML = `<span class="highlight-placeholder" style="padding: 10px;">No custom overrides defined.</span>`;
    return;
  }
  
  entries.forEach(([word, val]) => {
    const item = document.createElement("div");
    item.className = "list-item";
    item.style.display = "flex";
    item.style.justifyContent = "space-between";
    item.style.alignItems = "center";
    item.style.padding = "10px 14px";
    item.style.margin = "0";
    
    let badgeClass = "badge-neu";
    if (val > 0.1) badgeClass = "badge-pos";
    else if (val < -0.1) badgeClass = "badge-neg";
    
    const prefix = val > 0 ? "+" : "";
    
    item.innerHTML = `
      <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-family: var(--font-heading); font-weight: 600; color: var(--text-primary);">"${word}"</span>
        <span class="badge ${badgeClass}">${prefix}${val.toFixed(1)}</span>
      </div>
      <button class="btn btn-secondary" onclick="removeCustomWord('${word}')" style="min-width: unset; padding: 4px 8px; font-size: 11px; border-radius: 6px; border-color: rgba(239, 68, 68, 0.4); color: #f87171;">
        Remove
      </button>
    `;
    listEl.appendChild(item);
  });
}

// Reprocess bulk uploaded records using the updated thresholds/lexicon
async function reprocessBulkData() {
  if (!state.bulkUploadedData || !state.bulkUploadedData.records) return;
  
  const texts = state.bulkUploadedData.records.map(r => r.text);
  try {
    const response = await fetch("/api/analyze-batch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texts, settings: state.settings })
    });
    const batchData = await response.json();
    
    state.bulkUploadedData.records = texts.map((t, idx) => ({
      text: t,
      result: batchData.results[idx]
    }));
    
    renderBulkResults();
  } catch (err) {
    console.error("Failed to re-process bulk data:", err);
  }
}

// ==========================================
// 5. BULK DATA UPLOADER TAB
// ==========================================

function setupUploader() {
  const dropzone = document.getElementById("uploader-box");
  
  // Drag over animations
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });
  
  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });
  
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    
    if (e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  });
}

function setupAmazonAnalyzer() {
  const btn = document.getElementById("amazon-analyze-btn");
  const input = document.getElementById("amazon-url");
  const resultDiv = document.getElementById("amazon-result");

  btn.addEventListener("click", async () => {
    const url = input.value.trim();
    if (!url) {
      resultDiv.innerHTML = `<span class="highlight-placeholder">Please enter a valid Amazon product URL.</span>`;
      return;
    }

    btn.disabled = true;
    btn.innerText = "Analyzing...";
    resultDiv.innerHTML = `<span class="highlight-placeholder">Analyzing reviews, please wait...</span>`;

    try {
      const response = await fetch("/api/amazon-analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, settings: state.settings })
      });
      const data = await response.json();
      if (data.error) {
        resultDiv.innerHTML = `<span class="highlight-placeholder error">Error: ${data.error}</span>`;
        return;
      }

      // Render full Amazon dashboard using existing logic
      await loadAmazonProduct(data);
      // Clear placeholder and switch to Amazon panel to show visualizations
      resultDiv.innerHTML = "";
      switchPanel('amazon');
    } catch (e) {
      console.error("Amazon analysis failed:", e);
      resultDiv.innerHTML = `<span class="highlight-placeholder error">Failed to analyze the URL.</span>`;
    } finally {
      btn.disabled = false;
      btn.innerText = "Analyze URL";
    }
  });
}


function triggerFileSelect() {
  document.getElementById("file-input").click();
}

function handleFileSelect(e) {
  if (e.target.files.length > 0) {
    processFile(e.target.files[0]);
  }
}

function processFile(file) {
  const reader = new FileReader();
  
  reader.onload = async (event) => {
    const content = event.target.result;
    let texts = [];
    
    if (file.name.endsWith(".csv")) {
      // Basic CSV parsing
      const lines = content.split(/\r?\n/);
      if (lines.length < 2) return;
      
      const headers = lines[0].split(",");
      // Try to find a text column
      let textColIndex = 0;
      headers.forEach((h, index) => {
        const cleaned = h.toLowerCase().trim();
        if (cleaned.includes("review") || cleaned.includes("text") || cleaned.includes("comment") || cleaned.includes("body") || cleaned.includes("feedback")) {
          textColIndex = index;
        }
      });
      
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        // Split handling simple quoted commas
        const cols = line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);
        if (cols[textColIndex]) {
          // Strip surrounding quotes
          texts.push(cols[textColIndex].replace(/^["']|["']$/g, "").trim());
        }
      }
    } else {
      // Text file - treat each paragraph/line as a feedback item
      texts = content.split(/\r?\n\r?\n/).map(t => t.trim()).filter(t => t.length > 0);
    }
    
    if (texts.length === 0) {
      alert("No readable text found in the file!");
      return;
    }
    
    // Slice large files to prevent timeouts in UI demo
    if (texts.length > 50) {
      texts = texts.slice(0, 50);
      console.log("File sliced to 50 rows for display convenience.");
    }
    
    // Post to Flask batch endpoint
    try {
      const response = await fetch("/api/analyze-batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texts, settings: state.settings })
      });
      const batchData = await response.json();
      
      state.bulkUploadedData = {
        fileName: file.name,
        records: texts.map((t, idx) => ({
          text: t,
          result: batchData.results[idx]
        }))
      };
      
      renderBulkResults();
    } catch (err) {
      console.error("Bulk upload batch request failed:", err);
    }
  };
  
  reader.readAsText(file);
}

function renderBulkResults() {
  const data = state.bulkUploadedData;
  document.getElementById("bulk-results-area").style.display = "grid";
  
  // Aggregate calculations
  const total = data.records.length;
  let polaritySum = 0;
  let posCount = 0;
  let neuCount = 0;
  let negCount = 0;
  const aggregatedEmotions = { joy: 0, sadness: 0, anger: 0, fear: 0, trust: 0, disgust: 0, anticipation: 0, surprise: 0 };
  
  const recordsList = document.getElementById("bulk-records-list");
  recordsList.innerHTML = "";
  
  data.records.forEach((rec, idx) => {
    polaritySum += rec.result.polarity;
    
    if (rec.result.sentiment === "Positive") posCount++;
    else if (rec.result.sentiment === "Negative") negCount++;
    else neuCount++;
    
    // Accumulate emotions
    Object.keys(aggregatedEmotions).forEach(key => {
      aggregatedEmotions[key] += rec.result.rawEmotionScores[key] || 0;
    });
    
    // Append item
    const item = document.createElement("div");
    item.className = "list-item";
    
    let badgeClass = "badge-neu";
    if (rec.result.sentiment === "Positive") badgeClass = "badge-pos";
    else if (rec.result.sentiment === "Negative") badgeClass = "badge-neg";
    
    item.innerHTML = `
      <div class="item-meta">
        <span class="item-author" style="color:var(--text-muted)">Record #${idx + 1}</span>
        <span class="badge ${badgeClass}">${rec.result.sentiment}</span>
      </div>
      <div class="item-snippet" style="font-size: 13px;">${rec.result.highlightedHtml}</div>
    `;
    recordsList.appendChild(item);
  });
  
  const avgPolarity = polaritySum / total;
  
  // Update Stats UI
  document.getElementById("bulk-stat-total").innerText = total;
  document.getElementById("bulk-stat-polarity").innerText = avgPolarity.toFixed(2);
  
  // Update Distribution Progress bars
  const posPerc = Math.round((posCount / total) * 100);
  const neuPerc = Math.round((neuCount / total) * 100);
  const negPerc = Math.round((negCount / total) * 100);
  
  document.getElementById("bulk-progress-pos").style.width = `${posPerc}%`;
  document.getElementById("bulk-progress-pos-label").innerText = `${posPerc}%`;
  
  document.getElementById("bulk-progress-neu").style.width = `${neuPerc}%`;
  document.getElementById("bulk-progress-neu-label").innerText = `${neuPerc}%`;
  
  document.getElementById("bulk-progress-neg").style.width = `${negPerc}%`;
  document.getElementById("bulk-progress-neg-label").innerText = `${negPerc}%`;
  
  // Normalize Emotions Radar
  const totalEmWeight = Object.values(aggregatedEmotions).reduce((a, b) => a + b, 0);
  const normalizedEmotions = {};
  Object.keys(aggregatedEmotions).forEach(k => {
    normalizedEmotions[k] = totalEmWeight > 0 
      ? Math.round((aggregatedEmotions[k] / totalEmWeight) * 100) 
      : 0;
  });
  
  updateEmotionRadar("bulk-emotion-radar", normalizedEmotions, "bulk");
}

function downloadJSONReport() {
  if (!state.bulkUploadedData) return;
  
  const blob = new Blob([JSON.stringify(state.bulkUploadedData, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement("a");
  a.href = url;
  a.download = `SentimentIQ_Report_${state.bulkUploadedData.fileName.replace(/\.[^/.]+$/, "")}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ==========================================
// CHART.JS HELPER RENDERING FUNCTIONS
// ==========================================

// 1. Polarity Speedometer Gauge (Half-Doughnut)
function updatePolarityGauge(canvasId, polarityValue, chartNamespace) {
  const ctx = document.getElementById(canvasId).getContext("2d");
  
  // Polarity value is -1.0 to +1.0. We map it to [0, 100] for display mapping
  const mappedVal = Math.round(((polarityValue + 1.0) / 2.0) * 100);
  const remainder = 100 - mappedVal;
  
  // Dynamic color based on polarity score
  let needleColor = "#9ca3af";
  let labelText = "Neutral";
  if (polarityValue >= 0.05) {
    needleColor = "var(--color-pos)";
    labelText = "Positive";
  } else if (polarityValue <= -0.05) {
    needleColor = "var(--color-neg)";
    labelText = "Negative";
  }
  
  // Update DOM labels if Quick analyzer
  if (chartNamespace === "quick") {
    document.getElementById("quick-polarity-value").innerText = polarityValue.toFixed(2);
    document.getElementById("quick-polarity-label").innerText = labelText;
    document.getElementById("quick-polarity-label").style.color = needleColor;
  }
  
  if (state.charts[chartNamespace + "_polarity"]) {
    state.charts[chartNamespace + "_polarity"].destroy();
  }
  
  state.charts[chartNamespace + "_polarity"] = new Chart(ctx, {
    type: "doughnut",
    data: {
      datasets: [
        {
          data: [mappedVal, remainder],
          backgroundColor: [needleColor, "rgba(255, 255, 255, 0.05)"],
          borderWidth: 0,
          cutout: "85%"
        }
      ]
    },
    options: {
      circumference: 180,
      rotation: 270,
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      }
    }
  });
}

// 2. Plutchik Emotion Radar (8 Facets)
function updateEmotionRadar(canvasId, emotionsData, chartNamespace) {
  const ctx = document.getElementById(canvasId).getContext("2d");
  
  const labels = ["Joy", "Trust", "Fear", "Surprise", "Sadness", "Disgust", "Anger", "Anticipation"];
  const keys = ["joy", "trust", "fear", "surprise", "sadness", "disgust", "anger", "anticipation"];
  const values = keys.map(k => emotionsData[k] || 0);
  
  if (state.charts[chartNamespace + "_emotions"]) {
    state.charts[chartNamespace + "_emotions"].destroy();
  }
  
  state.charts[chartNamespace + "_emotions"] = new Chart(ctx, {
    type: "radar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Linguistic Percentage Weight",
          data: values,
          backgroundColor: "rgba(139, 92, 246, 0.2)",
          borderColor: "#8b5cf6",
          borderWidth: 2,
          pointBackgroundColor: "#8b5cf6",
          pointBorderColor: "#ffffff",
          pointHoverBackgroundColor: "#ffffff",
          pointHoverBorderColor: "#8b5cf6"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          grid: { color: "rgba(255, 255, 255, 0.06)" },
          angleLines: { color: "rgba(255, 255, 255, 0.06)" },
          ticks: { display: false, stepSize: 20 },
          pointLabels: {
            color: "var(--text-secondary)",
            font: { family: "Outfit", size: 10, weight: "600" }
          },
          suggestedMin: 0,
          suggestedMax: 60
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// ==========================================
// AI CHATBOT INTERACTIVE CONTROLLER
// ==========================================
function toggleChatWindow() {
  const windowEl = document.getElementById("chat-window");
  windowEl.classList.toggle("active");
  if (windowEl.classList.contains("active")) {
    document.getElementById("chat-input").focus();
  }
}

function handleChatKeyPress(event) {
  if (event.key === "Enter") {
    sendChatMessage();
  }
}

async function sendChatMessage() {
  const inputEl = document.getElementById("chat-input");
  const message = inputEl.value.trim();
  if (!message) return;

  // Clear input
  inputEl.value = "";

  // Append user message
  appendChatBubble(message, "user");

  // Determine active product & hashtag
  const activeProduct = state.currentAmazonProduct ? (state.currentAmazonProduct.productId || state.currentAmazonProduct.asin || "") : "";
  const activeHashtag = state.currentSocialHashtag ? (state.currentSocialHashtag.hashtag || "") : "";

  // Determine typing indicator language
  const isHindi = state.chatLanguage === "hindi";
  const typingText = isHindi ? "Co-Pilot response type ho raha hai..." : "Typing Co-Pilot feedback...";

  // Append typing indicator
  const botBubble = appendChatBubble(typingText, "bot typing");

  try {
    const response = await fetch("/api/chatbot", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        activeProduct: activeProduct,
        activeHashtag: activeHashtag,
        preferredLanguage: state.chatLanguage || "",
        currentProduct: state.currentAmazonProduct,
        currentSocial: state.currentSocialHashtag
      })
    });
    const data = await response.json();
    
    // Update language preference
    if (data.language) {
      state.chatLanguage = data.language;
    }
    
    // Replace typing indicator with actual reply
    botBubble.innerHTML = `<p>${data.reply}</p>`;
    botBubble.classList.remove("typing");
  } catch (error) {
    console.error("Chatbot failed:", error);
    const errorMsg = state.chatLanguage === "hindi"
      ? "Maaf kijiyega, main server se connect nahi ho paa raha hoon. Kripya check karein ki backend app active hai ya nahi."
      : "Sorry, I am unable to connect to the server. Please check if the backend application is running.";
    botBubble.innerHTML = `<p>${errorMsg}</p>`;
    botBubble.classList.remove("typing");
  }

  // Scroll to bottom
  const bodyEl = document.getElementById("chat-body");
  bodyEl.scrollTop = bodyEl.scrollHeight;
}

function appendChatBubble(text, sender) {
  const bodyEl = document.getElementById("chat-body");
  const msgEl = document.createElement("div");
  msgEl.className = `chat-msg ${sender}`;
  msgEl.innerHTML = `<p>${text}</p>`;
  bodyEl.appendChild(msgEl);
  bodyEl.scrollTop = bodyEl.scrollHeight;
  return msgEl;
}




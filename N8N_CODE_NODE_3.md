# Updated n8n Code Node 3 - Format Prompt (Handles Empty News)

When setting up Node 3 in n8n (Code node after HTTP Request), use this JavaScript:

```javascript
const data = $input.first().json;

// Build news context - handle empty news
let newsContext = "";
if (data.news && data.news.length > 0) {
  newsContext = data.news.map((article, index) => 
    `${index + 1}. ${article.ai_context || article.title || 'No title'}`
  ).join('\n\n');
} else {
  newsContext = "No recent news available. Analyzing based on company fundamentals and market trends.";
}

// The Flask app now builds the full prompt, but we can also handle it here
const prompt = data.prompt_template; // Already includes news context or fallback

return [{
  json: {
    ticker: data.ticker,
    stock: data.stock,
    prompt: prompt,
    timestamp: data.timestamp,
    has_news: data.news && data.news.length > 0
  }
}];
```

This will:
1. Check if news array has articles
2. If yes: format them with ai_context
3. If no: use fallback text
4. Pass complete prompt to OpenAI

The Flask backend now also handles empty news by including a fallback message in the prompt itself.

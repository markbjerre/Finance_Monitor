# Fix for n8n Code Node 2 (Parse Response) - OpenAI Response Structure

The error occurs because the OpenAI node response structure is different. 

## Updated Code Node 2 - Parse Response

Replace the code in the second Code node with this:

```javascript
const input = $input.first().json;

// OpenAI response is directly in the input
// Check what we actually got
console.log("Input:", JSON.stringify(input, null, 2).substring(0, 500));

let analysis = {};

// Handle different possible response structures
if (input.response) {
  // If wrapped in response
  analysis = typeof input.response === 'string' 
    ? JSON.parse(input.response) 
    : input.response;
} else if (input.text) {
  // If in text field
  analysis = typeof input.text === 'string' 
    ? JSON.parse(input.text) 
    : input.text;
} else if (typeof input === 'string') {
  // If entire input is string
  analysis = JSON.parse(input);
} else {
  // Last resort: convert to string and parse
  const str = JSON.stringify(input);
  try {
    analysis = JSON.parse(str);
  } catch (e) {
    console.log("Could not parse, using raw input");
    analysis = input;
  }
}

// Ensure required fields exist
const result = {
  ticker: input.ticker || "META",
  content: JSON.stringify(analysis),
  sentiment: analysis.sentiment || "neutral",
  risk_level: analysis.risk_level || "medium",
  insight_type: "daily"
};

console.log("Result:", JSON.stringify(result, null, 2));

return [{ json: result }];
```

## How to Fix:

1. **In n8n, go to the second Code node** (after OpenAI)
2. **Delete the existing code**
3. **Paste the code above**
4. **Click "Execute Node"** to test
5. **Look at the output** - it will show what the actual OpenAI structure is
6. **Adjust if needed based on what you see**

## Alternative: Check OpenAI Node Output First

Before fixing the Code node:

1. **In the OpenAI node output panel**, look at what's actually returned
2. The response might be in a different field
3. Common fields: `text`, `response`, `message`, `content`, `choices[0].message.content`

Let me know what the OpenAI node output shows and I'll adjust the Code node!

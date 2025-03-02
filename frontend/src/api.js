const openAIKey = import.meta.env.VITE_APP_OPENAI_API_KEY;

export async function getCompanies(data = {}) {
  if (!openAIKey) {
    console.error('OpenAI API key is missing. Please check your environment variables.');
    return;
  }

  try {
    console.log('Using OpenAI Key:', openAIKey);

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${openAIKey}`
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: 'You are a helpful assistant that finds companies matching specific criteria.'
          },
          {
            role: 'user',
            content: `Find 3 companies that match these criteria: Industry: ${data.industry || 'Any'}, Size: ${data.size || 'Any'}, Location: ${data.location || 'Any'}, Sector: ${data.sector || 'Any'}. For each company, provide the name, website or email, and a brief description.`
          }
        ],
        temperature: 0.7
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`API error: ${errorData.error?.message || response.statusText}`);
    }

    const responseData = await response.json();
    return responseData;
  } catch (err) {
    console.error('An error occurred while calling the OpenAI API:', err);
  }
}

export async function generateEmail(companyName: string) {
    try {
    console.log(`Sending request for company: ${companyName}`);

      const response = await fetch('/api/prompts/generate_email/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company_name: companyName,
        }),
      });

      console.log(`Response status: ${response.status}`);
      console.log(`Response type: ${response.type}`);

      // Check if response is empty
        const text = await response.text();
        console.log(`Raw response text: ${text.substring(0, 200)}...`);
        
        if (!text) {
        throw new Error('Empty response from server');
        }
    
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate email');
      }
  
      const data = await response.json();
      return data.email;
    } catch (error) {
      console.error('Error generating email:', error);
      throw error;
    }
  }
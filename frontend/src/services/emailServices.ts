// emailServices.ts
const generateEmail = async (company: string) => {
  console.log(`Sending request for company: ${company}`);
  try {
    const response = await fetch('http://localhost:8000/api/prompts/generate_email/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ company_name: company }),
    });

    console.log(`Response status: ${response.status}`);
    if (!response.ok) {
      const errorText = await response.text();
      console.log('Error response:', errorText);
      throw new Error('Failed to generate email');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error generating email:', error);
    throw error;
  }
};

export default generateEmail
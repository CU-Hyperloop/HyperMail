import axios from 'axios';

async function getCompanies(params = {}) {
  const data = {
    industry: params.industry || "Technology",
    size: params.size || "Medium",
    sector: params.sector || "Software",
    location: params.location || "California",
    vibe: params.vibe || "Professional"
  };

  const res = await axios.post('http://localhost:8000/api/emailGenerator/generate/', data, {
    headers: {
      "Content-Type": "application/json"
    }
  });

  console.log(res.data);
  return res.data; // axios automatically parses JSON
}

export default getCompanies
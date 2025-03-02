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


export async function sendEmail(emailData={}) {

  const data = {
    to_email: emailData.to_email || "harikakondur3@gmail.com",
    subject: emailData.subject || "Medium",
    cc_email: emailData.cc_email || "hako6198@colorado.edu",
    message: emailData.message || "California",
  };

  try {
    console.log("Sending email with data:", data);
    const res = await axios.post('hhttp://localhost:8000/api/emailGenerator/send_email/', data, {
      headers: {
        "Content-Type": "application/json"
      }
    });
    return res.data; 
  } catch (error) {
    console.error("Error sending email:", error);
    throw error; 
  }
}

export default {getCompanies,sendEmail};
;
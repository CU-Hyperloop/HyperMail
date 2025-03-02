import axios from 'axios';
const BASE_URL = import.meta.env.VITE_API_URL;

export async function getCompanies(params = {}) {

  console.log(params)

  const data = '{“industry”:“Technology”,“size”:“Medium”,“sector”:“Software”,“location”:“California”,“vibe”:“Professional”}'

  const res = await fetch('http://localhost:8000/api/emailGenerator/generate/', {
    method: 'POST',
    headers: {
      "Content-Type": "application/json"
    },
    body: data
  });


    console.log(res);

    return res
}

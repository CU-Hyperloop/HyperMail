import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL;

export async function getCompanies(params = {}) {

  console.log(params)

  const response = await axios.post('http://localhost:8000/api/emailGenerator/generate/', params);


    console.log(response.data);

    return response.data;
}

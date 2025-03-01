import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';
import {BrowserRouter as Router, Route, Routes,  } from 'react-router';


import Home from './pages/Home';
import EmailGenerator from './pages/EmailGenerator';

export default function App() {
  return (
  <MantineProvider>

    <Router>
      <Routes>
        <Route path="/" element={<Home/>}/>
        <Route path="/generate" element={<EmailGenerator/>}/>
      </Routes>
    </Router>
    
  </MantineProvider>
  
);
}

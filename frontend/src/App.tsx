import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';
import {BrowserRouter as Router, Route, Routes,  } from 'react-router';


import Home from './pages/Home';
import EmailGenerator from './pages/EmailGenerator';
import DraftMail from './pages/DraftMail';
import Test from './pages/test';
import EmailDash from './pages/EmailDash';

export default function App() {
  return (
  <MantineProvider>

    <Router>
      <Routes>
        <Route path="/" element={<Home/>}/>
        <Route path="/generate" element={<EmailGenerator/>}/>
        <Route path="/draft" element={<DraftMail/>}/>
        <Route path="/test" element={<Test/>}/>
        <Route path="/dashboard" element={<EmailDash/>}/>
      </Routes>
    </Router>
  </MantineProvider>
  
);
}

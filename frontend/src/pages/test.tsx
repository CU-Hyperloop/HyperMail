import { Container, Card, Textarea, Button, TextInput, Loader } from "@mantine/core";
import { useNavigate } from 'react-router';
import { useState, useEffect, useRef } from 'react';
import { generateEmail } from '../services/emailServices';

export default function EmailFeedback() {
    const [companyName, setCompanyName] = useState("");
    const [emailContent, setEmailContent] = useState(
      "This is a placeholder for the generated email. Generate an email by entering a company name above."
    );
    const [feedback, setFeedback] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
  
    const handleGenerateEmail = async () => {
      if (!companyName) {
        setError("Please enter a company name");
        return;
      }
      
      setIsLoading(true);
      setError(null);
      
      try {
        const generatedEmail = await generateEmail(companyName);
        setEmailContent(generatedEmail);
      } catch (err: any) {
        setError(err.message || "Failed to generate email");
      } finally {
        setIsLoading(false);
      }
    };
  
    const handleFeedbackSubmit = () => {
      console.log("Feedback submitted:", feedback);
      alert("Feedback submitted successfully!");
      setFeedback("");
    };
  
    return (
      <Container className="home-container arcade-theme">
        <h1 className="arcade-title">Email Generator</h1>
        
        <div className="generate-section">
          <TextInput
            label="Company Name"
            placeholder="Enter company name"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            className="company-input"
            required
          />
          
          <Button 
            size="lg" 
            className="generate-button" 
            onClick={handleGenerateEmail}
            loading={isLoading}
            disabled={isLoading || !companyName}
          >
            Generate Email
          </Button>
          
          {error && <div className="error-message">{error}</div>}
        </div>
        
        <h2 className="arcade-subtitle">Generated Email</h2>
        <Card className="email-card shadow-lg">
          {isLoading ? (
            <div className="loader-container">
              <Loader size="lg" />
              <p>Generating email... This may take a minute...</p>
            </div>
          ) : (
            <p className="whitespace-pre-line email-content">{emailContent}</p>
          )}
        </Card>
        
        <h2 className="arcade-subtitle">Provide Feedback</h2>
        <Textarea
          className="feedback-textarea"
          placeholder="Write your feedback here..."
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
        />
        <Button size="lg" className="start-button" onClick={handleFeedbackSubmit}>
          Submit Feedback
        </Button>
      </Container>
    );
  }
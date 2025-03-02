import {
  TextInput,
  Button,
  Container,
  Stack,
  Group,
  Textarea,
  Text,
  Loader,
  Card,
  Tabs,
  Divider,
  Grid,
  Col
} from "@mantine/core";
import { useNavigate } from "react-router";
import { useState, useEffect } from "react";
import generateEmail from "../services/emailServices";
import { useLocation } from "react-router";
import LangGraphVisualizer from "../pages/LangGraphVisualizer";

export default function Dashboard() {
  const location = useLocation();
  const { data } = location.state || {};
  const navigate = useNavigate();

  // Combined state from both components
  const [companyName, setCompanyName] = useState("");
  const [to, setTo] = useState("");
  const [cc, setCc] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [emailContent, setEmailContent] = useState(
    "This is a placeholder for the generated email. Generate an email by entering a company name above."
  );
  const [feedback, setFeedback] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("generate");
  
  // Add new state for the visualization popup
  const [visualizerOpen, setVisualizerOpen] = useState(false);

  const handleCompanyClick = (company: any) => {
    // Set the company name for email generation
    setCompanyName(company.name);
    
    // Also populate the To field with company email or name
    if (company.email) {
      setTo(company.email);
    } else {
      setTo(company.name);
    }
    
    // Optionally, set any other fields you want to pre-populate
    // For example, you might want to set a default subject
    setSubject(`Partnership Opportunity with CU Hyperloop: ${company.name}`);
  };

  const handleGenerateEmail = async () => {
    if (!companyName) {
      setError("Please enter a company name");
      return;
    }

    // Open the visualization popup before starting the API call
    setVisualizerOpen(true);
    
    setIsLoading(true);
    setError(null);

    try {
      // Wait a moment to let the visualizer initialize before making the actual API call
      // This creates a better user experience as they can see the workflow starting
      setTimeout(async () => {
        try {
          const generatedEmail = await generateEmail(companyName);
          setEmailContent(generatedEmail.email);
          // Auto-fill the email body with generated content
          setBody(generatedEmail.email);
        } catch (err: any) {
          setError(err.message || "Failed to generate email");
        } finally {
          setIsLoading(false);
          // Note: We're NOT closing the visualizer here to let it finish its animation
        }
      }, 1000);
    } catch (err: any) {
      setError(err.message || "Failed to generate email");
      setIsLoading(false);
      setVisualizerOpen(false);
    }
  };

  const handleUseEmail = () => {
    // Parse subject from the email content
    const subjectMatch = emailContent.match(/SUBJECT:\s*(.*?)(?:\s*\n|\s*$)/);
    const extractedSubject = subjectMatch ? subjectMatch[1].trim() : "";
    
    // Parse recipient from the greeting line 
    const recipientMatch = emailContent.match(/Hello\s+(.*?)(?:,|\s*\n)/);
    const extractedRecipient = recipientMatch ? recipientMatch[1].trim() : "";
    
    // Set the extracted values
    if (extractedSubject) setSubject(extractedSubject);
    if (extractedRecipient) setTo(extractedRecipient);
    
    // Set body - remove the SUBJECT line if present
    const bodyContent = emailContent.replace(/SUBJECT:\s*.*?\n/, '').trim();
    setBody(bodyContent);
    
    // Switch to compose tab
    setActiveTab("compose");
  };

  const handleFeedbackSubmit = () => {
    console.log("Feedback submitted:", feedback);
    alert("Feedback submitted successfully!");
    setFeedback("");
  };

  const handleSendEmail = () => {
    // Logic to send email would go here
    console.log("Email sent with:", { to, cc, subject, body });
    alert("Email sent successfully!");
  };

  const handleCloseVisualizer = () => {
    setVisualizerOpen(false);
  };

  return (
    <Container>
      <h1 className="arcade-title">Email Command Center</h1>

      {/* Visualization popup */}
      <LangGraphVisualizer 
        opened={visualizerOpen} 
        onClose={handleCloseVisualizer} 
        companyName={companyName} 
      />

      <Grid>
        <Grid.Col span={{ base: 12, md: 4 }}>
          <div className="arcade-panel company-list">
            <Text className="arcade-font" size="lg">
              Companies
            </Text>
            {data && data.length > 0 ? (
              data.map((company: any, index: number) => (
                <button
                  key={index}
                  className="company-item"
                  onClick={() => handleCompanyClick(company)}
                >
                  <Text weight={600} size="lg">
                    {company.name}
                  </Text>
                  <Text size="sm">
                    <strong>Email:</strong> {company.email}
                  </Text>
                  <Text size="sm">
                    <strong>Size:</strong> {company.size}
                  </Text>
                  <Text size="sm">
                    <strong>Location:</strong> {company.location}
                  </Text>
                  <Text size="sm">
                    <strong>Industry:</strong> {company.industry}
                  </Text>
                </button>
              ))
            ) : (
              <Text color="dimmed" align="center" mt="md">
                No companies available
              </Text>
            )}
          </div>
        </Grid.Col>

        <Grid.Col span={{ base: 12, md: 8 }}>
          <div className="arcade-panel">
            <Tabs value={activeTab} onChange={setActiveTab}>
              <Tabs.List>
                <Tabs.Tab value="compose">Compose Email</Tabs.Tab>
                <Tabs.Tab value="generate">Generate Content</Tabs.Tab>
              </Tabs.List>

              <Tabs.Panel value="generate" pt="md">
                <Stack spacing="md">
                  <TextInput
                    label="Company Name"
                    placeholder="Enter company name"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    required
                  />

                  <Button
                    onClick={handleGenerateEmail}
                    loading={isLoading}
                    disabled={isLoading || !companyName}
                  >
                    Generate Email
                  </Button>

                  {error && (
                    <Text color="red" size="sm">
                      {error}
                    </Text>
                  )}

                  <Text className="arcade-font" size="lg">
                    Generated Email:
                  </Text>

                  <Card shadow="sm" padding="md">
                    {isLoading ? (
                      <div className="loader-container">
                        <Loader size="md" />
                        <Text mt="md">
                          Generating email... This may take a minute...
                        </Text>
                      </div>
                    ) : (
                      <div className="email-content">{emailContent}</div>
                    )}
                  </Card>

                  <Group position="right">
                    <Button
                      onClick={handleUseEmail}
                    >
                      Use This Email
                    </Button>
                  </Group>

                  <Divider my="sm" />

                  <Text className="arcade-font" size="lg">
                    Provide Feedback:
                  </Text>

                  <Textarea
                    placeholder="Write your feedback here..."
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    minRows={4}
                  />

                  <Group position="right">
                    <Button
                      onClick={handleFeedbackSubmit}
                      disabled={!feedback.trim()}
                    >
                      Submit Feedback
                    </Button>
                  </Group>
                </Stack>
              </Tabs.Panel>

              <Tabs.Panel value="compose" pt="md">
                <Stack spacing="md">
                  <Group>
                    <Text style={{ width: "60px" }}>To: </Text>
                    <TextInput
                      placeholder="Recipients"
                      style={{ flex: 1 }}
                      value={to}
                      onChange={(e) => setTo(e.target.value)}
                    />
                  </Group>

                  <Group>
                    <Text style={{ width: "60px" }}>Cc: </Text>
                    <TextInput
                      placeholder="Carbon copy"
                      style={{ flex: 1 }}
                      value={cc}
                      onChange={(e) => setCc(e.target.value)}
                    />
                  </Group>

                  <Group>
                    <Text style={{ width: "60px" }}>Subject: </Text>
                    <TextInput
                      placeholder="Subject line"
                      style={{ flex: 1 }}
                      value={subject}
                      onChange={(e) => setSubject(e.target.value)}
                    />
                  </Group>

                  <Text>Body:</Text>
                  <Textarea
                    placeholder="Email body"
                    autosize
                    minRows={12}
                    value={body}
                    onChange={(e) => setBody(e.target.value)}
                  />

                  <Group position="right">
                    <Button variant="outline" onClick={() => navigate('/')}>
                      Cancel
                    </Button>
                    <Button onClick={handleSendEmail}>Send</Button>
                  </Group>
                </Stack>
              </Tabs.Panel>
            </Tabs>
          </div>
        </Grid.Col>
      </Grid>
    </Container>
  );
}
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
import { useState, useEffect, useRef } from "react";
import generateEmail from "../services/emailServices";
import { useLocation } from "react-router";

export default function Dashboard() {

    const location = useLocation();
    const { data } = location.state || {};

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
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("generate");

  const handleGenerateEmail = async () => {
    if (!companyName) {
      setError("Please enter a company name");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const generatedEmail = await generateEmail(companyName);
      setEmailContent(generatedEmail.email);
      // Auto-fill the email body with generated content
      setBody(generatedEmail.email);
    } catch (err) {
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

  const handleSendEmail = () => {
    // Logic to send email would go here
    
    console.log("Email sent with:", { to, cc, subject, body });
    alert("Email sent successfully!");
  };

  return (
    <>

    <Container
      size="md"
      style={{
        padding: "1.5rem",
        borderRadius: "8px",
        minHeight: "100vh",
      }}
    >
      <h1
        style={{
          textAlign: "center",
          marginBottom: "1.5rem",
          fontFamily: '"Press Start 2P", cursive', // Arcade-style font
        //   color: "#333",
        }}
      >
        Email Composer & Generator
      </h1>

      <Grid>

      <Grid.Col gutter="lg" span={4}>
        <div
          style={{
            padding: "1rem",
            borderRadius: "8px",
            border: "1px solid #ddd",
            backgroundColor: "#f9fafb",
            height: "100vh",
          }}
        >
          <Text weight={600} size="lg" style={{ marginBottom: "0.5rem" }}>
            Companies
          </Text>
          {data &&
            data.map((company, index) => (
              <Button
                key={index}
                fullWidth
                variant="light"
                style={{
                  padding: "1rem",
                  borderRadius: "8px",
                  border: "1px solid #ddd",
                  backgroundColor: "#f9fafb",
                  marginBottom: "1rem",
                  textAlign: "left",
                }}
                onClick={() => setCompanyName(company.name)}
              >
                <Text weight={600} size="lg">{company.name}</Text>
                <Text size="sm"><strong>Email:</strong> {company.email}</Text>
                <Text size="sm"><strong>Size:</strong> {company.size}</Text>
                <Text size="sm"><strong>Location:</strong> {company.location}</Text>
                <Text size="sm"><strong>Industry:</strong> {company.industry}</Text>
              </Button>
            ))}
        </div>
    </Grid.Col>

        <Grid.Col span={8}>

        <Tabs value={activeTab} onChange={setActiveTab}>
        <Tabs.List>
          <Tabs.Tab value="compose">Compose Email</Tabs.Tab>
          <Tabs.Tab value="generate">Generate Content</Tabs.Tab>
        </Tabs.List>


        <Tabs.Panel value="generate" pt="md">
          <div style={{ marginBottom: "1.5rem" }}>
            <TextInput
              label="Company Name"
              placeholder="Enter company name"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              required
              style={{ marginBottom: "1rem" }}
            />

            <Button
              size="md"
              onClick={handleGenerateEmail}
              loading={isLoading}
              disabled={isLoading || !companyName}
              style={{ marginBottom: "1rem" }}
            >
              Generate Email
            </Button>

            {error && (
              <Text color="red" size="sm" style={{ marginTop: "0.5rem" }}>
                {error}
              </Text>
            )}
          </div>

          <Text weight={600} size="lg" style={{ marginBottom: "0.5rem" }}>
            Generated Email:
          </Text>

          <Card
            shadow="sm"
            p="lg"
            style={{
              border: "1px solid #ddd",
              borderRadius: "8px",
              marginBottom: "1rem",
            }}
          >
            {isLoading ? (
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  padding: "2rem",
                }}
              >
                <Loader size="lg" />
                <Text style={{ marginTop: "1rem" }}>
                  Generating email... This may take a minute...
                </Text>
              </div>
            ) : (
              <div style={{ whiteSpace: "pre-line" }}>{emailContent}</div>
            )}
          </Card>

          <Group position="right" pd="md" m="md">
            <Button
              color="blue"
              size="lg"
              onClick={() => {
                setBody(emailContent);
                setActiveTab("compose");
              }}
            >
              Use This Email
            </Button>
          </Group>
          <Divider/>
          <Text weight={600} size="lg" style={{ marginBottom: "0.5rem" }}>
            Provide Feedback:
          </Text>

          <Textarea
            placeholder="Write your feedback here..."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            minRows={6}
            style={{ marginBottom: "1rem" }}
          />

          <Button
            onClick={handleFeedbackSubmit}
            disabled={!feedback.trim()}
          >
            Submit Feedback
          </Button>
        </Tabs.Panel>
        <Tabs.Panel value="compose" pt="md">
          <Stack spacing="md" style={{ width: "100%" }}>
            <Group position="apart">
              <Text style={{ width: "60px" }}>To: </Text>
              <TextInput
                placeholder="Recipients"
                style={{ flex: 1 }}
                value={to}
                onChange={(e) => setTo(e.target.value)}
              />
            </Group>

            <Group position="apart">
              <Text style={{ width: "60px" }}>Cc: </Text>
              <TextInput
                placeholder="Carbon copy"
                style={{ flex: 1 }}
                value={cc}
                onChange={(e) => setCc(e.target.value)}
              />
            </Group>

            <Group position="apart">
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
              minRows={15}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              style={{ border: "1px solid #ddd" }}
            />

            <Group position="right">
              <Button variant="outline">
                Cancel
              </Button>
              <Button onClick={handleSendEmail}>
                Send
              </Button>
            </Group>
          </Stack>
        </Tabs.Panel>

        
      </Tabs>
         

         </Grid.Col>
      </Grid>

      
    </Container>
    </>
  );


}

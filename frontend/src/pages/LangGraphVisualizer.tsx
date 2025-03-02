import { useState, useEffect } from 'react';
import { Modal, Text, Progress, Stack, Badge, Group, Box, Timeline } from '@mantine/core';

// Define types for agent states
type AgentStatus = 'waiting' | 'running' | 'completed' | 'error';

interface Agent {
  id: string;
  name: string;
  description: string;
  status: AgentStatus;
  progress: number;
  messages: string[];
}

interface LangGraphVisualizerProps {
  opened: boolean;
  onClose: () => void;
  companyName: string;
}

export default function LangGraphVisualizer({ opened, onClose, companyName }: LangGraphVisualizerProps) {
  // State for simulating agents
  const [agents, setAgents] = useState<Agent[]>([]);
  const [activeAgentIndex, setActiveAgentIndex] = useState(0);
  const [overallProgress, setOverallProgress] = useState(0);

  // Define the workflow steps/agents
  useEffect(() => {
    if (opened) {
      // Reset state when opened
      const initialAgents: Agent[] = [
        {
          id: 'company-researcher',
          name: 'Company Researcher',
          description: 'Analyzes company information and industry context',
          status: 'waiting',
          progress: 0,
          messages: []
        },
        {
          id: 'decision-maker-profiler',
          name: 'Decision Maker Profiler',
          description: 'Identifies key decision makers and their preferences',
          status: 'waiting',
          progress: 0,
          messages: []
        },
        {
          id: 'value-proposition-generator',
          name: 'Value Proposition Generator',
          description: 'Creates personalized value propositions',
          status: 'waiting', 
          progress: 0,
          messages: []
        },
        {
          id: 'tone-analyzer',
          name: 'Tone Analyzer',
          description: 'Determines appropriate communication style',
          status: 'waiting',
          progress: 0,
          messages: []
        },
        {
          id: 'email-composer',
          name: 'Email Composer',
          description: 'Drafts the final email with all inputs',
          status: 'waiting',
          progress: 0,
          messages: []
        }
      ];
      setAgents(initialAgents);
      setActiveAgentIndex(0);
      setOverallProgress(0);
      
      // Start the simulation
      simulateWorkflow(initialAgents);
    }
  }, [opened, companyName]);

  // Simulate the workflow process
  const simulateWorkflow = (initialAgents: Agent[]) => {
    const agentMessages = {
      'company-researcher': [
        `Searching for information about "${companyName}"...`,
        `Found company website and social media profiles`,
        `Analyzing recent news and press releases`,
        `Identifying industry trends and competitive landscape`,
        `Compiling company insights and business focus areas`
      ],
      'decision-maker-profiler': [
        `Identifying key decision makers at "${companyName}"`,
        `Analyzing professional backgrounds and communication styles`,
        `Mapping reporting structures and decision authority`,
        `Determining potential interest points for sponsorship`,
        `Profiling complete for target stakeholders`
      ],
      'value-proposition-generator': [
        `Creating customized value propositions for "${companyName}"`,
        `Mapping CU Hyperloop strengths to company priorities`,
        `Developing quantifiable benefit statements`,
        `Aligning proposal with company's strategic objectives`,
        `Value propositions prioritized and refined`
      ],
      'tone-analyzer': [
        `Analyzing optimal communication tone for "${companyName}"`,
        `Evaluating corporate culture and communication style`,
        `Determining formality level and technical depth`,
        `Setting appropriate enthusiasm and assertiveness levels`,
        `Communication approach optimized for recipient preferences`
      ],
      'email-composer': [
        `Structuring email for "${companyName}" with all agent inputs`,
        `Crafting compelling subject line and introduction`,
        `Incorporating value propositions and evidence points`,
        `Adding appropriate call-to-action`,
        `Email draft completed and ready for review`
      ]
    };

    // Process each agent sequentially
    initialAgents.forEach((agent, index) => {
      const startDelay = index * 3000; // Start each agent 3 seconds after the previous one
      const progressInterval = 500; // Update progress every 500ms
      const totalSteps = agentMessages[agent.id as keyof typeof agentMessages].length;
      
      // Start the agent after delay
      setTimeout(() => {
        setActiveAgentIndex(index);
        setAgents(prev => {
          const updated = [...prev];
          updated[index] = {
            ...updated[index],
            status: 'running',
            progress: 0
          };
          return updated;
        });
        
        // Process each message with progress updates
        agentMessages[agent.id as keyof typeof agentMessages].forEach((message, messageIndex) => {
          setTimeout(() => {
            setAgents(prev => {
              const updated = [...prev];
              const newProgress = Math.round(((messageIndex + 1) / totalSteps) * 100);
              
              updated[index] = {
                ...updated[index],
                progress: newProgress,
                messages: [...updated[index].messages, message]
              };
              
              // Mark as complete if this is the last message
              if (messageIndex === totalSteps - 1) {
                updated[index].status = 'completed';
              }
              
              return updated;
            });
            
            // Update overall progress
            setOverallProgress(prev => {
              const agentWeight = 100 / initialAgents.length;
              const agentContribution = agentWeight * (index + (messageIndex + 1) / totalSteps);
              return Math.min(Math.round(agentContribution), 100);
            });
          }, messageIndex * 1000);
        });
      }, startDelay);
    });
  };

  // Get color based on agent status
  const getStatusColor = (status: AgentStatus) => {
    switch (status) {
      case 'waiting': return 'gray';
      case 'running': return 'blue';
      case 'completed': return 'green';
      case 'error': return 'red';
      default: return 'gray';
    }
  };

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={
        <Group>
          <Text className="arcade-font" size="lg">AI Workflow for {companyName}</Text>
          <Badge color="blue">{overallProgress}% Complete</Badge>
        </Group>
      }
      size="lg"
      centered
      padding="xl"
      styles={{
        header: {
          marginBottom: '1.5rem',
        },
        body: {
          padding: '0 1rem',
        },
        title: {
          width: '100%',
        }
      }}
    >
      <Progress value={overallProgress} mb="md" size="lg" color="blue" />
      
      <Timeline active={activeAgentIndex} bulletSize={24} lineWidth={2}>
        {agents.map((agent, index) => (
          <Timeline.Item
            key={agent.id}
            bullet={
              agent.status === 'completed' ? '✓' : 
              agent.status === 'running' ? '⚙️' : 
              agent.status === 'error' ? '✗' : 
              index + 1
            }
            title={
              <Group>
                <Text weight={700}>{agent.name}</Text>
                <Badge color={getStatusColor(agent.status)}>
                  {agent.status === 'waiting' ? 'Waiting' : 
                   agent.status === 'running' ? 'Running' : 
                   agent.status === 'completed' ? 'Completed' : 
                   'Error'}
                </Badge>
              </Group>
            }
          >
            <Text color="dimmed" size="sm">{agent.description}</Text>
            
            {agent.status !== 'waiting' && (
              <Box mt="xs">
                <Progress 
                  value={agent.progress} 
                  size="sm" 
                  color={getStatusColor(agent.status)} 
                  mt="xs" 
                  mb="xs"
                />
                
                <Stack spacing="xs" mt="sm">
                  {agent.messages.map((message, i) => (
                    <Text key={i} size="sm" style={{ opacity: 1 - (agent.messages.length - i) * 0.15 }}>
                      {message}
                    </Text>
                  ))}
                </Stack>
              </Box>
            )}
          </Timeline.Item>
        ))}
      </Timeline>
    </Modal>
  );
}
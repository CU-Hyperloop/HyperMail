import { useState, useEffect, useRef } from 'react';
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
  estimatedDuration: number; // Time in seconds this agent typically takes
  complexityFactor: number; // Factor between 0.8-1.5 to vary timing
}

interface LangGraphVisualizerProps {
  opened: boolean;
  onClose: () => void;
  companyName: string;
  isGenerating: boolean; // Track if the API is still generating
}

export default function LangGraphVisualizer({ opened, onClose, companyName, isGenerating }: LangGraphVisualizerProps) {
  // State for simulating agents
  const [agents, setAgents] = useState<Agent[]>([]);
  const [activeAgentIndex, setActiveAgentIndex] = useState(0);
  const [overallProgress, setOverallProgress] = useState(0);
  const [simulationStarted, setSimulationStarted] = useState(false);
  const simulationRef = useRef<{intervals: NodeJS.Timeout[]}>(
    { intervals: [] }
  );

  // Reset simulation when component unmounts
  useEffect(() => {
    return () => {
      simulationRef.current.intervals.forEach(interval => clearInterval(interval));
    };
  }, []);

  // Define the workflow steps/agents
  useEffect(() => {
    if (opened && !simulationStarted) {
      // Reset state when opened
      const initialAgents: Agent[] = [
        {
          id: 'company-researcher',
          name: 'Company Researcher',
          description: 'Analyzes company information and industry context',
          status: 'waiting',
          progress: 0,
          messages: [],
          estimatedDuration: 20, // In seconds
          complexityFactor: Math.random() * 0.4 + 0.8 // Between 0.8 and 1.2
        },
        {
          id: 'decision-maker-profiler',
          name: 'Decision Maker Profiler',
          description: 'Identifies key decision makers and their preferences',
          status: 'waiting',
          progress: 0,
          messages: [],
          estimatedDuration: 25,
          complexityFactor: Math.random() * 0.4 + 0.8
        },
        {
          id: 'value-proposition-generator',
          name: 'Value Proposition Generator',
          description: 'Creates personalized value propositions',
          status: 'waiting', 
          progress: 0,
          messages: [],
          estimatedDuration: 18,
          complexityFactor: Math.random() * 0.4 + 0.8
        },
        {
          id: 'tone-analyzer',
          name: 'Tone Analyzer',
          description: 'Determines appropriate communication style',
          status: 'waiting',
          progress: 0,
          messages: [],
          estimatedDuration: 15,
          complexityFactor: Math.random() * 0.4 + 0.8
        },
        {
          id: 'email-composer',
          name: 'Email Composer',
          description: 'Drafts the final email with all inputs',
          status: 'waiting',
          progress: 0,
          messages: [],
          estimatedDuration: 22,
          complexityFactor: Math.random() * 0.4 + 0.8
        }
      ];
      setAgents(initialAgents);
      setActiveAgentIndex(0);
      setOverallProgress(0);
      setSimulationStarted(true);
      
      // Start the simulation
      simulateWorkflow(initialAgents);
    }
  }, [opened, companyName, simulationStarted]);

  // Reset simulation state when modal is closed
  useEffect(() => {
    if (!opened) {
      simulationRef.current.intervals.forEach(interval => clearInterval(interval));
      simulationRef.current.intervals = [];
      setSimulationStarted(false);
    }
  }, [opened]);

  // Update the simulation when isGenerating changes
  useEffect(() => {
    if (!isGenerating && simulationStarted) {
      // If API is done but simulation isn't, speed up completion
      completeSimulation();
    }
  }, [isGenerating, simulationStarted]);

  // Speed up and complete the simulation
  const completeSimulation = () => {
    // Clear all existing intervals
    simulationRef.current.intervals.forEach(interval => clearInterval(interval));
    simulationRef.current.intervals = [];
    
    // Complete any running agent
    setAgents(prev => {
      const updated = [...prev];
      for (let i = 0; i < updated.length; i++) {
        if (updated[i].status === 'running') {
          updated[i].status = 'completed';
          updated[i].progress = 100;
        }
      }
      return updated;
    });
    
    // Complete all remaining agents quickly
    const remainingAgents = agents.filter(agent => agent.status === 'waiting');
    
    if (remainingAgents.length > 0) {
      // Speed up remaining agents (complete all within 2-3 seconds)
      const speedUpCompletion = setInterval(() => {
        setAgents(prev => {
          const updated = [...prev];
          let allDone = true;
          
          for (let i = 0; i < updated.length; i++) {
            if (updated[i].status === 'waiting') {
              setActiveAgentIndex(i);
              updated[i].status = 'completed';
              updated[i].progress = 100;
              allDone = false;
              break;
            }
          }
          
          if (allDone) {
            clearInterval(speedUpCompletion);
            setOverallProgress(100);
          }
          
          return updated;
        });
      }, 800);
      
      simulationRef.current.intervals.push(speedUpCompletion);
    }
  };

  // Simulate the workflow process with more realistic timing
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

    // Process agents sequentially with more realistic timing
    let totalProcessingTime = 0;
    
    // Start the first agent immediately
    processAgent(0);
    
    function processAgent(agentIndex: number) {
      if (agentIndex >= initialAgents.length) return;
      
      const agent = initialAgents[agentIndex];
      const agentId = agent.id as keyof typeof agentMessages;
      const messages = agentMessages[agentId];
      
      // Calculate realistic timing based on agent complexity
      const totalAgentTime = agent.estimatedDuration * agent.complexityFactor * 1000; // Convert to ms
      const messageInterval = totalAgentTime / messages.length;
      const progressUpdateInterval = totalAgentTime / 20; // 20 progress updates per agent
      
      // Start the agent
      setActiveAgentIndex(agentIndex);
      setAgents(prev => {
        const updated = [...prev];
        updated[agentIndex] = {
          ...updated[agentIndex],
          status: 'running',
          progress: 0
        };
        return updated;
      });
      
      // Schedule message updates
      messages.forEach((message, messageIndex) => {
        const randomVariation = Math.random() * 0.4 + 0.8; // 80% to 120% of base timing
        const messageTime = messageInterval * randomVariation * (messageIndex + 1);
        
        const timeout = setTimeout(() => {
          setAgents(prev => {
            const updated = [...prev];
            updated[agentIndex].messages = [...updated[agentIndex].messages, message];
            return updated;
          });
        }, messageTime);
        
        simulationRef.current.intervals.push(timeout);
      });
      
      // Schedule progress updates with small variations to seem more natural
      let progressCounter = 0;
      const progressInterval = setInterval(() => {
        progressCounter++;
        
        if (progressCounter >= 20) {
          clearInterval(progressInterval);
          
          // Mark as complete and start next agent
          setAgents(prev => {
            const updated = [...prev];
            updated[agentIndex] = {
              ...updated[agentIndex],
              status: 'completed',
              progress: 100
            };
            return updated;
          });
          
          // Update overall progress
          const overallIncrement = 100 / initialAgents.length;
          setOverallProgress(prev => 
            Math.min(Math.round(prev + overallIncrement), 
            agentIndex === initialAgents.length - 1 ? 100 : 99)
          );
          
          // Start next agent with a small delay
          if (agentIndex < initialAgents.length - 1) {
            const nextAgentDelay = Math.random() * 1000 + 500; // 500-1500ms delay
            const nextAgentTimeout = setTimeout(() => {
              processAgent(agentIndex + 1);
            }, nextAgentDelay);
            
            simulationRef.current.intervals.push(nextAgentTimeout);
          }
        } else {
          // Update progress with small variations
          const newProgress = Math.round((progressCounter / 20) * 100);
          setAgents(prev => {
            const updated = [...prev];
            updated[agentIndex].progress = newProgress;
            return updated;
          });
          
          // Update overall progress incrementally
          const overallIncrement = (100 / initialAgents.length) / 20;
          setOverallProgress(prev => 
            Math.min(Math.round(prev + overallIncrement), 
            agentIndex === initialAgents.length - 1 && progressCounter >= 19 ? 100 : 99)
          );
        }
      }, progressUpdateInterval);
      
      simulationRef.current.intervals.push(progressInterval);
    }
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
                {agent.status === 'running' && (
                  <Text size="xs" color="dimmed">{agent.progress}%</Text>
                )}
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
                  animated={agent.status === 'running'}
                />
                
                <Stack spacing="xs" mt="sm">
                  {agent.messages.map((message, i) => (
                    <Text 
                      key={i} 
                      size="sm" 
                      className="agent-message"
                      style={{ 
                        opacity: 1 - (agent.messages.length - i) * 0.15,
                        animation: `fadeInMessage ${0.3 + i * 0.1}s ease-out forwards`
                      }}
                    >
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
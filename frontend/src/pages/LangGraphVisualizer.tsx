import { useState, useEffect, useRef } from 'react';
import { Modal, Text, Progress, Stack, Badge, Group, Box, Timeline, ActionIcon, Tooltip } from '@mantine/core';

// Define types for agent states
type AgentStatus = 'waiting' | 'running' | 'completed' | 'error';
type VisualizerMode = 'professional' | 'arcade';

interface Agent {
  id: string;
  name: string;
  description: string;
  status: AgentStatus;
  progress: number;
  messages: string[];
  estimatedDuration: number; // Time in seconds this agent typically takes
  complexityFactor: number; // Factor between 0.8-1.5 to vary timing
  ghostColor: string; // Color for the ghost in arcade mode
}

interface LangGraphVisualizerProps {
  opened: boolean;
  onClose: () => void;
  companyName: string;
  isGenerating: boolean; // Track if the API is still generating
}

// Simple icon components to replace tabler-icons
const SimpleIcons = {
  ChartBar: () => (
    <div style={{ width: '16px', height: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
      <div style={{ width: '4px', height: '6px', backgroundColor: 'currentColor', marginLeft: '2px' }} />
      <div style={{ width: '4px', height: '10px', backgroundColor: 'currentColor', marginLeft: '6px' }} />
      <div style={{ width: '4px', height: '14px', backgroundColor: 'currentColor', marginLeft: '10px' }} />
    </div>
  ),
  Ghost: () => (
    <div style={{ width: '16px', height: '16px', position: 'relative' }}>
      <div style={{ 
        width: '14px', 
        height: '14px', 
        borderRadius: '7px 7px 0 0',
        backgroundColor: 'currentColor',
        position: 'relative'
      }}>
        <div style={{ 
          position: 'absolute', 
          bottom: '-2px', 
          width: '100%', 
          height: '2px',
          backgroundColor: 'currentColor',
          clipPath: 'polygon(0% 0%, 33% 100%, 66% 0%, 100% 100%)'
        }} />
      </div>
    </div>
  ),
  Clock: () => (
    <div style={{ width: '16px', height: '16px', position: 'relative' }}>
      <div style={{ 
        width: '14px', 
        height: '14px', 
        borderRadius: '50%', 
        border: '1px solid currentColor',
        position: 'relative'
      }}>
        <div style={{ 
          position: 'absolute', 
          top: '6px', 
          left: '6px', 
          width: '5px', 
          height: '1px', 
          backgroundColor: 'currentColor',
          transform: 'rotate(45deg)',
          transformOrigin: '0 0'
        }} />
      </div>
    </div>
  )
};

export default function LangGraphVisualizer({ opened, onClose, companyName, isGenerating }: LangGraphVisualizerProps) {
  // State for simulating agents
  const [agents, setAgents] = useState<Agent[]>([]);
  const [activeAgentIndex, setActiveAgentIndex] = useState(0);
  const [overallProgress, setOverallProgress] = useState(0);
  const [simulationStarted, setSimulationStarted] = useState(false);
  const [visualizerMode, setVisualizerMode] = useState<VisualizerMode>('professional');
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState<number>(0);
  const [elapsedTime, setElapsedTime] = useState<number>(0);
  
  const simulationRef = useRef<{
    intervals: NodeJS.Timeout[],
    startTime: number,
    totalEstimatedTime: number
  }>({
    intervals: [],
    startTime: 0,
    totalEstimatedTime: 0
  });

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
          complexityFactor: Math.random() * 0.4 + 0.8, // Between 0.8 and 1.2
          ghostColor: '#FF0000' // Blinky (red)
        },
        {
          id: 'decision-maker-profiler',
          name: 'Decision Maker Profiler',
          description: 'Identifies key decision makers and their preferences',
          status: 'waiting',
          progress: 0,
          messages: [],
          estimatedDuration: 25,
          complexityFactor: Math.random() * 0.4 + 0.8,
          ghostColor: '#FFB8FF' // Pinky (pink)
        },
        {
          id: 'value-proposition-generator',
          name: 'Value Proposition Generator',
          description: 'Creates personalized value propositions',
          status: 'waiting', 
          progress: 0,
          messages: [],
          estimatedDuration: 18,
          complexityFactor: Math.random() * 0.4 + 0.8,
          ghostColor: '#00FFFF' // Inky (cyan)
        },
        {
          id: 'tone-analyzer',
          name: 'Tone Analyzer',
          description: 'Determines appropriate communication style',
          status: 'waiting',
          progress: 0,
          messages: [],
          estimatedDuration: 15,
          complexityFactor: Math.random() * 0.4 + 0.8,
          ghostColor: '#FFB852' // Clyde (orange)
        },
        {
          id: 'email-composer',
          name: 'Email Composer',
          description: 'Drafts the final email with all inputs',
          status: 'waiting',
          progress: 0,
          messages: [],
          estimatedDuration: 22,
          complexityFactor: Math.random() * 0.4 + 0.8,
          ghostColor: '#7D26CD' // Purple (for variety)
        }
      ];
      
      // Calculate total estimated time
      const totalTime = initialAgents.reduce((sum, agent) => {
        return sum + (agent.estimatedDuration * agent.complexityFactor);
      }, 0);
      
      simulationRef.current.totalEstimatedTime = totalTime;
      simulationRef.current.startTime = Date.now();
      
      setEstimatedTimeRemaining(Math.round(totalTime));
      setAgents(initialAgents);
      setActiveAgentIndex(0);
      setOverallProgress(0);
      setElapsedTime(0);
      setSimulationStarted(true);
      
      // Start the simulation
      simulateWorkflow(initialAgents);
      
      // Start a timer to update elapsed time and remaining time
      const timerInterval = setInterval(() => {
        const now = Date.now();
        const elapsed = (now - simulationRef.current.startTime) / 1000;
        setElapsedTime(Math.round(elapsed));
        
        // Calculate remaining time based on progress vs estimated total time
        const progressRatio = overallProgress / 100;
        const totalTimeEstimate = simulationRef.current.totalEstimatedTime;
        const estimatedTotal = elapsed / progressRatio;
        const remaining = Math.max(0, Math.round(estimatedTotal - elapsed));
        
        setEstimatedTimeRemaining(remaining);
      }, 1000);
      
      simulationRef.current.intervals.push(timerInterval);
    }
  }, [opened, companyName, simulationStarted, overallProgress]);

  // Reset simulation state when modal is closed
  useEffect(() => {
    if (!opened) {
      simulationRef.current.intervals.forEach(interval => clearInterval(interval));
      simulationRef.current.intervals = [];
      setSimulationStarted(false);
      setElapsedTime(0);
      setEstimatedTimeRemaining(0);
    }
  }, [opened]);

  // Update the simulation when isGenerating changes
  useEffect(() => {
    if (!isGenerating && simulationStarted) {
      // If API is done but simulation isn't, speed up completion
      completeSimulation();
    }
  }, [isGenerating, simulationStarted]);

  // Format time in MM:SS
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

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
            setEstimatedTimeRemaining(0);
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

  // Render the Ghost Mode visualization
  const renderGhostVisualizer = () => {
    return (
      <div className="ghost-visualizer-container">
        <div className="ghost-maze-track">
          {/* Pacman as overall progress indicator */}
          <div 
            className="pacman-character" 
            style={{ 
              left: `${overallProgress}%`,
              transform: 'translate(-50%, -50%) scale(0.8)'
            }}
          >
            <div className="pacman-eye"></div>
            <div className="pacman-mouth"></div>
          </div>
          
          {/* Progress dots */}
          {Array.from({ length: 20 }).map((_, i) => (
            <div 
              key={i} 
              className={`pacman-pellet ${overallProgress >= (i+1) * 5 ? 'eaten' : ''}`}
              style={{ left: `${(i+1) * 5}%` }}
            ></div>
          ))}
          
          {/* Ghost agents */}
          <div className="ghost-agents-container">
            {agents.map((agent, index) => (
              <div 
                key={agent.id} 
                className={`ghost-agent ${agent.status}`}
                style={{ 
                  left: `${agent.progress}%`,
                  backgroundColor: agent.ghostColor,
                  top: `${150 + index * 70}px`,
                  zIndex: activeAgentIndex === index ? 10 : 5,
                  transform: `scale(${activeAgentIndex === index ? 1.2 : 1})`,
                  opacity: agent.status === 'waiting' ? 0.5 : 1
                }}
              >
                <div className="ghost-eyes">
                  <div className="eye"></div>
                  <div className="eye"></div>
                </div>
                <div className="ghost-skirt"></div>
                
                {/* Agent name */}
                <div className="ghost-name">
                  {agent.name}
                </div>
                
                {/* Agent progress */}
                <div className="ghost-progress">
                  <Progress 
                    value={agent.progress} 
                    color={getStatusColor(agent.status)} 
                    size="sm" 
                    style={{ width: '100px' }}
                    animated={agent.status === 'running'}
                  />
                </div>
                
                {/* Current message */}
                {agent.status === 'running' && agent.messages.length > 0 && (
                  <div className="ghost-message">
                    {agent.messages[agent.messages.length - 1]}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
        
        {/* Status information */}
        <div className="ghost-status-info">
          <div className="status-item">
            <SimpleIcons.Clock />
            <Text>Elapsed: {formatTime(elapsedTime)}</Text>
          </div>
          <div className="status-item">
            <Badge size="lg" color="blue">{overallProgress}% Complete</Badge>
          </div>
        </div>
        
        {/* Current Agent Information */}
        {activeAgentIndex < agents.length && (
          <div className="active-ghost-info">
            <Text className="arcade-font" size="lg">
              {agents[activeAgentIndex].name} is hunting for data...
            </Text>
            <div className="active-ghost-messages">
              {agents[activeAgentIndex].messages.slice(-3).map((message, i) => (
                <Text 
                  key={i} 
                  className="agent-message"
                  style={{ animation: `fadeInMessage ${0.3 + i * 0.1}s ease-out forwards` }}
                >
                  {message}
                </Text>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  // Render the Professional Timeline visualization
  const renderTimelineVisualizer = () => {
    return (
      <>
        <Progress value={overallProgress} mb="md" size="lg" color="blue" />
        
        <Group mb="md" position="apart">
          <Text size="md" color="dimmed">
            <span style={{ marginRight: '5px', verticalAlign: 'middle', display: 'inline-block' }}>
              <SimpleIcons.Clock />
            </span>
            Elapsed: {formatTime(elapsedTime)}
          </Text>
          <Text size="md" color="dimmed">
            <span style={{ marginRight: '5px', verticalAlign: 'middle', display: 'inline-block' }}>
              <SimpleIcons.Clock />
            </span>
            Estimated remaining: {formatTime(estimatedTimeRemaining)}
          </Text>
        </Group>
        
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
      </>
    );
  };

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={
        <Group style={{width: '100%'}} position="apart">
          <Text className="arcade-font" size="lg">AI Workflow for {companyName}</Text>
          <Group>
            <Badge color="blue">{overallProgress}% Complete</Badge>
            <Tooltip label={visualizerMode === 'professional' ? 'Switch to Arcade Mode' : 'Switch to Professional Mode'}>
              <ActionIcon 
                variant="filled" 
                color={visualizerMode === 'professional' ? 'blue' : 'yellow'}
                onClick={() => setVisualizerMode(visualizerMode === 'professional' ? 'arcade' : 'professional')}
              >
                {visualizerMode === 'professional' ? <SimpleIcons.Ghost /> : <SimpleIcons.ChartBar />}
              </ActionIcon>
            </Tooltip>
          </Group>
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
      {visualizerMode === 'professional' ? renderTimelineVisualizer() : renderGhostVisualizer()}
    </Modal>
  );
}
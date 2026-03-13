import React, { useState, useEffect, useRef } from 'react';
import { Handle, Position, useReactFlow, useNodesInitialized } from '@xyflow/react';
import { Button } from './ui/button';
import { Paperclip, Send, Settings, Download, X, Loader2, Search, RotateCcw, History, Plus, CheckCircle, AlertCircle, RefreshCw, BotMessageSquare, Atom, FileText, Image, Code } from 'lucide-react';
import Linkify from 'react-linkify';
import { v4 as uuidv4 } from 'uuid';
import dagre from '@dagrejs/dagre';

const AIChatNode = ({ id, data, isConnectable }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [connectedNodes, setConnectedNodes] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [multiGenResponses, setMultiGenResponses] = useState([]);
  const [verificationStatus, setVerificationStatus] = useState(null);
  const [showSearch, setShowSearch] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showMultiGen, setShowMultiGen] = useState(false);
  const [showMultiGenModal, setShowMultiGenModal] = useState(false);
  const [selectedModalities, setSelectedModalities] = useState([]);
  const [generatedNodes, setGeneratedNodes] = useState([]);
  const messagesEndRef = useRef(null);
  const { getEdges, getNodes, addNodes, deleteElements, setNodes } = useReactFlow();
  const nodesInitialized = useNodesInitialized();

  // Initialize chat session - only when user creates a new chat
  // Removed automatic chat creation to prevent default previous chats

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Detect connected nodes
  useEffect(() => {
    const updateConnectedNodes = () => {
      const edges = getEdges();
      const nodes = getNodes();
      
      // Find edges that connect to this AI Chat Node
      const incomingEdges = edges.filter(edge => edge.target === id);
      
      // Get the source nodes
      const connectedNodeIds = incomingEdges.map(edge => edge.source);
      const connectedNodesData = nodes
        .filter(node => connectedNodeIds.includes(node.id))
        .map(node => {
          // Handle YouTube nodes specially - extract videoData
          if (node.type === 'youtubeNode' && node.data.videoData) {
            return {
              id: node.id,
              type: 'youtube',
              data: node.data.videoData
            };
          }
          // Handle other nodes normally
          return {
          id: node.id,
          type: node.type,
          data: node.data
          };
        });
      
      setConnectedNodes(connectedNodesData);
    };

    updateConnectedNodes();
    
    // Update when edges change
    const interval = setInterval(updateConnectedNodes, 1000);
    return () => clearInterval(interval);
  }, [id, getEdges, getNodes]);

  // Grounded Search functionality
  const performGroundedSearch = async (query) => {
    try {
      // Prepare YouTube context from connected nodes
      const youtubeContext = connectedNodes.find(node => node.type === 'youtube')?.data;
      
      const response = await fetch('http://localhost:8001/api/grounded-search/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query, 
          youtube_context: youtubeContext,
          num_results: 5
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        setSearchResults(result.search_results || []);
        return {
          success: true,
          ai_response: result.ai_response,
          citations: result.citations,
          sources: result.sources,
          search_results: result.search_results
        };
      } else {
        throw new Error(result.error || 'Grounded search failed');
      }
    } catch (error) {
      console.error('Grounded search error:', error);
      return {
        success: false,
        error: error.message,
        ai_response: "I encountered an error while performing grounded search. Please try again.",
        citations: [],
        sources: []
      };
    }
  };

  // Multi-Generation functionality
  const generateMultipleResponses = async (prompt) => {
    try {
      const response = await fetch('http://localhost:8001/api/ai/multi-gen', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt, 
          nodes: connectedNodes,
          count: 3 
        })
      });
      const result = await response.json();
      setMultiGenResponses(result.responses || []);
      return result.responses || [];
    } catch (error) {
      console.error('Multi-gen error:', error);
      return [];
    }
  };

  // Cross-check and verification
  const verifyResponse = async (response) => {
    try {
      setVerificationStatus('verifying');
      const verifyResponse = await fetch('http://localhost:8001/api/ai/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          response, 
          context: connectedNodes,
          original_prompt: inputValue 
        })
      });
      const result = await verifyResponse.json();
      setVerificationStatus(result.verified ? 'verified' : 'unverified');
      return result;
    } catch (error) {
      console.error('Verification error:', error);
      setVerificationStatus('error');
      return { verified: false, error: error.message };
    }
  };

  // New Chat functionality
  const startNewChat = () => {
    const newChatId = `chat_${uuidv4()}`;
    setCurrentChatId(newChatId);
    setMessages([]);
    setMultiGenResponses([]);
    setSearchResults([]);
    setVerificationStatus(null);
    setChatHistory(prev => [...prev, { 
      id: newChatId, 
      messages: [], 
      createdAt: new Date() 
    }]);
  };

  // Load Previous Chat
  const loadPreviousChat = (chatId) => {
    const chat = chatHistory.find(c => c.id === chatId);
    if (chat) {
      setCurrentChatId(chatId);
      setMessages(chat.messages);
      setShowHistory(false);
    }
  };

  // Save current chat to history
  const saveCurrentChat = () => {
    setChatHistory(prev => prev.map(chat => 
      chat.id === currentChatId 
        ? { ...chat, messages: [...messages] }
        : chat
    ));
  };

  const handleSendMessage = async () => {
    if (inputValue.trim()) {
      const userMessage = { id: `user_${uuidv4()}`, text: inputValue, isUser: true };
      setMessages(prev => [...prev, userMessage]);
      const currentPrompt = inputValue;
      setInputValue('');
      setIsProcessing(true);

      try {
        // Perform grounded search if enabled
        if (showSearch) {
          const groundedResult = await performGroundedSearch(currentPrompt);
          
          if (groundedResult.success) {
            const aiMessage = { 
              id: `ai_${uuidv4()}`, 
              text: groundedResult.ai_response, 
              isUser: false,
              timestamp: new Date(),
              citations: groundedResult.citations,
              sources: groundedResult.sources,
              isGroundedSearch: true,
              searchResults: groundedResult.search_results
            };
            setMessages(prev => [...prev, aiMessage]);
            
            // Trigger multi-gen after grounded search response
            if (showMultiGen && selectedModalities.length > 0) {
              await handleMultiGenGenerate(currentPrompt, groundedResult.ai_response, groundedResult.search_results || []);
            }
          } else {
            // Fallback to regular AI processing
            const response = await processWithAI(currentPrompt, connectedNodes, []);
            const aiMessage = { 
              id: `ai_${uuidv4()}`, 
              text: response, 
              isUser: false,
              timestamp: new Date()
            };
            setMessages(prev => [...prev, aiMessage]);
            
            // Trigger multi-gen after regular AI response
            if (showMultiGen && selectedModalities.length > 0) {
              await handleMultiGenGenerate(currentPrompt, response, []);
            }
          }
        } else {
          // Regular AI processing
        if (connectedNodes.length > 0) {
            const response = await processWithAI(currentPrompt, connectedNodes, []);
          const aiMessage = { 
            id: `ai_${uuidv4()}`, 
            text: response, 
            isUser: false,
              timestamp: new Date()
          };
          setMessages(prev => [...prev, aiMessage]);

            // Trigger multi-gen after regular AI response
            if (showMultiGen && selectedModalities.length > 0) {
              await handleMultiGenGenerate(currentPrompt, response, []);
            }

          // Generate multiple responses if enabled
          if (showMultiGen) {
            await generateMultipleResponses(currentPrompt);
          }

          // Verify response if enabled
          if (verificationStatus !== null) {
            await verifyResponse(response);
          }
        } else {
          // No connected nodes, just add a placeholder response
          const aiMessage = { 
            id: `ai_${uuidv4()}`, 
            text: "I'm ready to help! Connect some nodes to me to analyze their content.", 
            isUser: false,
            timestamp: new Date()
          };
          setMessages(prev => [...prev, aiMessage]);
        }
        }


        // Save current chat
        saveCurrentChat();
      } catch (error) {
        console.error('Error processing with AI:', error);
        const errorMessage = { 
          id: `ai_${uuidv4()}`, 
          text: "Sorry, I encountered an error processing your request. Please try again.", 
          isUser: false,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsProcessing(false);
      }
    }
  };

  const processWithAI = async (userPrompt, nodes, searchContext = []) => {
    try {
      const response = await fetch('http://localhost:8001/api/ai/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_prompt: userPrompt,
          nodes: nodes,
          search_context: searchContext
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        return result.response;
      } else {
        throw new Error(result.error || 'Unknown error occurred');
      }
    } catch (error) {
      console.error('AI processing error:', error);
      throw error;
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setMultiGenResponses([]);
    setSearchResults([]);
    setVerificationStatus(null);
  };

  // Handle modality selection/deselection
  const toggleModality = (modality) => {
    setSelectedModalities(prev => 
      prev.includes(modality) 
        ? prev.filter(m => m !== modality)
        : [...prev, modality]
    );
  };

  const handleModalClose = () => {
    setShowMultiGenModal(false);
    if (selectedModalities.length > 0) {
      setShowMultiGen(true);
    }
  };

  // Multi-Gen Generation Process
  // React Flow compliant automatic layout system using @dagrejs/dagre
  const getLayoutedElements = (nodes, edges, direction = 'TB') => {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));
    
    const isHorizontal = direction === 'LR';
    dagreGraph.setGraph({ rankdir: direction });

    nodes.forEach((node) => {
      // Set node dimensions based on type following React Flow documentation
      let nodeWidth = 172;
      let nodeHeight = 36;
      
      if (node.type === 'aiChatNode') {
        nodeWidth = 800;
        nodeHeight = 600;
      } else if (node.type === 'imageNode') {
        nodeWidth = 260;
        nodeHeight = 200;
      } else if (node.type === 'pdfNode') {
        nodeWidth = 550;
        nodeHeight = 450;
      } else if (node.type === 'youtubeNode') {
        nodeWidth = 400;
        nodeHeight = 300;
      } else if (node.type === 'documentNode') {
        nodeWidth = 300;
        nodeHeight = 200;
      } else if (node.type === 'textNode') {
        nodeWidth = 250;
        nodeHeight = 150;
      } else if (node.type === 'codeNode') {
        nodeWidth = 350;
        nodeHeight = 250;
      } else if (node.type === 'websiteNode') {
        nodeWidth = 400;
        nodeHeight = 300;
      }
      
      dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
    });

    edges.forEach((edge) => {
      dagreGraph.setEdge(edge.source, edge.target);
    });

    dagre.layout(dagreGraph);

    return nodes.map((node) => {
      const nodeWithPosition = dagreGraph.node(node.id);
      const nodeWidth = nodeWithPosition.width;
      const nodeHeight = nodeWithPosition.height;
      
      // Set handle positions based on direction
      node.targetPosition = isHorizontal ? 'left' : 'top';
      node.sourcePosition = isHorizontal ? 'right' : 'bottom';
      
      // Position nodes to prevent overlap
      node.position = {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      };
      
      return node;
    });
  };

  // Enhanced collision detection function
  const checkNodeOverlap = (node1, node2, buffer = 50) => {
    const n1 = { 
      x: node1.position.x - buffer/2, 
      y: node1.position.y - buffer/2,
      width: (node1.width || 400) + buffer,
      height: (node1.height || 300) + buffer
    };
    const n2 = { 
      x: node2.position.x - buffer/2, 
      y: node2.position.y - buffer/2,
      width: (node2.width || 400) + buffer,
      height: (node2.height || 300) + buffer
    };
    
    return !(n1.x + n1.width < n2.x || 
             n2.x + n2.width < n1.x || 
             n1.y + n1.height < n2.y || 
             n2.y + n2.height < n1.y);
  };

  // Smart positioning system with React Flow best practices and collision detection
  const findFreePosition = (nodes, nodeWidth = 400, nodeHeight = 300, spacing = 100) => {
    if (nodes.length === 0) {
      return { x: 100, y: 100 };
    }

    // Try positions in a spiral pattern from center
    const centerX = 400;
    const centerY = 300;
    const maxAttempts = 100;
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      // Calculate spiral position
      const angle = attempt * 0.5;
      const radius = spacing * (1 + attempt * 0.3);
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      
      const testNode = { 
        position: { x, y }, 
        width: nodeWidth, 
        height: nodeHeight 
      };
      
      // Check if this position overlaps with any existing nodes
      let hasOverlap = false;
      for (const existingNode of nodes) {
        if (checkNodeOverlap(testNode, existingNode, spacing)) {
          hasOverlap = true;
          break;
        }
      }
      
      if (!hasOverlap) {
        return { x, y };
      }
    }
    
    // Fallback: place to the right of existing nodes
    const rightmostNode = nodes.reduce((max, node) => 
      node.position.x > max.position.x ? node : max, nodes[0]);
    
    return { 
      x: rightmostNode.position.x + nodeWidth + spacing, 
      y: rightmostNode.position.y 
    };
  };

  // Helper function to get node dimensions based on type
  const getNodeDimensions = (nodeType) => {
    const dimensions = {
      'aiChatNode': { width: 800, height: 600 },
      'imageNode': { width: 260, height: 200 },
      'pdfNode': { width: 550, height: 450 },
      'youtubeNode': { width: 400, height: 300 },
      'documentNode': { width: 300, height: 200 },
      'textNode': { width: 250, height: 150 },
      'codeNode': { width: 350, height: 250 },
      'websiteNode': { width: 400, height: 300 }
    };
    return dimensions[nodeType] || { width: 400, height: 300 };
  };

  const handleMultiGenGenerate = async (userPrompt, aiResponse, searchContext) => {
    if (selectedModalities.length === 0) return;

    const newNodes = [];
    const currentNodes = getNodes() || [];
    const currentEdges = getEdges() || [];
    
    // Add node dimensions for proper collision detection
    const nodesWithDimensions = currentNodes.map(node => ({
      ...node,
      width: getNodeDimensions(node.type).width,
      height: getNodeDimensions(node.type).height
    }));

    // Generate Image Node if selected
    if (selectedModalities.includes('image')) {
      const imageNodeId = `image_${uuidv4()}`;
      const imageDims = getNodeDimensions('imageNode');
      const imagePosition = findFreePosition(nodesWithDimensions, imageDims.width, imageDims.height, 100);
      
      const imageNode = {
        id: imageNodeId,
        type: 'imageNode',
        position: imagePosition,
        width: imageDims.width,
        height: imageDims.height,
        data: {
          isLoading: true,
          imageUrl: null,
          userPrompt: userPrompt,
          aiResponse: aiResponse,
          searchContext: searchContext,
          onClose: () => handleNodeClose(imageNodeId)
        }
      };
      newNodes.push(imageNode);
      nodesWithDimensions.push(imageNode);
    }

    // Generate PDF Node if selected
    if (selectedModalities.includes('pdf')) {
      const pdfNodeId = `pdf_${uuidv4()}`;
      const pdfDims = getNodeDimensions('pdfNode');
      const pdfPosition = findFreePosition(nodesWithDimensions, pdfDims.width, pdfDims.height, 100);
      
      const pdfNode = {
        id: pdfNodeId,
        type: 'pdfNode',
        position: pdfPosition,
        width: pdfDims.width,
        height: pdfDims.height,
        data: {
          isLoading: true,
          pdfContent: '',
          userPrompt: userPrompt,
          aiResponse: aiResponse,
          searchContext: searchContext,
          connectedNodes: connectedNodes,
          onClose: () => handleNodeClose(pdfNodeId)
        }
      };
      newNodes.push(pdfNode);
      nodesWithDimensions.push(pdfNode);
    }

    // Add nodes with collision-free positioning
    if (newNodes.length > 0) {
      // Wait for nodes to be initialized before adding them
      if (nodesInitialized) {
        addNodes(newNodes);
        setGeneratedNodes(newNodes.map(node => node.id));
      } else {
        // If nodes aren't initialized yet, add them and let the effect handle positioning
        addNodes(newNodes);
        setGeneratedNodes(newNodes.map(node => node.id));
      }
    }
  };

  const handleNodeClose = (nodeId) => {
    deleteElements({ nodes: [{ id: nodeId }] });
    setGeneratedNodes(prev => prev.filter(id => id !== nodeId));
  };

  return (
    <div 
      className="bg-white/10 backdrop-blur-sm rounded-lg p-2 border border-white/20 w-[800px] h-[600px] flex flex-col relative glow-effect" 
      style={{ 
        minWidth: '800px', 
        minHeight: '600px',
        boxShadow: '0 0 20px rgba(0, 170, 255, 0.3), 0 0 40px rgba(0, 170, 255, 0.1)',
        animation: 'glow-pulse 3s ease-in-out infinite alternate'
      }}
    >
      {/* Top Bar */}
      <div 
        className="bg-[#00aaff] px-4 py-2 rounded-t-lg flex items-center justify-between"
        style={{
          boxShadow: '0 0 15px rgba(0, 170, 255, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
        }}
      >
        <div className="flex items-center space-x-2">
          <BotMessageSquare className="h-4 w-4 text-white" />
          <span className="text-sm font-medium text-white">AI ASSISTANT</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-6 p-0 hover:bg-[#0088cc] text-white"
          onClick={() => data?.onClose?.()}
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
      
      {/* Main Content */}
      <div className="flex flex-1 min-w-0 h-full overflow-hidden">
        {/* Left Sidebar */}
        <div 
          className="w-48 bg-white/10 backdrop-blur-sm rounded-lg p-2 border border-white/20 m-2 min-w-0"
          style={{
            boxShadow: '0 0 10px rgba(0, 170, 255, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
          }}
        >
          <Button
            onClick={startNewChat}
            className="w-full bg-[#00aaff] hover:bg-[#0088cc] text-white text-sm py-2 px-3 rounded-lg mb-4 flex items-center justify-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Chat
          </Button>
          
          <div className="text-sm font-medium text-white mb-2">Previous Chats</div>
          
          <div className="space-y-1 overflow-y-auto flex-1">
            {chatHistory.length > 0 ? (
              chatHistory.map((chat) => (
              <button
                key={chat.id}
                className={`w-full text-left p-2 rounded text-sm ${
                  chat.id === currentChatId 
                      ? 'bg-[#00aaff]/30 text-white' 
                      : 'text-white/70 hover:bg-white/10'
                }`}
                onClick={() => loadPreviousChat(chat.id)}
              >
                Chat {chat.id.slice(-6)}
              </button>
              ))
            ) : (
              <div className="text-white/50 text-xs text-center py-4">
                No previous chats
              </div>
            )}
          </div>
        </div>
        
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col min-w-0 h-full">
          {/* Chat Area */}
          <div className="flex-1 overflow-y-auto overflow-x-hidden overscroll-contain min-h-0">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm space-y-3 px-4">
                <div className="text-center">
                  <div className="text-lg font-medium text-white/80 mb-2">Hi! I'm your AI Assistant</div>
                  <div className="text-sm text-white/60 leading-relaxed">
                    I can analyze content from connected nodes, perform grounded searches, 
                    generate images, create PDF reports, and help you with various tasks. 
                    Connect some nodes to me or ask me anything!
                  </div>
                </div>
                {connectedNodes.length > 0 && (
                  <div className="text-xs text-gray-400 bg-white/10 px-3 py-1 rounded-full">
                    Connected: {connectedNodes.length} node{connectedNodes.length !== 1 ? 's' : ''}
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4 p-2">
                {messages.map((message) => (
                  <div key={message.id} className="break-words">
                    {/* Message Label */}
                    <div className={`text-xs font-medium mb-1 px-1 ${
                      message.isUser 
                        ? 'text-blue-300 text-right mr-8' 
                        : 'text-green-300 text-left ml-8'
                    }`}>
                      {message.isUser ? 'YOU' : 'AI'}
                    </div>
                    
                    <div
                      className={`p-3 rounded-lg text-sm break-words whitespace-normal ai-response ${
                        message.isUser
                          ? 'bg-blue-100 text-blue-900 ml-8'
                          : 'bg-gray-100 text-gray-800 mr-8'
                      }`}
                    >
                      <div className="break-words whitespace-normal ai-response-content">
                        <Linkify
                          componentDecorator={(decoratedHref, decoratedText, key) => (
                            <a
                              key={key}
                              href={decoratedHref}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 underline font-medium"
                              style={{ wordBreak: 'break-all' }}
                            >
                              {decoratedText}
                            </a>
                          )}
                    >
                      {message.text}
                        </Linkify>
                      </div>
                      {message.timestamp && (
                        <div className="text-xs text-gray-500 mt-1">
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </div>
                      )}
                    </div>
                    
                    {/* Grounded Search Citations and Sources */}
                    {message.isGroundedSearch && message.citations && message.citations.length > 0 && (
                      <div className="mr-8 mt-3 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 break-words shadow-sm">
                        <div className="text-blue-800 text-sm font-semibold mb-3 flex items-center">
                          <Search className="h-4 w-4 mr-2" />
                          📚 Research Citations & References
                        </div>
                        <div className="text-sm text-gray-700 space-y-2">
                          {message.citations.map((citation, idx) => (
                            <div key={idx} className="flex items-start break-words bg-white/60 p-3 rounded-md border border-blue-100">
                              <span className="text-blue-600 font-bold mr-3 flex-shrink-0 text-xs bg-blue-100 px-2 py-1 rounded-full">[{idx + 1}]</span>
                              <div className="flex-1 break-words whitespace-normal">
                                <Linkify
                                  componentDecorator={(decoratedHref, decoratedText, key) => (
                                    <a
                                      key={key}
                                      href={decoratedHref}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-blue-600 hover:text-blue-800 underline font-medium hover:bg-blue-50 px-1 rounded transition-colors"
                                      style={{ wordBreak: 'break-all' }}
                                    >
                                      {decoratedText}
                                    </a>
                                  )}
                                >
                                  {citation}
                                </Linkify>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Sources List */}
                    {message.isGroundedSearch && message.sources && message.sources.length > 0 && (
                      <div className="mr-8 mt-3 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200 break-words shadow-sm">
                        <div className="text-green-800 text-sm font-semibold mb-3 flex items-center">
                          <FileText className="h-4 w-4 mr-2" />
                          🔗 Source Materials & References
                        </div>
                        <div className="text-sm text-gray-700 space-y-3">
                          {message.sources.map((source, idx) => (
                            <div key={idx} className="flex items-start break-words bg-white/60 p-3 rounded-md border border-green-100">
                              <span className="text-green-600 font-bold mr-3 flex-shrink-0 text-xs bg-green-100 px-2 py-1 rounded-full">
                                {source.number || `[${idx + 1}]`}
                              </span>
                              <div className="flex-1 break-words">
                                <div className="font-semibold break-words whitespace-normal text-gray-800 mb-2 text-sm">{source.title}</div>
                                {source.url && source.url !== "YouTube Video Context" && (
                                  <a 
                                    href={source.url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-blue-600 hover:text-blue-800 hover:underline break-all text-xs bg-blue-50 hover:bg-blue-100 px-2 py-1 rounded transition-colors inline-block"
                                  >
                                    🔗 {source.url}
                                  </a>
                                )}
                                {source.snippet && (
                                  <div className="text-gray-600 mt-2 text-xs break-words whitespace-normal italic bg-gray-50 p-2 rounded border-l-2 border-gray-300">
                                    "{source.snippet}"
                                  </div>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Legacy Search Context Display */}
                    {message.searchContext && !message.isGroundedSearch && (
                      <div className="ml-8 mt-1 p-2 bg-blue-50 rounded text-xs break-words">
                        <div className="text-blue-700 font-semibold mb-2">Search Results & Citations:</div>
                        {message.searchContext.slice(0, 2).map((result, idx) => (
                          <div key={idx} className="text-gray-600 break-words whitespace-normal mb-1">
                            <Linkify
                              componentDecorator={(decoratedHref, decoratedText, key) => (
                                <a
                                  key={key}
                                  href={decoratedHref}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-blue-600 hover:text-blue-800 underline font-medium"
                                  style={{ wordBreak: 'break-all' }}
                                >
                                  {decoratedText}
                                </a>
                              )}
                            >
                              • {result.title || result.snippet}
                            </Linkify>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
                
                {/* Multi-Generation Responses */}
                {multiGenResponses.length > 0 && (
                  <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200 break-words">
                    <div className="text-green-700 text-xs mb-2 font-semibold">Alternative Responses:</div>
                    {multiGenResponses.map((response, idx) => (
                      <div key={idx} className="text-sm text-gray-700 mb-2 p-2 bg-white rounded border border-gray-100 break-words whitespace-normal">
                        <Linkify
                          componentDecorator={(decoratedHref, decoratedText, key) => (
                            <a
                              key={key}
                              href={decoratedHref}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 underline font-medium"
                              style={{ wordBreak: 'break-all' }}
                            >
                              {decoratedText}
                            </a>
                          )}
                        >
                        {response}
                        </Linkify>
                      </div>
                    ))}
                  </div>
                )}
                
                {/* Verification Status */}
                {verificationStatus && (
                  <div className="flex items-center space-x-2 mt-2 text-xs">
                    {verificationStatus === 'verifying' && (
                      <>
                        <RefreshCw className="h-3 w-3 animate-spin text-yellow-600" />
                        <span className="text-yellow-600">Verifying response...</span>
                      </>
                    )}
                    {verificationStatus === 'verified' && (
                      <>
                        <CheckCircle className="h-3 w-3 text-green-600" />
                        <span className="text-green-600">Response verified</span>
                      </>
                    )}
                    {verificationStatus === 'unverified' && (
                      <>
                        <AlertCircle className="h-3 w-3 text-red-600" />
                        <span className="text-red-600">Response needs review</span>
                      </>
                    )}
                    {verificationStatus === 'error' && (
                      <>
                        <AlertCircle className="h-3 w-3 text-red-600" />
                        <span className="text-red-600">Verification failed</span>
                      </>
                    )}
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="p-3 border-t border-white/20 flex-shrink-0">
            <div className="flex items-center space-x-2 mb-2 min-w-0">
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 hover:bg-gray-100 text-gray-500"
              >
                <Paperclip className="h-3 w-3" />
              </Button>
              <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }} className="flex items-center gap-2 flex-1 min-w-0">
                <div className="flex-1 relative min-w-0">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message..."
                    aria-label="Type your message"
                    className="w-full px-3 py-2 text-sm bg-white/10 backdrop-blur-sm border border-white/30 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-blue-400/50 focus:border-blue-400/50"
                  />
                </div>
                <Button
                  type="submit"
                  size="sm"
                  aria-label="Send message"
                  className="h-8 w-8 p-0 bg-[#00aaff] hover:bg-[#0088cc] border border-[#00aaff]/30 flex-shrink-0"
                  disabled={isProcessing || !inputValue.trim()}
                >
                  {isProcessing ? (
                    <Loader2 className="h-3 w-3 text-white animate-spin" />
                  ) : (
                    <Send className="h-3 w-3 text-white" />
                  )}
                </Button>
              </form>
            </div>
            
            {/* Feature Controls */}
            <div className="flex items-center justify-between mt-2 min-w-0">
              <div className="flex items-center space-x-2 min-w-0 flex-wrap">
                <Button
                  variant="outline"
                  size="sm"
                  className={`h-6 px-2 text-xs ${showSearch ? 'bg-[#00aaff] text-white border-[#00aaff] shadow-lg shadow-[#00aaff]/25' : 'text-gray-600 border-gray-400 hover:border-[#00aaff]/50'} flex-shrink-0`}
                  onClick={() => setShowSearch(!showSearch)}
                >
                  <Search className="h-3 w-3 mr-1" />
                  GROUNDED SEARCH
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className={`h-6 px-2 text-xs ${showMultiGen ? 'bg-[#00aaff] text-white border-[#00aaff] shadow-lg shadow-[#00aaff]/25' : 'text-gray-600 border-gray-400 hover:border-[#00aaff]/50'} flex-shrink-0`}
                  onClick={() => setShowMultiGenModal(true)}
                >
                  <Atom className="h-3 w-3 mr-1" />
                  MULTI GEN
                </Button>
              </div>
              
              <select className="ai-chat-dropdown text-xs rounded px-2 py-1 flex-shrink-0" defaultValue="grok4">
                <option value="grok4">Grok 4</option>
                <option value="dalle2">DALL-E 2</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Connection Handles (React Flow compliant) */}
      <Handle
        type="target"
        position={Position.Left}
        id="in"
        isConnectable={isConnectable}
        className="w-3 h-3 bg-[#00aaff] border-2 border-white shadow-lg"
        style={{
          boxShadow: '0 0 10px rgba(0, 170, 255, 0.5)'
        }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="out"
        isConnectable={isConnectable}
        className="w-3 h-3 bg-[#00aaff] border-2 border-white shadow-lg"
        style={{
          boxShadow: '0 0 10px rgba(0, 170, 255, 0.5)'
        }}
      />

      {/* Multi-Gen Modal */}
      {showMultiGenModal && (
        <div className="multi-gen-modal-overlay" onClick={handleModalClose}>
          <div className="multi-gen-modal nodrag" onClick={(e) => e.stopPropagation()}>
            <div className="multi-gen-modal-header">
              <h3 className="multi-gen-modal-title">Select Output Modalities</h3>
              <button 
                className="multi-gen-modal-close"
                onClick={handleModalClose}
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <div className="multi-gen-modal-content">
              <div 
                className={`modality-option ${selectedModalities.includes('pdf') ? 'selected' : ''}`}
                onClick={() => toggleModality('pdf')}
              >
                <div className="modality-checkbox">
                  {selectedModalities.includes('pdf') && <CheckCircle className="h-4 w-4" />}
                </div>
                <div className="modality-icon">
                  <FileText className="h-6 w-6" />
                </div>
                <div className="modality-info">
                  <h4 className="modality-title">PDF</h4>
                  <p className="modality-description">Generate formatted PDF documents with text and images</p>
                </div>
              </div>
              
              <div 
                className={`modality-option ${selectedModalities.includes('image') ? 'selected' : ''}`}
                onClick={() => toggleModality('image')}
              >
                <div className="modality-checkbox">
                  {selectedModalities.includes('image') && <CheckCircle className="h-4 w-4" />}
                </div>
                <div className="modality-icon">
                  <Image className="h-6 w-6" />
                </div>
                <div className="modality-info">
                  <h4 className="modality-title">Image</h4>
                  <p className="modality-description">Create visual content and illustrations from text descriptions</p>
                </div>
              </div>
              
              <div 
                className={`modality-option ${selectedModalities.includes('code') ? 'selected' : ''}`}
                onClick={() => toggleModality('code')}
              >
                <div className="modality-checkbox">
                  {selectedModalities.includes('code') && <CheckCircle className="h-4 w-4" />}
                </div>
                <div className="modality-icon">
                  <Code className="h-6 w-6" />
                </div>
                <div className="modality-info">
                  <h4 className="modality-title">Code</h4>
                  <p className="modality-description">Generate code snippets and programming solutions</p>
                </div>
              </div>
            </div>
            
            <div className="multi-gen-modal-footer">
              <div className="selected-count">
                {selectedModalities.length} modalit{selectedModalities.length !== 1 ? 'ies' : 'y'} selected
              </div>
              <button 
                className="confirm-button"
                onClick={handleModalClose}
                disabled={selectedModalities.length === 0}
              >
                Confirm Selection
              </button>
            </div>
          </div>
        </div>
             )}

    </div>
  );
};

export default AIChatNode;
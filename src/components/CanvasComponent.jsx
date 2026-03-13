import React, { useCallback, useRef, useState } from 'react';
import { ReactFlow, Background, Controls, ReactFlowProvider, applyNodeChanges, applyEdgeChanges } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import AIChatNode from './AIChatNode';
import TestNode from './TestNode';
import TextNode from './TextNode';
import DocumentNode from './DocumentNode';
import ImageNode from './ImageNode';
import WebsiteNode from './WebsiteNode';
import YouTubeNode from './YouTubeNode';
import CodeNode from './CodeNode';
import PDFNode from './PDFNode';

const CanvasComponent = ({ onAddAIChatNode, onAddTextNode, onAddDocumentNode, onAddImageNode, onAddWebsiteNode, onAddYouTubeNode, onAddCodeNode, onUndo, onRedo }) => {
  const reactFlowWrapper = useRef(null);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [deletedNodes, setDeletedNodes] = useState([]);


  // Node types for React Flow
  const nodeTypes = {
    aiChatNode: AIChatNode,
    testNode: TestNode,
    textNode: TextNode,
    documentNode: DocumentNode,
    imageNode: ImageNode,
    websiteNode: WebsiteNode,
    youtubeNode: YouTubeNode,
    codeNode: CodeNode,
    pdfNode: PDFNode,
  };

  const onInit = useCallback((instance) => {
    setReactFlowInstance(instance);
  }, []);

  // Connection validation function
  const isValidConnection = useCallback((connection) => {
    // Check if target is AI chat node and limit source connections to 100
    const targetNode = nodes.find(node => node.id === connection.target);
    if (targetNode && targetNode.type === 'aiChatNode') {
      const existingConnections = edges.filter(edge => edge.target === connection.target);
      console.log(`AI Chat Node connections: ${existingConnections.length}/100`);
      if (existingConnections.length >= 100) {
        console.log('Connection limit reached for AI Chat Node');
        return false;
      }
    }
    return true;
  }, [nodes, edges]);

  const onConnect = useCallback((params) => {
    console.log('Connection attempt:', params);
    if (isValidConnection(params)) {
      console.log('Connection allowed');
      const newEdge = {
        ...params,
        id: `edge-${params.source}-${params.target}-${Date.now()}`,
        animated: true
      };
      setEdges((eds) => [...eds, newEdge]);
    } else {
      console.log('Connection rejected');
    }
  }, [isValidConnection]);

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  // Function to find the next available position
  const getNextAvailablePosition = useCallback(() => {
    const nodeWidth = 320; // Approximate width of nodes
    const nodeHeight = 200; // Reduced height for better spacing
    const padding = 80; // Increased padding between nodes
    const gridSize = 60; // Grid size for positioning
    
    // Get all existing node positions
    const existingPositions = nodes.map(node => ({
      x: node.position.x,
      y: node.position.y,
      width: nodeWidth,
      height: nodeHeight
    }));
    
    // Start from a base position
    let x = 150;
    let y = 150;
    let attempts = 0;
    const maxAttempts = 200; // Increased attempts
    
    while (attempts < maxAttempts) {
      let hasOverlap = false;
      
      // Check if current position overlaps with any existing node
      for (const existingPos of existingPositions) {
        if (
          x < existingPos.x + existingPos.width + padding &&
          x + nodeWidth + padding > existingPos.x &&
          y < existingPos.y + existingPos.height + padding &&
          y + nodeHeight + padding > existingPos.y
        ) {
          hasOverlap = true;
          break;
        }
      }
      
      if (!hasOverlap) {
        return { x, y };
      }
      
      // Move to next position in a grid pattern
      x += gridSize;
      if (x > 1000) { // Reset x and move down
        x = 150;
        y += gridSize;
      }
      
      attempts++;
    }
    
    // Fallback: return a position with more spacing
    return {
      x: 150 + (nodes.length * 400),
      y: 150 + (Math.floor(nodes.length / 3) * 300)
    };
  }, [nodes]);

  // Function to add Test Node
  const addTestNode = useCallback(() => {
    console.log('addTestNode called');
    const newNode = {
      id: `test-${Date.now()}`,
      type: 'testNode',
      position: { x: 200, y: 200 },
      data: { id: `test-${Date.now()}` },
    };
    console.log('Adding test node:', newNode);
    setNodes((nds) => {
      console.log('Current nodes:', nds);
      const newNodes = [...nds, newNode];
      console.log('New nodes array:', newNodes);
      return newNodes;
    });
  }, []);

  // Function to add AI Chat Node
  const addAIChatNode = useCallback(() => {
    const position = getNextAvailablePosition();
    const newNode = {
      id: `ai-chat-${Date.now()}`,
      type: 'aiChatNode',
      position,
      data: {
        onClose: () => {
          setNodes((nds) => nds.filter((node) => node.id !== newNode.id));
        },
      },
    };
    
    setNodes((nds) => [...nds, newNode]);
    setDeletedNodes([]); // Clear deleted nodes when adding new ones
  }, [getNextAvailablePosition]);

  // Function to focus on a node
  const focusOnNode = useCallback((nodeId) => {
    if (reactFlowInstance) {
      const node = nodes.find(n => n.id === nodeId);
      if (node) {
        // Use fitView with specific node
        reactFlowInstance.fitView({
          nodes: [{ id: nodeId }],
          padding: 0.3,
          duration: 800,
          minZoom: 0.5,
          maxZoom: 2
        });
      }
    }
  }, [reactFlowInstance, nodes]);

  // Function to add Text Node
  const addTextNode = useCallback(() => {
    const position = getNextAvailablePosition();
    const newNode = {
      id: `text-${Date.now()}`,
      type: 'textNode',
      position,
      data: {
        onClose: () => {
          setNodes((nds) => nds.filter((node) => node.id !== newNode.id));
        },
        onFocus: () => focusOnNode(newNode.id),
      },
    };
    
    setNodes((nds) => [...nds, newNode]);
    setDeletedNodes([]); // Clear deleted nodes when adding new ones
  }, [getNextAvailablePosition, focusOnNode]);

  // Function to add Document Node
  const addDocumentNode = useCallback(() => {
    const position = getNextAvailablePosition();
    const newNode = {
      id: `document-${Date.now()}`,
      type: 'documentNode',
      position,
      data: {
        onClose: () => {
          setNodes((nds) => nds.filter((node) => node.id !== newNode.id));
        },
      },
    };
    
    setNodes((nds) => [...nds, newNode]);
    setDeletedNodes([]); // Clear deleted nodes when adding new ones
  }, [getNextAvailablePosition]);

  // Function to add Image Node
  const addImageNode = useCallback((imageSrc) => {
    const position = getNextAvailablePosition();
    const newNode = {
      id: `image-${Date.now()}`,
      type: 'imageNode',
      position,
      data: {
        imageSrc,
        onClose: () => {
          setNodes((nds) => nds.filter((node) => node.id !== newNode.id));
        },
      },
    };
    
    setNodes((nds) => [...nds, newNode]);
    setDeletedNodes([]); // Clear deleted nodes when adding new ones
  }, [getNextAvailablePosition]);

  // Function to add Website Node
  const addWebsiteNode = useCallback(() => {
    const position = getNextAvailablePosition();
    const newNode = {
      id: `website-${Date.now()}`,
      type: 'websiteNode',
      position,
      data: {
        initialUrl: '',
        onClose: () => {
          setNodes((nds) => nds.filter((node) => node.id !== newNode.id));
        },
        onSave: (nodeId, url) => {
          setNodes((nds) => nds.map(node => 
            node.id === nodeId ? { ...node, data: { ...node.data, initialUrl: url } } : node
          ));
        },
      },
    };
    
    setNodes((nds) => [...nds, newNode]);
    setDeletedNodes([]); // Clear deleted nodes when adding new ones
  }, [getNextAvailablePosition]);

  // Function to add YouTube Node
  const addYouTubeNode = useCallback((videoData) => {
    const position = getNextAvailablePosition();
    const newNode = {
      id: `youtube-${Date.now()}`,
      type: 'youtubeNode',
      position,
      data: {
        videoData: videoData,
        onClose: () => {
          setNodes((nds) => nds.filter((node) => node.id !== newNode.id));
        },
      },
    };
    
    setNodes((nds) => [...nds, newNode]);
    setDeletedNodes([]); // Clear deleted nodes when adding new ones
  }, [getNextAvailablePosition]);

  // Function to add Code Node
  const addCodeNode = useCallback(() => {
    const position = getNextAvailablePosition();
    const newNode = {
      id: `code-${Date.now()}`,
      type: 'codeNode',
      position,
                       data: {
                   initialCode: 'def hello_world():\n    print("Hello, World!")\n    return "Success"',
                   language: 'python',
        onClose: () => {
          setNodes((nds) => nds.filter((node) => node.id !== newNode.id));
        },
        onSave: (nodeId, code, language) => {
          setNodes((nds) => nds.map(node => 
            node.id === nodeId ? { ...node, data: { ...node.data, initialCode: code, language } } : node
          ));
        },
      },
    };
    
    setNodes((nds) => [...nds, newNode]);
    setDeletedNodes([]); // Clear deleted nodes when adding new ones
  }, [getNextAvailablePosition]);

  // Expose the addAIChatNode function to parent
  React.useEffect(() => {
    if (onAddAIChatNode) {
      onAddAIChatNode(addAIChatNode);
    }
  }, [addAIChatNode, onAddAIChatNode]);

  // Undo function - remove last node and store it for redo
  const undo = useCallback(() => {
    setNodes((nds) => {
      if (nds.length > 0) {
        const lastNode = nds[nds.length - 1];
        setDeletedNodes(prev => [...prev, lastNode]);
        return nds.slice(0, -1);
      }
      return nds;
    });
  }, []);

  // Redo function - restore last deleted node
  const redo = useCallback(() => {
    setDeletedNodes((deleted) => {
      if (deleted.length > 0) {
        const lastDeleted = deleted[deleted.length - 1];
        setNodes(prev => [...prev, lastDeleted]);
        return deleted.slice(0, -1);
      }
      return deleted;
    });
  }, []);

  // Expose the addTextNode function to parent
  React.useEffect(() => {
    if (onAddTextNode) {
      onAddTextNode(addTextNode);
    }
  }, [addTextNode, onAddTextNode]);

  // Expose the addDocumentNode function to parent
  React.useEffect(() => {
    if (onAddDocumentNode) {
      onAddDocumentNode(addDocumentNode);
    }
  }, [addDocumentNode, onAddDocumentNode]);

  // Expose the addImageNode function to parent
  React.useEffect(() => {
    if (onAddImageNode) {
      onAddImageNode(addImageNode);
    }
  }, [addImageNode, onAddImageNode]);

  // Expose the addWebsiteNode function to parent
  React.useEffect(() => {
    if (onAddWebsiteNode) {
      onAddWebsiteNode(addWebsiteNode);
    }
  }, [addWebsiteNode, onAddWebsiteNode]);

  // Expose the addYouTubeNode function to parent
  React.useEffect(() => {
    if (onAddYouTubeNode) {
      onAddYouTubeNode(addYouTubeNode);
    }
  }, [addYouTubeNode, onAddYouTubeNode]);

  // Expose the addCodeNode function to parent
  React.useEffect(() => {
    if (onAddCodeNode) {
      onAddCodeNode(addCodeNode);
    }
  }, [addCodeNode, onAddCodeNode]);

  // Expose undo/redo functions to parent
  React.useEffect(() => {
    if (onUndo) {
      onUndo(undo);
    }
  }, [undo, onUndo]);

  React.useEffect(() => {
    if (onRedo) {
      onRedo(redo);
    }
  }, [redo, onRedo]);

  return (
    <div className="w-full h-full relative z-0" ref={reactFlowWrapper}>
      <ReactFlow
        onInit={onInit}
        onConnect={onConnect}
        isValidConnection={isValidConnection}
        style={{ backgroundColor: '#002147' }}
        panOnScroll={true}
        zoomOnScroll={true}
        zoomOnPinch={true}
        minZoom={0.1}
        maxZoom={4}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
        fitView={false}
        attributionPosition="bottom-left"
        proOptions={{ hideAttribution: true }}
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodesDraggable={true}
        nodesConnectable={true}
        elementsSelectable={true}
      >
        <Background 
          color="rgba(255,255,255,0.3)"
          gap={30}
          size={1}
          variant="dots"
        />
        <Controls 
          showZoom={true}
          showFitView={true}
          showInteractive={false}
          position="bottom-right"
        />
      </ReactFlow>
    </div>
  );
};

const CanvasComponentWrapper = ({ onAddAIChatNode, onAddTextNode, onAddDocumentNode, onAddImageNode, onAddWebsiteNode, onAddYouTubeNode, onAddCodeNode, onUndo, onRedo }) => {
  return (
    <ReactFlowProvider>
      <div className="w-screen h-screen">
        <CanvasComponent 
          onAddAIChatNode={onAddAIChatNode} 
          onAddTextNode={onAddTextNode}
          onAddDocumentNode={onAddDocumentNode}
          onAddImageNode={onAddImageNode}
          onAddWebsiteNode={onAddWebsiteNode}
          onAddYouTubeNode={onAddYouTubeNode}
          onAddCodeNode={onAddCodeNode}
          onUndo={onUndo}
          onRedo={onRedo}
        />
      </div>
    </ReactFlowProvider>
  );
};

export default CanvasComponentWrapper;

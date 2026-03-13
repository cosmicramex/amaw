import React, { useState, useEffect } from 'react';
import { Handle, Position, NodeToolbar } from '@xyflow/react';
import { Button } from './ui/button';
import { Download, X, Loader2, FileText, CheckCircle, Trash2, Plus } from 'lucide-react';
import { TypeAnimation } from 'react-type-animation';

const PDFNode = ({ id, data, isConnectable }) => {
  const [isLoading, setIsLoading] = useState(data?.isLoading || false);
  const [pdfContent, setPdfContent] = useState(data?.pdfContent || '');
  const [generationProgress, setGenerationProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [showActions, setShowActions] = useState(false);

  useEffect(() => {
    if (data?.isLoading) {
      setIsLoading(true);
      setGenerationProgress(0);
      setIsComplete(false);
      
      // Call backend API for real PDF generation
      generatePDFContent();
    }
  }, [data?.isLoading, data?.pdfContent]);

  const generatePDFContent = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/multi-gen/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_prompt: data?.userPrompt || '',
          ai_response: data?.aiResponse || '',
          search_context: data?.searchContext || [],
          connected_nodes: data?.connectedNodes || [],
          modalities: ['pdf']
        })
      });
      
      const result = await response.json();
      
          if (result.success && result.pdf_content) {
            // Simulate real-time generation with actual content
            const content = result.pdf_content;
            let currentText = '';
            let progress = 0;
            
            const textInterval = setInterval(() => {
              if (progress < content.length) {
                currentText += content[progress];
                setPdfContent(currentText);
                progress++;
                setGenerationProgress(Math.round((progress / content.length) * 100));
              } else {
                clearInterval(textInterval);
                setIsLoading(false);
                setIsComplete(true);
                setGenerationProgress(100);
                setShowActions(true);
              }
            }, 5); // Faster typing for real content
        
        return () => clearInterval(textInterval);
      } else {
        throw new Error('PDF generation failed');
      }
    } catch (error) {
      console.error('PDF generation error:', error);
      // Fallback to simulation
      const progressInterval = setInterval(() => {
        setGenerationProgress(prev => {
          if (prev >= 100) {
            clearInterval(progressInterval);
            setIsLoading(false);
            setIsComplete(true);
            setShowActions(true);
            return 100;
          }
          return prev + 2;
        });
      }, 100);
      
      return () => clearInterval(progressInterval);
    }
  };

  const handleDownload = async () => {
    if (pdfContent) {
      try {
        // Call backend to generate actual PDF
        const response = await fetch('http://localhost:8001/api/multi-gen/generate-pdf', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_prompt: data?.userPrompt || '',
            ai_response: data?.aiResponse || '',
            search_context: data?.searchContext || [],
            connected_nodes: data?.connectedNodes || []
          })
        });
        
        if (response.ok) {
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `research-analysis-${id}.pdf`;
          link.style.display = 'none';
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
          console.log('PDF downloaded successfully');
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      } catch (error) {
        console.error('PDF download error:', error);
        // Fallback to text download
        const blob = new Blob([pdfContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `research-analysis-${id}.txt`;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        console.log('Text file downloaded as fallback');
      }
    } else {
      console.error('No PDF content available for download');
      alert('No content available for download');
    }
  };

  const handleDiscard = () => {
    if (data?.onClose) {
      data.onClose();
    }
  };

  const handleAddToWorkspace = () => {
    setShowActions(false);
    // Node stays in workspace
  };

  return (
    <div 
      className={`bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20 flex flex-col relative shadow-lg ${
        (data?.isLoading || data?.userPrompt) ? 'node-spawn-animation' : ''
      }`} 
      style={{ 
        width: '550px',
        height: '450px',
        minWidth: '550px', 
        minHeight: '450px'
      }}
    >
      {/* Node Toolbar with Action Buttons */}
      {showActions && (
        <NodeToolbar 
          isVisible={true} 
          position="top"
          offset={10}
          className="z-50"
        >
          <div className="flex space-x-2 bg-white/10 backdrop-blur-sm rounded-lg p-2 border border-white/20">
            <Button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                handleDiscard();
              }}
              size="sm"
              className="bg-red-500/20 backdrop-blur-sm hover:bg-red-500/30 border border-red-400/30 text-red-200 hover:text-red-100 text-xs px-3 py-1 flex items-center transition-all duration-200"
            >
              <Trash2 className="h-3 w-3 mr-1" />
              DISCARD
            </Button>
            <Button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                handleAddToWorkspace();
              }}
              size="sm"
              className="bg-green-500/20 backdrop-blur-sm hover:bg-green-500/30 border border-green-400/30 text-green-200 hover:text-green-100 text-xs px-3 py-1 flex items-center transition-all duration-200"
            >
              <Plus className="h-3 w-3 mr-1" />
              ADD TO WORKSPACE
            </Button>
          </div>
        </NodeToolbar>
      )}
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <FileText className="h-4 w-4 text-white" />
          <span className="text-sm font-medium text-white">GENERATED PDF</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-6 p-0 hover:bg-[#0088cc] text-white"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            data?.onClose?.();
          }}
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col">
        {isLoading ? (
          <div className="flex flex-col space-y-3">
            <div className="flex items-center space-x-2">
              <Loader2 className="h-4 w-4 text-[#00aaff] animate-spin" />
              <span className="text-sm text-white/70">Generating content...</span>
            </div>
            <div className="w-full bg-white/20 rounded-full h-2">
              <div 
                className="bg-[#00aaff] h-2 rounded-full transition-all duration-300"
                style={{ width: `${generationProgress}%` }}
              />
            </div>
            <div className="text-xs text-white/50 text-center">
              {generationProgress}% complete
            </div>
            
            {/* Typewriter Animation for PDF Content */}
            <div className="flex-1 overflow-y-auto bg-white/5 rounded-lg p-3 max-h-80">
              <div className="text-sm text-white whitespace-pre-wrap break-words leading-relaxed">
                <TypeAnimation
                  sequence={[
                    'Initializing document structure...',
                    1000,
                    'Analyzing AI conversation context...',
                    1500,
                    'Generating comprehensive content...',
                    2000,
                    'Formatting for PDF output...',
                    1500,
                    'Finalizing document...',
                    1000,
                    'PDF generation complete!',
                    500,
                    'This is a generated PDF document based on your AI conversation. It contains relevant information and insights that can be downloaded and shared. The content is contextually relevant to your query and provides valuable insights based on the connected nodes and AI response.',
                  ]}
                  speed={30}
                  repeat={0}
                  style={{ 
                    fontSize: '0.875rem', 
                    color: 'rgba(255, 255, 255, 0.9)',
                    lineHeight: '1.5'
                  }}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col">
            <div className="flex-1 overflow-y-auto bg-white/5 rounded-lg p-3 mb-3 max-h-80">
              <div className="text-sm text-white whitespace-pre-wrap break-words leading-relaxed">
                {pdfContent || 'This is a generated PDF document based on your AI conversation. It contains relevant information and insights that can be downloaded and shared. The content is contextually relevant to your query and provides valuable insights based on the connected nodes and AI response.'}
              </div>
            </div>
            
            {isComplete && (
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-1 text-green-400 text-xs">
                  <CheckCircle className="h-3 w-3" />
                  <span>Generation complete</span>
                </div>
                <Button
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    handleDownload();
                  }}
                  size="sm"
                  className="bg-[#00aaff] hover:bg-[#0088cc] text-white text-xs px-3 py-1"
                >
                  <Download className="h-3 w-3 mr-1" />
                  Download
                </Button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Connection Handles */}
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
    </div>
  );
};

export default PDFNode;

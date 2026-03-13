import React, { useState, useEffect } from 'react';
import { Handle, Position, NodeToolbar } from '@xyflow/react';
import { X, Image as ImageIcon, Loader2, Download, Trash2, Plus } from 'lucide-react';
import { Button } from './ui/button';

const ImageNode = ({ id, data, isConnectable }) => {
  const [isLoading, setIsLoading] = useState(data?.isLoading || false);
  const [imageUrl, setImageUrl] = useState(data?.imageUrl || data?.imageSrc || null);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [showActions, setShowActions] = useState(false);

  useEffect(() => {
    if (data?.isLoading) {
      setIsLoading(true);
      setGenerationProgress(0);
      
      // Call backend API for real DALL-E generation
      generateImageContent();
    }
  }, [data?.isLoading, data?.imageUrl]);

  const generateImageContent = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/multi-gen/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_prompt: data?.userPrompt || '',
          ai_response: data?.aiResponse || '',
          search_context: data?.searchContext || [],
          connected_nodes: data?.connectedNodes || [],
          modalities: ['image']
        })
      });
      
      const result = await response.json();
      
          if (result.success && result.image_url) {
            // Simulate progress updates
            const progressInterval = setInterval(() => {
              setGenerationProgress(prev => {
                if (prev >= 100) {
                  clearInterval(progressInterval);
                  setIsLoading(false);
                  // Handle both base64 data URLs and regular URLs
                  const imageUrl = result.image_url.startsWith('data:') 
                    ? result.image_url 
                    : result.image_url;
                  setImageUrl(imageUrl);
                  setShowActions(true);
                  return 100;
                }
                return prev + 10;
              });
            }, 200);
        
        return () => clearInterval(progressInterval);
      } else {
        throw new Error('Image generation failed');
      }
    } catch (error) {
      console.error('Image generation error:', error);
      // Fallback to simulation
      const progressInterval = setInterval(() => {
        setGenerationProgress(prev => {
          if (prev >= 100) {
            clearInterval(progressInterval);
            setIsLoading(false);
            setImageUrl(data?.imageUrl || 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMzMzIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxOCIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkdlbmVyYXRlZCBJbWFnZTwvdGV4dD48L3N2Zz4=');
            setShowActions(true);
            return 100;
          }
          return prev + 10;
        });
      }, 200);
      
      return () => clearInterval(progressInterval);
    }
  };

  const handleDownload = async () => {
    if (imageUrl) {
      try {
        let blob;
        
        if (imageUrl.startsWith('data:')) {
          // Handle base64 data URL
          const response = await fetch(imageUrl);
          blob = await response.blob();
        } else {
          // Handle regular URL
          const response = await fetch(imageUrl);
          blob = await response.blob();
        }
        
        // Create download link
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `research-image-${id}.jpg`;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        console.log('Image downloaded successfully');
      } catch (error) {
        console.error('Image download error:', error);
        alert('Download failed. Please try again.');
      }
    } else {
      console.error('No image URL available for download');
      alert('No image available for download');
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
      className={`bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20 shadow-lg relative ${
        (data?.isLoading || data?.userPrompt) ? 'node-spawn-animation' : ''
      }`} 
      style={{ 
        minWidth: '260px', 
        minHeight: '200px'
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
          <ImageIcon className="h-5 w-5 text-[#00aaff]" />
          <h3 className="font-medium text-sm text-white">
            {data?.isLoading || data?.userPrompt ? "GENERATED IMAGE" : "IMAGE"}
          </h3>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="h-5 w-5 p-0 hover:bg-white/20 text-white/70 z-10"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            data?.onClose?.();
          }}
        >
          <X className="h-3 w-3" />
        </Button>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center">
        {isLoading ? (
          <div className="flex flex-col items-center space-y-3">
            <div className="relative">
              <Loader2 className="h-12 w-12 text-[#00aaff] animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-xs text-white font-medium">
                  {generationProgress}%
                </div>
              </div>
            </div>
            <div className="text-sm text-white/70 text-center">
              Generating image...
            </div>
            <div className="w-full bg-white/20 rounded-full h-2">
              <div 
                className="bg-[#00aaff] h-2 rounded-full transition-all duration-300"
                style={{ width: `${generationProgress}%` }}
              />
            </div>
          </div>
        ) : imageUrl ? (
          <div className="flex flex-col items-center space-y-3 w-full">
            <div className="w-full h-40 flex items-center justify-center bg-black/20 rounded-lg border border-white/20 overflow-hidden">
              <img 
                src={imageUrl} 
                alt="Generated content" 
                className="max-w-full max-h-full object-contain"
                style={{ 
                  maxWidth: '100%', 
                  maxHeight: '100%',
                  objectFit: 'contain'
                }}
                onError={(e) => {
                  console.error('Image load error:', e);
                  e.target.style.display = 'none';
                }}
              />
            </div>
            {/* Only show download button for generated images */}
            {(data?.isLoading || data?.userPrompt) && (
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
                Download Image
              </Button>
            )}
          </div>
        ) : (
          <div className="text-white/50 text-sm text-center">
            No image generated
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

export default ImageNode;

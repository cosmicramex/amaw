import React, { useState, useRef, useEffect } from 'react';
import { Handle, Position } from '@xyflow/react';
import { X, Globe, ExternalLink } from 'lucide-react';
import { Button } from './ui/button';

const WebsiteNode = ({ id, data, isConnectable }) => {
  const [url, setUrl] = useState(data.initialUrl || '');
  const [isEditing, setIsEditing] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleUrlChange = (e) => {
    setUrl(e.target.value);
  };

  const handleDoubleClick = () => {
    setIsEditing(true);
  };

  const handleBlur = () => {
    setIsEditing(false);
    if (data?.onSave) {
      data.onSave(id, url);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleBlur();
    } else if (e.key === 'Escape') {
      setIsEditing(false);
      setUrl(data.initialUrl || '');
    }
  };

  const handleOpenUrl = () => {
    if (url && (url.startsWith('http://') || url.startsWith('https://'))) {
      window.open(url, '_blank');
    } else if (url) {
      window.open(`https://${url}`, '_blank');
    }
  };

  const isValidUrl = (string) => {
    try {
      new URL(string.startsWith('http') ? string : `https://${string}`);
      return true;
    } catch (_) {
      return false;
    }
  };

  return (
    <div 
      className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20 shadow-lg relative" 
      style={{ minWidth: '280px', minHeight: '120px' }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Globe className="h-5 w-5 icon-glow-website" />
          <h3 className="font-medium text-sm glow-text-website">WEBSITE</h3>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="h-5 w-5 p-0 hover:bg-white/20 text-white/70 z-10"
          onClick={() => data?.onClose?.()}
        >
          <X className="h-3 w-3" />
        </Button>
      </div>

      {/* URL Input Area */}
      <div className="flex items-center space-x-2">
        {isEditing ? (
          <input
            ref={inputRef}
            type="text"
            value={url}
            onChange={handleUrlChange}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            placeholder="Enter any website url"
            className="flex-1 px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white placeholder-white/60 text-sm focus:outline-none focus:ring-2 focus:ring-white/50 focus:border-transparent"
          />
        ) : (
          <div 
            className="flex-1 px-3 py-2 bg-white/20 border border-white/30 rounded-lg text-white text-sm cursor-text"
            onDoubleClick={handleDoubleClick}
          >
            {url || 'Enter any website url'}
          </div>
        )}
        
        <Button
          onClick={handleOpenUrl}
          disabled={!url || !isValidUrl(url)}
          size="sm"
          className="h-8 w-8 p-0 bg-cyan-400 hover:bg-cyan-500 disabled:bg-gray-500 disabled:cursor-not-allowed"
        >
          <ExternalLink className="h-4 w-4 text-white" />
        </Button>
      </div>

      {/* Connection Handles */}
      <Handle
        type="source"
        position={Position.Right}
        isConnectable={isConnectable}
        style={{ 
          width: '20px', 
          height: '20px', 
          background: 'white',
          borderRadius: '50%',
          border: '2px solid rgba(255, 255, 255, 0.3)'
        }}
      />
    </div>
  );
};

export default WebsiteNode;

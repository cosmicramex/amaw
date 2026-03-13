import React, { useState, useRef, useEffect } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Button } from './ui/button';
import { X } from 'lucide-react';

const TextNode = ({ data, isConnectable }) => {
  const [text, setText] = useState('Type here...');
  const [isEditing, setIsEditing] = useState(false);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.select();
    }
  }, [isEditing]);

  const handleTextChange = (e) => {
    setText(e.target.value);
  };

  const handleDoubleClick = () => {
    setIsEditing(true);
    // Auto-focus and zoom to the node
    if (data?.onFocus) {
      data.onFocus();
    }
  };

  const handleBlur = () => {
    setIsEditing(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      setIsEditing(false);
    }
    if (e.key === 'Escape') {
      setIsEditing(false);
    }
  };

  return (
    <div 
      className="bg-white/10 backdrop-blur-sm rounded-lg p-2 border border-white/20 min-w-[200px] min-h-[100px] relative"
      onDoubleClick={handleDoubleClick}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="text-lg icon-glow-text" style={{ fontFamily: 'Playfair Display, serif', fontWeight: '400' }}>T</span>
          <h3 className="font-medium text-sm glow-text-text">TEXT</h3>
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

      {/* Text Content */}
      {isEditing ? (
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleTextChange}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          className="w-full h-full bg-transparent text-white placeholder-white/70 resize-none outline-none text-sm leading-relaxed"
          placeholder="Type here..."
          style={{ minHeight: '80px' }}
        />
      ) : (
        <div 
          className="text-white text-sm leading-relaxed cursor-text select-text"
          style={{ minHeight: '80px', wordWrap: 'break-word' }}
        >
          {text}
        </div>
      )}

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

export default TextNode;

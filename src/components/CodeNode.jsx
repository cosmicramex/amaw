import React, { useState, useRef, useEffect } from 'react';
import { Handle, Position } from '@xyflow/react';
import { X, SquareCode } from 'lucide-react';
import { Button } from './ui/button';
import Editor from 'react-simple-code-editor';
import { Highlight, themes } from 'prism-react-renderer';

const CodeNode = ({ id, data, isConnectable }) => {
  const [code, setCode] = useState(data.initialCode || 'Type something...');
  const [isEditing, setIsEditing] = useState(false);
  const [language, setLanguage] = useState(data.language || 'python');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isEditing]);

  const handleCodeChange = (e) => {
    setCode(e.target.value);
  };

  const handleDoubleClick = () => {
    setIsEditing(true);
  };

  const handleBlur = () => {
    setIsEditing(false);
    if (data?.onSave) {
      data.onSave(id, code, language);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      setIsEditing(false);
    }
  };

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  // Syntax highlighting function using prism-react-renderer
  const highlightCode = (code) => (
    <Highlight theme={themes.nightOwl} code={code} language={language}>
      {({ className, style, tokens, getLineProps, getTokenProps }) => (
        <pre className={className} style={{...style, backgroundColor: 'transparent'}}>
          {tokens.map((line, i) => (
            <div key={i} {...getLineProps({ line })}>
              {line.map((token, key) => (
                <span key={key} {...getTokenProps({ token })} />
              ))}
            </div>
          ))}
        </pre>
      )}
    </Highlight>
  );





  return (
    <div 
      className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20 shadow-lg relative" 
      style={{ minWidth: '300px', minHeight: '200px' }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <SquareCode className="h-5 w-5 icon-glow-code" />
          <h3 className="font-medium text-sm glow-text-code">CODE</h3>
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

      {/* Language Selector */}
      <div className="mb-3">
        <select
          value={language}
          onChange={handleLanguageChange}
          className="px-2 py-1 bg-white/20 border border-white/30 rounded text-white text-xs focus:outline-none focus:ring-2 focus:ring-white/50"
        >
          <option value="javascript">JavaScript</option>
          <option value="python">Python</option>
          <option value="html">HTML</option>
          <option value="css">CSS</option>
          <option value="json">JSON</option>
          <option value="markdown">Markdown</option>
        </select>
      </div>

      {/* Code Area */}
      <div className="relative">
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-2 border border-white/20">
          <Editor
            value={code}
            onValueChange={setCode}
            highlight={highlightCode}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            padding={12}
            style={{
              fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
              fontSize: 12,
              backgroundColor: 'transparent',
              border: 'none',
              borderRadius: '8px',
              minHeight: '128px',
              color: 'white',
              lineHeight: '1.4'
            }}
            textareaClassName="text-white bg-transparent"
            preClassName="text-white bg-transparent"
          />
        </div>
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

export default CodeNode;

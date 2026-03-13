import React, { useState, useRef } from 'react';
import { Handle, Position } from '@xyflow/react';
import { X, Upload, FileText } from 'lucide-react';
import { Button } from './ui/button';

const DocumentNode = ({ id, data, isConnectable }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileUpload = (files) => {
    const newFiles = Array.from(files).map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: file.type,
      file: file
    }));
    setUploadedFiles(prev => [...prev, ...newFiles]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    handleFileUpload(files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleFileInputChange = (e) => {
    const files = e.target.files;
    handleFileUpload(files);
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const containerStyle = {
    minWidth: '280px',
    ...(uploadedFiles.length === 0 ? { minHeight: '200px' } : {})
  };

  return (
    <div 
      className="bg-white/10 backdrop-blur-sm rounded-lg px-4 pt-4 pb-2 border border-white/20 shadow-lg relative" 
      style={containerStyle}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
                 <div className="flex items-center space-x-2">
           <FileText className="h-5 w-5 icon-glow-document" />
           <h3 className="font-medium text-sm glow-text-document">DOCUMENT</h3>
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

      {/* Upload Area - Only show if no files uploaded */}
      {uploadedFiles.length === 0 && (
        <div
          className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
            isDragOver 
              ? 'border-white/60 bg-white/10' 
              : 'border-white/30 bg-white/5'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="flex flex-col items-center space-y-2">
            <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
              <Upload className="h-6 w-6 text-white" />
            </div>
            <p className="text-white text-sm">Drop files here</p>
            <p className="text-white/60 text-xs">or click to browse</p>
          </div>
        </div>
      )}

      {/* File Input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        onChange={handleFileInputChange}
        className="hidden"
      />

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="mt-2 space-y-2">
          <h4 className="text-white text-xs font-medium">Uploaded Files:</h4>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {uploadedFiles.map((file) => (
              <div key={file.id} className="flex items-center justify-between bg-white/10 rounded px-2 py-1.5">
                <div className="flex items-center space-x-2 flex-1 min-w-0">
                  <FileText className="h-4 w-4 text-white/70 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p className="text-white text-xs truncate leading-tight">{file.name}</p>
                    <p className="text-white/60 text-[10px] leading-tight">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-4 w-4 p-0 hover:bg-white/20 text-white/70"
                  onClick={() => removeFile(file.id)}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </div>
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

export default DocumentNode;

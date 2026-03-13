import React, { useRef } from 'react';
import { Button } from './ui/button';
import { Plus, FileText, Image, Globe, Youtube, MessageCircle, Folder, Undo, Redo, SquareCode } from 'lucide-react';

const Toolbar = ({ onAIChatClick, onTextClick, onDocumentClick, onImageClick, onGlobeClick, onYouTubeClick, onCodeClick, onUndoClick, onRedoClick }) => {
  const fileInputRef = useRef(null);
  const handleAIChatClick = (event) => {
    event.stopPropagation();
    if (onAIChatClick) {
      onAIChatClick();
    }
  };

  const handleTextClick = (event) => {
    event.stopPropagation();
    if (onTextClick) {
      onTextClick();
    }
  };

  const handleDocumentClick = (event) => {
    event.stopPropagation();
    if (onDocumentClick) {
      onDocumentClick();
    }
  };

  const handleImageClick = (event) => {
    event.stopPropagation();
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleGlobeClick = (event) => {
    event.stopPropagation();
    if (onGlobeClick) {
      onGlobeClick();
    }
  };

  const handleYouTubeClick = (event) => {
    event.stopPropagation();
    if (onYouTubeClick) {
      onYouTubeClick();
    }
  };

  const handleCodeClick = (event) => {
    event.stopPropagation();
    if (onCodeClick) {
      onCodeClick();
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && onImageClick) {
      // Check if file is an image
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          onImageClick(e.target.result);
        };
        reader.readAsDataURL(file);
      } else {
        alert('Please select a valid image file (JPEG, JPG, PNG, or WebP)');
      }
    }
    // Reset the input value so the same file can be selected again
    event.target.value = '';
  };

  const handleUndoClick = (event) => {
    event.stopPropagation();
    if (onUndoClick) {
      onUndoClick();
    }
  };

  const handleRedoClick = (event) => {
    event.stopPropagation();
    if (onRedoClick) {
      onRedoClick();
    }
  };
  return (
    <div className="fixed right-4 top-1/2 transform -translate-y-1/2 z-[9999] flex flex-col gap-3 bg-white/10 backdrop-blur-sm rounded-lg p-3 border border-white/20">
      <Button 
        size="icon" 
        variant="ghost" 
        className="text-white hover:bg-white/20"
        onClick={handleTextClick}
      >
        <span className="text-lg" style={{ fontFamily: 'Playfair Display, serif', fontWeight: '400' }}>T</span>
      </Button>
      
      <Button 
        size="icon" 
        variant="ghost" 
        className="text-white hover:bg-white/20"
        onClick={handleDocumentClick}
      >
        <FileText className="h-4 w-4" />
      </Button>
      
      <Button 
        size="icon" 
        variant="ghost" 
        className="text-white hover:bg-white/20"
        onClick={handleImageClick}
      >
        <Image className="h-4 w-4" />
      </Button>
      
      <Button 
        size="icon" 
        variant="ghost" 
        className="text-white hover:bg-white/20"
        onClick={handleGlobeClick}
      >
        <Globe className="h-4 w-4" />
      </Button>
      
      <Button 
        size="icon" 
        variant="ghost" 
        className="text-white hover:bg-white/20"
        onClick={handleYouTubeClick}
      >
        <Youtube className="h-4 w-4" />
      </Button>
      
      <div className="relative">
        <button 
          className="w-10 h-10 flex items-center justify-center text-white hover:bg-white/20 relative rounded-md border border-transparent hover:border-white/20"
          onClick={handleAIChatClick}
        >
          <MessageCircle className="h-4 w-4" />
          <span 
            className="absolute inset-0 flex items-center justify-center text-[8px] font-bold text-white leading-none pointer-events-none" 
            style={{
              textShadow: '0 0 5px #00ffcc, 0 0 10px #00ffcc, 0 0 20px #00ffcc',
              animation: 'constant-glow 2s infinite alternate'
            }}
          >
            AI
          </span>
        </button>
      </div>
      
      <Button 
        size="icon" 
        variant="ghost" 
        className="text-white hover:bg-white/20"
        onClick={handleCodeClick}
      >
        <SquareCode className="h-4 w-4" />
      </Button>
      
      <Button size="icon" variant="ghost" className="text-white hover:bg-white/20">
        <Folder className="h-4 w-4" />
      </Button>
      
      <div className="h-px bg-white/20 my-2" />
      
      <Button 
        size="icon" 
        variant="ghost" 
        className="text-white hover:bg-white/20"
        onClick={handleUndoClick}
      >
        <Undo className="h-4 w-4" />
      </Button>
      
      <Button 
        size="icon" 
        variant="ghost" 
        className="text-white hover:bg-white/20"
        onClick={handleRedoClick}
      >
        <Redo className="h-4 w-4" />
      </Button>

      {/* Hidden file input for image selection */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/jpg,image/png,image/webp"
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
    </div>
  );
};

export default Toolbar;

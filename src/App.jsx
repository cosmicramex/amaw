import React, { useRef, useCallback, useState } from 'react'
import CanvasComponentWrapper from './components/CanvasComponent'
import Toolbar from './components/Toolbar'
import YouTubeModal from './components/YouTubeModal'

function App() {
  const addAIChatNodeRef = useRef(null);
  const addTextNodeRef = useRef(null);
  const addDocumentNodeRef = useRef(null);
  const addImageNodeRef = useRef(null);
  const addWebsiteNodeRef = useRef(null);
  const addYouTubeNodeRef = useRef(null);
  const addCodeNodeRef = useRef(null);
  const undoRef = useRef(null);
  const redoRef = useRef(null);
  const [isYouTubeModalOpen, setIsYouTubeModalOpen] = useState(false);

  const handleAddAIChatNode = (addAIChatNodeFn) => {
    addAIChatNodeRef.current = addAIChatNodeFn;
  };

  const handleAddTextNode = (addTextNodeFn) => {
    addTextNodeRef.current = addTextNodeFn;
  };

  const handleAddDocumentNode = (addDocumentNodeFn) => {
    addDocumentNodeRef.current = addDocumentNodeFn;
  };

  const handleAddImageNode = (addImageNodeFn) => {
    addImageNodeRef.current = addImageNodeFn;
  };

  const handleAddWebsiteNode = (addWebsiteNodeFn) => {
    addWebsiteNodeRef.current = addWebsiteNodeFn;
  };

  const handleAddYouTubeNode = (addYouTubeNodeFn) => {
    addYouTubeNodeRef.current = addYouTubeNodeFn;
  };

  const handleAddCodeNode = (addCodeNodeFn) => {
    addCodeNodeRef.current = addCodeNodeFn;
  };

  const handleUndo = (undoFn) => {
    undoRef.current = undoFn;
  };

  const handleRedo = (redoFn) => {
    redoRef.current = redoFn;
  };

  const onAIChatClick = useCallback(() => {
    if (addAIChatNodeRef.current) {
      addAIChatNodeRef.current();
    }
  }, []);

  const onTextClick = useCallback(() => {
    if (addTextNodeRef.current) {
      addTextNodeRef.current();
    }
  }, []);

  const onDocumentClick = useCallback(() => {
    if (addDocumentNodeRef.current) {
      addDocumentNodeRef.current();
    }
  }, []);

  const onImageClick = useCallback((imageSrc) => {
    if (addImageNodeRef.current) {
      addImageNodeRef.current(imageSrc);
    }
  }, []);

  const onGlobeClick = useCallback(() => {
    if (addWebsiteNodeRef.current) {
      addWebsiteNodeRef.current();
    }
  }, []);

  const onYouTubeClick = useCallback(() => {
    setIsYouTubeModalOpen(true);
  }, []);

  const handleAddVideo = useCallback((videoData) => {
    if (addYouTubeNodeRef.current) {
      addYouTubeNodeRef.current(videoData);
    }
    setIsYouTubeModalOpen(false);
  }, []);

  const onCodeClick = useCallback(() => {
    if (addCodeNodeRef.current) {
      addCodeNodeRef.current();
    }
  }, []);

  const onUndoClick = useCallback(() => {
    if (undoRef.current) {
      undoRef.current();
    }
  }, []);

  const onRedoClick = useCallback(() => {
    if (redoRef.current) {
      redoRef.current();
    }
  }, []);

  return (
    <div className="w-screen h-screen">
      <CanvasComponentWrapper 
        onAddAIChatNode={handleAddAIChatNode} 
        onAddTextNode={handleAddTextNode}
        onAddDocumentNode={handleAddDocumentNode}
        onAddImageNode={handleAddImageNode}
        onAddWebsiteNode={handleAddWebsiteNode}
        onAddYouTubeNode={handleAddYouTubeNode}
        onAddCodeNode={handleAddCodeNode}
        onUndo={handleUndo}
        onRedo={handleRedo}
      />
      <Toolbar 
        onAIChatClick={onAIChatClick} 
        onTextClick={onTextClick}
        onDocumentClick={onDocumentClick}
        onImageClick={onImageClick}
        onGlobeClick={onGlobeClick}
        onYouTubeClick={onYouTubeClick}
        onCodeClick={onCodeClick}
        onUndoClick={onUndoClick}
        onRedoClick={onRedoClick}
      />
      
      {/* YouTube Modal */}
      <YouTubeModal
        isOpen={isYouTubeModalOpen}
        onClose={() => setIsYouTubeModalOpen(false)}
        onAddVideo={handleAddVideo}
      />
    </div>
  )
}

export default App

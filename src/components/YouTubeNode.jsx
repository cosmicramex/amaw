import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { X, Youtube, Play } from 'lucide-react';
import { Button } from './ui/button';

const YouTubeNode = ({ id, data, isConnectable }) => {
  const { videoData } = data;

  const handleOpenVideo = () => {
    if (videoData?.video_id) {
      window.open(`https://www.youtube.com/watch?v=${videoData.video_id}`, '_blank');
    }
  };

  return (
    <div 
      className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20 shadow-lg relative" 
      style={{ minWidth: '320px', maxWidth: '360px' }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <Youtube className="h-5 w-5 icon-glow-youtube" />
          <h3 className="font-medium text-sm glow-text-youtube">YOUTUBE</h3>
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

      {/* Video Content */}
      {videoData && (
        <div className="space-y-3">
          {/* Video Title (single line with ellipsis) */}
          <h4 className="text-white text-sm font-medium leading-tight truncate">
            {videoData.title}
          </h4>
          
          {/* Video Thumbnail */}
          <div className="relative group cursor-pointer" onClick={handleOpenVideo}>
            <img 
              src={videoData.thumbnail_url} 
              alt={videoData.title}
              className="w-full aspect-video object-contain rounded-lg border border-white/20 bg-black/20"
            />
            {/* Play Button Overlay */}
            <div className="absolute inset-0 flex items-center justify-center bg-black/20 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="bg-red-600 rounded-full p-2">
                <Play className="h-6 w-6 text-white fill-white" />
              </div>
            </div>
          </div>
          
          {/* Video Info */}
          <div className="flex items-center justify-center text-xs text-white/60">
            <span className="truncate">{videoData.channel_title}</span>
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

export default YouTubeNode;

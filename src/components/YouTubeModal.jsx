import React, { useState, useRef, useEffect } from 'react';
import { X, Youtube, Loader2 } from 'lucide-react';
import { Button } from './ui/button';

const YouTubeModal = ({ isOpen, onClose, onAddVideo }) => {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isAnimating, setIsAnimating] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      setIsAnimating(true);
      if (inputRef.current) {
        inputRef.current.focus();
      }
    } else {
      setIsAnimating(false);
    }
  }, [isOpen]);

  const handleUrlChange = (e) => {
    setUrl(e.target.value);
    setError('');
  };

  const extractVideoId = (url) => {
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
      /youtube\.com\/watch\?.*v=([^&\n?#]+)/,
    ];
    
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) {
        return match[1];
      }
    }
    return null;
  };

  const isValidYouTubeUrl = (string) => {
    return extractVideoId(string) !== null;
  };

  const handleAddToBoard = async () => {
    if (!url || !isValidYouTubeUrl(url)) {
      setError('Please enter a valid YouTube URL');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      const videoId = extractVideoId(url);
      
      // Try backend API first, fallback to direct API call
      let videoData;
      
      try {
        // Call our backend API to get video data
        console.log('Calling backend API for video:', videoId);
        const response = await fetch(`http://localhost:8001/api/youtube/video/${videoId}`);
        console.log('Backend response status:', response.status);
        const result = await response.json();
        console.log('Backend API result:', result);
        
        if (response.ok && result.success) {
          const video = result.data;
          
          // Format view count
          const viewCount = parseInt(video.view_count || 0);
          const formattedViewCount = viewCount >= 1000000 
            ? `${(viewCount / 1000000).toFixed(1)}M`
            : viewCount >= 1000 
            ? `${(viewCount / 1000).toFixed(1)}K`
            : viewCount.toString();
          
          videoData = {
            video_id: videoId,
            title: video.title || 'Unknown Title',
            thumbnail_url: `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`,
            channel_title: video.channel_title || 'Unknown Channel',
            view_count: formattedViewCount,
            duration: video.duration || "Unknown",
            description: video.description || '',
            published_at: video.published_at
          };
        } else {
          throw new Error('Backend API failed');
        }
      } catch (backendError) {
        console.log('Backend API failed, using fallback method');
        
        // Fallback: Use YouTube's oEmbed API (no API key required)
        const oembedUrl = `https://www.youtube.com/oembed?url=${encodeURIComponent(url)}&format=json`;
        const oembedResponse = await fetch(oembedUrl);
        const oembedData = await oembedResponse.json();
        
        if (oembedResponse.ok) {
          videoData = {
            video_id: videoId,
            title: oembedData.title || 'Unknown Title',
            thumbnail_url: `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`,
            channel_title: oembedData.author_name || 'Unknown Channel',
            view_count: 'Unknown',
            duration: "Unknown",
            description: '',
            published_at: null
          };
        } else {
          throw new Error('Failed to fetch video data from both backend and oEmbed');
        }
      }
      
      // Call the parent function to add the video node
      onAddVideo(videoData);
      
      // Close modal and reset
      setUrl('');
      onClose();
      
    } catch (err) {
      setError('Failed to fetch video details. Please check the URL and try again.');
      console.error('Error fetching video details:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddToBoard();
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className={`fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[10000] modal-overlay ${isAnimating ? 'show' : ''}`}
      onClick={onClose}
    >
      <div 
        className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 shadow-2xl w-full max-w-lg mx-4 modal-content"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Youtube className="h-6 w-6 icon-glow-youtube" />
            <h2 className="text-xl font-semibold text-white">
              Add YouTube Video
            </h2>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0 hover:bg-white/20 text-white/70"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* URL Input */}
        <div className="mb-6">
          <label className="block text-white/80 text-sm font-medium mb-2">
            YouTube URL
          </label>
          <input
            ref={inputRef}
            type="text"
            value={url}
            onChange={handleUrlChange}
            onKeyDown={handleKeyDown}
            placeholder="Paste your content link here..."
            className="w-full px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500/50 transition-all"
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="text-red-400 text-sm text-center mb-4 bg-red-500/20 border border-red-500/30 rounded-lg p-3">
            {error}
          </div>
        )}

        {/* Buttons */}
        <div className="flex space-x-3">
          <Button
            variant="ghost"
            onClick={onClose}
            className="flex-1 bg-white/10 hover:bg-white/20 text-white border border-white/20"
          >
            Cancel
          </Button>
          <Button
            onClick={handleAddToBoard}
            disabled={!url || !isValidYouTubeUrl(url) || isLoading}
            className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-500 disabled:cursor-not-allowed text-white"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Adding...
              </>
            ) : (
              'Add to Board'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default YouTubeModal;

import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { videoApi } from '../api/axios';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import './VideoPlayer.css';

const VideoPlayer = () => {
  const { id } = useParams();
  const [video, setVideo] = useState(null);
  const [streamingUrl, setStreamingUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const videoRef = useRef(null);
  const playerRef = useRef(null);

  useEffect(() => {
    fetchVideo();
    return () => {
      if (playerRef.current) {
        playerRef.current.dispose();
      }
    };
  }, [id]);

  const fetchVideo = async () => {
    try {
      const [videoResponse, tokenResponse] = await Promise.all([
        videoApi.get(`/api/videos/${id}`),
        videoApi.get(`/api/stream/token/${id}`)
      ]);

      setVideo(videoResponse.data);
      setStreamingUrl(tokenResponse.data.hls_url);
      setLoading(false);

      // Initialize video player after getting streaming URL
      setTimeout(() => initPlayer(tokenResponse.data.hls_url), 100);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load video');
      setLoading(false);
    }
  };

  const initPlayer = (url) => {
    if (videoRef.current && !playerRef.current) {
      console.log('Initializing Video.js with URL:', url);
      
      playerRef.current = videojs(videoRef.current, {
        controls: true,
        autoplay: false,
        preload: 'auto',
        fluid: true,
        html5: {
          vhs: {
            overrideNative: true
          },
          nativeAudioTracks: false,
          nativeVideoTracks: false
        },
        sources: [{
          src: url,
          type: 'application/x-mpegURL'
        }]
      });

      // Error handling
      playerRef.current.on('error', (e) => {
        const error = playerRef.current.error();
        console.error('Video.js error:', error);
        setError(`Video playback error: ${error?.message || 'Unknown error'}`);
      });

      // Track watch progress
      playerRef.current.on('timeupdate', () => {
        const currentTime = playerRef.current.currentTime();
        if (currentTime > 0 && currentTime % 10 === 0) {
          updateWatchProgress(currentTime);
        }
      });

      playerRef.current.on('loadedmetadata', () => {
        console.log('Video metadata loaded successfully');
      });
    }
  };

  const updateWatchProgress = async (watchTime) => {
    try {
      await videoApi.post('/api/stream/progress', {
        video_id: parseInt(id),
        watch_time: Math.floor(watchTime),
        completed: false
      });
    } catch (err) {
      console.error('Failed to update watch progress', err);
    }
  };

  if (loading) {
    return <div className="loading">Loading video...</div>;
  }

  if (error) {
    return <div className="container"><p className="error-message">{error}</p></div>;
  }

  return (
    <div className="video-player-page">
      <div className="player-container">
        <div data-vjs-player>
          <video ref={videoRef} className="video-js vjs-big-play-centered" />
        </div>
      </div>

      <div className="video-details">
        <h1 className="video-title-large">{video.title}</h1>
        
        <div className="video-stats">
          <span>{video.views_count} views</span>
          <span> • </span>
          <span>{new Date(video.created_at).toLocaleDateString()}</span>
          <div className="video-actions">
            <button className="action-btn">
              👍 {video.likes_count}
            </button>
            <button className="action-btn">
              👎 {video.dislikes_count}
            </button>
          </div>
        </div>

        <div className="video-description">
          <p>{video.description}</p>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer;

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api, videoApi } from '../api/axios';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import './VideoPlayer.css';

const VideoPlayer = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [video, setVideo] = useState(null);
  const [relatedVideos, setRelatedVideos] = useState([]);
  const [streamingUrl, setStreamingUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [descriptionExpanded, setDescriptionExpanded] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [comments, setComments] = useState([]);
  const [userLikeStatus, setUserLikeStatus] = useState(null); // null, 'like', or 'dislike'
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [subscriptionId, setSubscriptionId] = useState(null);
  const videoRef = useRef(null);
  const playerRef = useRef(null);

  useEffect(() => {
    // Cleanup previous player
    if (playerRef.current) {
      playerRef.current.dispose();
      playerRef.current = null;
    }
    
    // Reset state
    setLoading(true);
    setError('');
    
    // Fetch new video
    fetchVideo();
    fetchRelatedVideos();
    fetchComments();
    
    return () => {
      if (playerRef.current) {
        playerRef.current.dispose();
        playerRef.current = null;
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
      
      // Check subscription status after video is loaded
      checkSubscriptionStatus(videoResponse.data.creator_id);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load video');
      setLoading(false);
    }
  };

  const fetchRelatedVideos = async () => {
    try {
      const response = await videoApi.get('/api/videos');
      console.log('All videos:', response.data);
      // API returns { total, page, page_size, videos: [] }
      const allVideos = response.data.videos || [];
      // Filter out current video
      const filtered = allVideos.filter(v => v.id !== parseInt(id));
      console.log('Filtered related videos:', filtered);
      setRelatedVideos(filtered);
    } catch (err) {
      console.error('Failed to fetch related videos', err);
    }
  };

  const initPlayer = (url) => {
    if (videoRef.current && !playerRef.current) {
      console.log('Initializing Video.js with URL:', url);
      
      playerRef.current = videojs(videoRef.current, {
        controls: true,
        autoplay: false,
        preload: 'auto',
        responsive: true,
        aspectRatio: '16:9',
        fill: false,
        controlBar: {
          children: [
            'playToggle',
            'volumePanel',
            'currentTimeDisplay',
            'timeDivider',
            'durationDisplay',
            'progressControl',
            'playbackRateMenuButton',
            'pictureInPictureToggle',
            'fullscreenToggle'
          ],
          volumePanel: {
            inline: true,
            vertical: false
          }
        },
        playbackRates: [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2],
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

      // Track watch progress - save every 10 seconds when playing
      let progressInterval;
      
      playerRef.current.on('play', () => {
        if (progressInterval) clearInterval(progressInterval);
        progressInterval = setInterval(() => {
          if (playerRef.current && !playerRef.current.paused()) {
            const currentTime = Math.floor(playerRef.current.currentTime());
            const duration = Math.floor(playerRef.current.duration());
            const completed = duration > 0 && currentTime >= duration - 5;
            updateWatchProgress(currentTime, completed);
          }
        }, 10000); // Save every 10 seconds
      });

      playerRef.current.on('pause', () => {
        if (progressInterval) {
          clearInterval(progressInterval);
          progressInterval = null;
        }
        // Save progress when paused
        const currentTime = Math.floor(playerRef.current.currentTime());
        const duration = Math.floor(playerRef.current.duration());
        const completed = duration > 0 && currentTime >= duration - 5;
        updateWatchProgress(currentTime, completed);
      });

      playerRef.current.on('ended', () => {
        if (progressInterval) {
          clearInterval(progressInterval);
          progressInterval = null;
        }
        // Mark as completed when video ends
        const duration = Math.floor(playerRef.current.duration());
        updateWatchProgress(duration, true);
      });

      // Cleanup interval on player disposal
      playerRef.current.on('dispose', () => {
        if (progressInterval) {
          clearInterval(progressInterval);
          progressInterval = null;
        }
      });

      playerRef.current.on('loadedmetadata', () => {
        console.log('Video metadata loaded successfully');
      });
    }
  };

  const updateWatchProgress = async (watchTime, completed = false) => {
    try {
      await videoApi.post('/api/stream/progress', {
        video_id: parseInt(id),
        watch_time: Math.floor(watchTime),
        completed: completed
      });
      console.log(`Watch progress saved: ${Math.floor(watchTime)}s, completed: ${completed}`);
    } catch (err) {
      console.error('Failed to save watch progress:', err);
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatViewCount = (count) => {
    if (!count) return '0';
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
    return count.toString();
  };

  const getTimeAgo = (dateString) => {
    const now = new Date();
    const past = new Date(dateString);
    const diffMs = now - past;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    const diffMonths = Math.floor(diffMs / 2592000000);
    const diffYears = Math.floor(diffMs / 31536000000);

    if (diffYears > 0) return `${diffYears} year${diffYears > 1 ? 's' : ''} ago`;
    if (diffMonths > 0) return `${diffMonths} month${diffMonths > 1 ? 's' : ''} ago`;
    if (diffDays > 0) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    if (diffHours > 0) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffMins > 0) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    return 'Just now';
  };

  const getThumbnailUrl = (video) => {
    if (video.thumbnail) {
      return `http://localhost:8080/${video.thumbnail}`;
    }
    return null;
  };

  const handleVideoClick = (videoId) => {
    navigate(`/video/${videoId}`);
  };

  const fetchComments = async () => {
    try {
      const response = await api.get(`/api/core/videos/${id}/comments/`);
      // Handle both array and paginated response
      const commentsData = Array.isArray(response.data) 
        ? response.data 
        : (response.data?.results || []);
      setComments(commentsData);
      console.log('Comments loaded:', commentsData.length);
    } catch (err) {
      console.error('Failed to fetch comments:', err);
      // If unauthorized or error, just show empty comments
      setComments([]);
    }
  };

  const fetchSubscriptionStatus = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const response = await api.get('/api/auth/subscriptions/');
      const subscriptions = response.data;
      // Wait for video to be loaded
      if (!video) return;
      
      const subscription = subscriptions.find(sub => sub.creator.id === video.creator_id);
      if (subscription) {
        setIsSubscribed(true);
        setSubscriptionId(subscription.id);
      } else {
        setIsSubscribed(false);
        setSubscriptionId(null);
      }
    } catch (err) {
      console.error('Failed to fetch subscription status:', err);
    }
  };

  const checkSubscriptionStatus = async (creatorId) => {
    const token = localStorage.getItem('access_token');
    if (!token || !creatorId) return;

    try {
      const response = await api.get('/api/auth/subscriptions/');
      const subscriptions = response.data;
      const subscription = subscriptions.find(sub => sub.creator.id === creatorId);
      if (subscription) {
        setIsSubscribed(true);
        setSubscriptionId(subscription.id);
      } else {
        setIsSubscribed(false);
        setSubscriptionId(null);
      }
    } catch (err) {
      console.error('Failed to fetch subscription status:', err);
    }
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (newComment.trim()) {
      // Check if user is logged in
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('Please login to comment');
        return;
      }
      
      try {
        await api.post(`/api/core/videos/${id}/comments/`, {
          video: parseInt(id),
          parent: null,
          content: newComment
        });
        setNewComment('');
        fetchComments(); // Reload comments from backend
      } catch (err) {
        console.error('Failed to post comment:', err);
        alert('Failed to post comment. Please try again.');
      }
    }
  };

  const handleLike = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('Please login to like videos');
      return;
    }

    try {
      await api.post('/api/core/likes/', {
        video: parseInt(id),
        like_type: 'like'
      });
      
      // Update local state
      if (userLikeStatus === 'like') {
        setUserLikeStatus(null);
        setVideo(prev => ({ ...prev, likes_count: prev.likes_count - 1 }));
      } else {
        if (userLikeStatus === 'dislike') {
          setVideo(prev => ({ ...prev, dislikes_count: prev.dislikes_count - 1 }));
        }
        setUserLikeStatus('like');
        setVideo(prev => ({ ...prev, likes_count: prev.likes_count + 1 }));
      }
    } catch (err) {
      console.error('Failed to like video:', err);
    }
  };

  const handleDislike = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('Please login to dislike videos');
      return;
    }

    try {
      await api.post('/api/core/likes/', {
        video: parseInt(id),
        like_type: 'dislike'
      });
      
      // Update local state
      if (userLikeStatus === 'dislike') {
        setUserLikeStatus(null);
        setVideo(prev => ({ ...prev, dislikes_count: prev.dislikes_count - 1 }));
      } else {
        if (userLikeStatus === 'like') {
          setVideo(prev => ({ ...prev, likes_count: prev.likes_count - 1 }));
        }
        setUserLikeStatus('dislike');
        setVideo(prev => ({ ...prev, dislikes_count: prev.dislikes_count + 1 }));
      }
    } catch (err) {
      console.error('Failed to dislike video:', err);
    }
  };

  const handleSubscribe = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('Please login to subscribe');
      return;
    }

    if (!video?.creator_id) {
      alert('Video creator information not available');
      return;
    }

    try {
      if (isSubscribed && subscriptionId) {
        // Unsubscribe
        await api.delete(`/api/auth/subscriptions/${subscriptionId}/`);
        setIsSubscribed(false);
        setSubscriptionId(null);
      } else {
        // Subscribe
        const response = await api.post('/api/auth/subscriptions/', {
          creator_id: video.creator_id
        });
        setIsSubscribed(true);
        setSubscriptionId(response.data.id);
      }
    } catch (err) {
      console.error('Failed to toggle subscription:', err);
      const errorMsg = err.response?.data?.creator_id?.[0] || err.response?.data?.detail || 'Failed to update subscription. Please try again.';
      alert(errorMsg);
    }
  };

  const toggleDescription = () => {
    setDescriptionExpanded(!descriptionExpanded);
  };

  if (loading) {
    return <div className="loading">Loading video...</div>;
  }

  if (error) {
    return <div className="container"><p className="error-message">{error}</p></div>;
  }

  return (
    <div className="video-player-page">
      <div className="primary-content">
        <div className="player-container">
          <div data-vjs-player>
            <video ref={videoRef} className="video-js vjs-big-play-centered" />
          </div>
        </div>

        <div className="video-info">
          <h1 className="video-title-large">{video.title}</h1>
          
          <div className="video-metadata">
            <div className="video-stats">
              <span>{formatViewCount(video.views_count)} views</span>
              <span> • </span>
              <span>{getTimeAgo(video.created_at)}</span>
            </div>
            
            <div className="video-actions">
              <button 
                className={`action-btn ${userLikeStatus === 'like' ? 'active' : ''}`}
                onClick={handleLike}
              >
                <span className="action-icon">👍</span>
                <span>{formatViewCount(video.likes_count)}</span>
              </button>
              <button 
                className={`action-btn ${userLikeStatus === 'dislike' ? 'active' : ''}`}
                onClick={handleDislike}
              >
                <span className="action-icon">👎</span>
                <span>{formatViewCount(video.dislikes_count)}</span>
              </button>
              <button className="action-btn">
                <span className="action-icon">↗️</span>
                <span>Share</span>
              </button>
              <button className="action-btn">
                <span className="action-icon">💾</span>
                <span>Save</span>
              </button>
            </div>
          </div>

          <div className="channel-info">
            <div className="channel-avatar">
              <div className="avatar-placeholder">
                {video.title?.charAt(0).toUpperCase() || 'V'}
              </div>
            </div>
            <div className="channel-details">
              <h3 className="channel-name">Video Channel</h3>
              <p className="channel-subscribers">1.2M subscribers</p>
            </div>
            <button 
              className={`subscribe-btn ${isSubscribed ? 'subscribed' : ''}`}
              onClick={handleSubscribe}
            >
              {isSubscribed ? 'Subscribed' : 'Subscribe'}
            </button>
          </div>

          <div className="video-description">
            <p className={descriptionExpanded ? 'description-expanded' : 'description-collapsed'}>
              {video.description}
            </p>
            <button className="description-toggle" onClick={toggleDescription}>
              {descriptionExpanded ? 'Show less' : 'Show more'}
            </button>
          </div>

          {/* Comments Section */}
          <div className="comments-section">
            <h3 className="comments-header">{comments.length} Comments</h3>
            
            <form className="comment-form" onSubmit={handleCommentSubmit}>
              <div className="comment-input-container">
                <div className="comment-avatar">CU</div>
                <input
                  type="text"
                  className="comment-input"
                  placeholder="Add a comment..."
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                />
              </div>
              {newComment && (
                <div className="comment-actions">
                  <button type="button" className="comment-cancel" onClick={() => setNewComment('')}>
                    Cancel
                  </button>
                  <button type="submit" className="comment-submit">
                    Comment
                  </button>
                </div>
              )}
            </form>

            <div className="comments-list">
              {comments.map(comment => (
                <div key={comment.id} className="comment">
                  <div className="comment-avatar">
                    {comment.user_name ? comment.user_name.charAt(0).toUpperCase() : 'U'}
                  </div>
                  <div className="comment-content">
                    <div className="comment-header">
                      <span className="comment-author">{comment.user_name || comment.user_email || 'User'}</span>
                      <span className="comment-time">{getTimeAgo(comment.created_at)}</span>
                    </div>
                    <p className="comment-text">{comment.content}</p>
                    <div className="comment-footer">
                      <button className="comment-like-btn">
                        <span>👍</span>
                        {comment.likes_count > 0 && <span>{comment.likes_count}</span>}
                      </button>
                      <button className="comment-dislike-btn">
                        <span>👎</span>
                      </button>
                      <button className="comment-reply-btn">Reply</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="secondary-content">
        <h3 className="sidebar-title">Recommended</h3>
        <p style={{color: '#fff', padding: '10px'}}>Total related videos: {relatedVideos.length}</p>
        <div className="related-videos">
          {relatedVideos.length === 0 ? (
            <p style={{color: '#aaa', padding: '20px'}}>No related videos found</p>
          ) : (
            relatedVideos.map(relVideo => (
              <div 
                key={relVideo.id} 
                className="related-video-card"
                onClick={() => handleVideoClick(relVideo.id)}
              >
                <div className="related-thumbnail-container">
                  {getThumbnailUrl(relVideo) ? (
                    <img 
                      src={getThumbnailUrl(relVideo)} 
                      alt={relVideo.title}
                      className="related-thumbnail"
                    />
                  ) : (
                    <div className="related-thumbnail-placeholder">
                      <span className="play-icon">▶</span>
                    </div>
                  )}
                  {relVideo.duration && (
                    <span className="related-duration">{formatDuration(relVideo.duration)}</span>
                  )}
                </div>
                
                <div className="related-video-info">
                  <h4 className="related-video-title">{relVideo.title}</h4>
                  <p className="related-channel-name">Video Channel</p>
                  <div className="related-video-stats">
                    <span>{formatViewCount(relVideo.views_count)} views</span>
                    <span> • </span>
                    <span>{getTimeAgo(relVideo.created_at)}</span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer;
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { videoApi } from '../api/axios';
import './Home.css';

const Home = () => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all'); // all, recent, popular

  useEffect(() => {
    fetchVideos();
  }, [filter]);

  const fetchVideos = async () => {
    try {
      setLoading(true);
      const response = await videoApi.get('/api/videos/');
      let sortedVideos = response.data.videos;
      
      // Sort based on filter
      if (filter === 'recent') {
        sortedVideos = sortedVideos.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      } else if (filter === 'popular') {
        sortedVideos = sortedVideos.sort((a, b) => b.views_count - a.views_count);
      }
      
      setVideos(sortedVideos);
    } catch (err) {
      setError('Failed to load videos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getThumbnailUrl = (video) => {
    if (video.thumbnail) {
      const url = `http://localhost:8080/${video.thumbnail}`;
      console.log(`Thumbnail URL for video ${video.id}:`, url);
      return url;
    }
    // Generate a colored placeholder based on video ID
    return null;
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const formatViewCount = (count) => {
    if (count >= 1000000) {
      return (count / 1000000).toFixed(1) + 'M';
    } else if (count >= 1000) {
      return (count / 1000).toFixed(1) + 'K';
    }
    return count;
  };

  const getTimeAgo = (date) => {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    
    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + ' years ago';
    
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + ' months ago';
    
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + ' days ago';
    
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + ' hours ago';
    
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + ' minutes ago';
    
    return Math.floor(seconds) + ' seconds ago';
  };

  if (loading && videos.length === 0) {
    return (
      <div className="explore-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading videos...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="explore-page">
      <div className="explore-header">
        <h1 className="explore-title">Explore</h1>
        <div className="filter-buttons">
          <button 
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button 
            className={`filter-btn ${filter === 'recent' ? 'active' : ''}`}
            onClick={() => setFilter('recent')}
          >
            Recent
          </button>
          <button 
            className={`filter-btn ${filter === 'popular' ? 'active' : ''}`}
            onClick={() => setFilter('popular')}
          >
            Popular
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {videos.length === 0 && !loading ? (
        <div className="no-videos">
          <p>No videos available yet. Be the first to upload!</p>
          <Link to="/upload" className="upload-btn-link">Upload Video</Link>
        </div>
      ) : (
        <div className="video-grid">
          {videos.map((video) => (
            <Link to={`/video/${video.id}`} key={video.id} className="video-card">
              <div className="thumbnail-container">
                {getThumbnailUrl(video) ? (
                  <img
                    src={getThumbnailUrl(video)}
                    alt={video.title}
                    className="video-thumbnail"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div className="thumbnail-placeholder" style={{ display: getThumbnailUrl(video) ? 'none' : 'flex' }}>
                  <div className="placeholder-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/>
                    </svg>
                  </div>
                  <div className="placeholder-title">{video.title.substring(0, 1).toUpperCase()}</div>
                </div>
                {video.duration && (
                  <div className="duration-badge">
                    {formatDuration(video.duration)}
                  </div>
                )}
                {video.status === 'processing' && (
                  <div className="processing-badge">Processing...</div>
                )}
              </div>
              
              <div className="video-info">
                <h3 className="video-title" title={video.title}>
                  {video.title}
                </h3>
                
                <div className="video-meta">
                  <span className="views">{formatViewCount(video.views_count)} views</span>
                  <span className="dot">•</span>
                  <span className="date">{getTimeAgo(video.created_at)}</span>
                </div>
                
                {video.creator_name && (
                  <div className="creator-info">
                    <span className="creator-name">{video.creator_name}</span>
                  </div>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default Home;

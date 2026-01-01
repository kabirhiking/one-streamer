import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { videoApi } from '../api/axios';
import './Search.css';

const Search = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const query = searchParams.get('q') || '';
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('recent');
  const [total, setTotal] = useState(0);

  useEffect(() => {
    if (query) {
      searchVideos();
    }
  }, [query, sortBy]);

  const searchVideos = async () => {
    setLoading(true);
    try {
      const response = await videoApi.get('/api/videos', {
        params: {
          search: query,
          sort_by: sortBy,
          page_size: 50
        }
      });
      setVideos(response.data.videos || []);
      setTotal(response.data.total || 0);
    } catch (err) {
      console.error('Search failed:', err);
      setVideos([]);
    } finally {
      setLoading(false);
    }
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

  const handleVideoClick = (videoId) => {
    navigate(`/video/${videoId}`);
  };

  return (
    <div className="search-page">
      <div className="search-header">
        <h2>Search results for "{query}"</h2>
        <p className="search-count">{total} {total === 1 ? 'result' : 'results'} found</p>
        
        <div className="search-filters">
          <label>Sort by:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="sort-select">
            <option value="recent">Recent</option>
            <option value="views">Most viewed</option>
            <option value="likes">Most liked</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading">Searching...</div>
      ) : videos.length === 0 ? (
        <div className="no-results">
          <svg width="120" height="120" viewBox="0 0 24 24" fill="none">
            <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <h3>No videos found</h3>
          <p>Try different keywords or check your spelling</p>
        </div>
      ) : (
        <div className="search-results">
          {videos.map(video => (
            <div 
              key={video.id} 
              className="search-result-item"
              onClick={() => handleVideoClick(video.id)}
            >
              <div className="result-thumbnail">
                {getThumbnailUrl(video) ? (
                  <img src={getThumbnailUrl(video)} alt={video.title} />
                ) : (
                  <div className="placeholder-thumbnail">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                      <path d="M14.7519 11.1679L11.5547 9.03647C10.8901 8.59343 10 9.06982 10 9.86852V14.1315C10 14.9302 10.8901 15.4066 11.5547 14.9635L14.7519 12.8321C15.3457 12.4362 15.3457 11.5638 14.7519 11.1679Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="1.5"/>
                    </svg>
                  </div>
                )}
                {video.duration > 0 && (
                  <span className="duration-badge">{formatDuration(video.duration)}</span>
                )}
              </div>

              <div className="result-details">
                <h3 className="result-title">{video.title}</h3>
                <div className="result-meta">
                  <span>{formatViewCount(video.views_count)} views</span>
                  <span> • </span>
                  <span>{getTimeAgo(video.created_at)}</span>
                </div>
                <p className="result-description">{video.description || 'No description'}</p>
                <div className="result-stats">
                  <span>👍 {formatViewCount(video.likes_count)}</span>
                  <span>💬 {formatViewCount(video.comments_count)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Search;

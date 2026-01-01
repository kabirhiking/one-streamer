import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { videoApi } from '../api/axios';
import './CreatorDashboard.css';

const CreatorDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState(null);
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (user && user.is_creator) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      const [analyticsRes, videosRes] = await Promise.all([
        videoApi.get('/api/analytics/creator'),
        videoApi.get('/api/videos', { params: { creator_id: user.id, page_size: 100 } })
      ]);
      setAnalytics(analyticsRes.data);
      setVideos(videosRes.data.videos || []);
    } catch (err) {
      console.error('Failed to fetch dashboard data', err);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (!num) return '0';
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hrs > 0) {
      return `${hrs}h ${mins}m`;
    }
    return `${mins}m ${secs}s`;
  };

  const getThumbnailUrl = (video) => {
    if (video.thumbnail) {
      return `http://localhost:8080/${video.thumbnail}`;
    }
    return null;
  };

  const getStatusBadge = (status) => {
    const badges = {
      'ready': { label: 'Published', className: 'status-published' },
      'processing': { label: 'Processing', className: 'status-processing' },
      'failed': { label: 'Failed', className: 'status-failed' },
      'draft': { label: 'Draft', className: 'status-draft' }
    };
    return badges[status] || { label: status, className: 'status-default' };
  };

  if (!user || !user.is_creator) {
    return (
      <div className="dashboard-container">
        <div className="not-creator">
          <svg width="120" height="120" viewBox="0 0 24 24" fill="none">
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 17C11.45 17 11 16.55 11 16V12C11 11.45 11.45 11 12 11C12.55 11 13 11.45 13 12V16C13 16.55 12.55 17 12 17ZM13 9H11V7H13V9Z" fill="currentColor"/>
          </svg>
          <h2>Creator Access Required</h2>
          <p>You need to be a creator to access the dashboard.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Creator Dashboard</h1>
          <p className="channel-name">{user.channel_name || user.display_name}</p>
        </div>
        <button className="btn-upload" onClick={() => navigate('/upload')}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M12 4V20M12 4L8 8M12 4L16 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M20 16V20H4V16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Upload Video
        </button>
      </div>

      <div className="dashboard-tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab ${activeTab === 'videos' ? 'active' : ''}`}
          onClick={() => setActiveTab('videos')}
        >
          My Videos ({videos.length})
        </button>
      </div>

      {activeTab === 'overview' && analytics && (
        <div className="overview-tab">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon subscribers">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13M16 3.13C16.8604 3.3503 17.623 3.8507 18.1676 4.55231C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89317 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88M13 7C13 9.20914 11.2091 11 9 11C6.79086 11 5 9.20914 5 7C5 4.79086 6.79086 3 9 3C11.2091 3 13 4.79086 13 7Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div className="stat-content">
                <p className="stat-label">Subscribers</p>
                <p className="stat-value">{formatNumber(user.subscribers_count)}</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon views">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M1 12C1 12 5 4 12 4C19 4 23 12 23 12C23 12 19 20 12 20C5 20 1 12 1 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div className="stat-content">
                <p className="stat-label">Total Views</p>
                <p className="stat-value">{formatNumber(analytics.total_views)}</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon likes">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M14 9V5C14 4.46957 13.7893 3.96086 13.4142 3.58579C13.0391 3.21071 12.5304 3 12 3C11.4696 3 10.9609 3.21071 10.5858 3.58579C10.2107 3.96086 10 4.46957 10 5V9L6 13V21H18.28C18.7623 21.0055 19.2304 20.8364 19.5979 20.524C19.9654 20.2116 20.2077 19.7769 20.28 19.3L21.66 11.3C21.7035 11.0134 21.6842 10.7207 21.6033 10.4423C21.5225 10.1638 21.3821 9.90629 21.1919 9.68751C21.0016 9.46873 20.7661 9.29393 20.5016 9.17522C20.2371 9.0565 19.9499 8.99672 19.66 9H14Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div className="stat-content">
                <p className="stat-label">Total Likes</p>
                <p className="stat-value">{formatNumber(analytics.total_likes)}</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon comments">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div className="stat-content">
                <p className="stat-label">Total Comments</p>
                <p className="stat-value">{formatNumber(analytics.total_comments)}</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon videos">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M23 7L16 12L23 17V7Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M14 5H3C1.89543 5 1 5.89543 1 7V17C1 18.1046 1.89543 19 3 19H14C15.1046 19 16 18.1046 16 17V7C16 5.89543 15.1046 5 14 5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div className="stat-content">
                <p className="stat-label">Total Videos</p>
                <p className="stat-value">{analytics.total_videos}</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon watch-time">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div className="stat-content">
                <p className="stat-label">Watch Time</p>
                <p className="stat-value">{formatDuration(analytics.total_watch_time)}</p>
              </div>
            </div>
          </div>

          <div className="recent-videos-section">
            <h2>Recent Videos</h2>
            {analytics.videos && analytics.videos.length > 0 ? (
              <div className="recent-videos-grid">
                {analytics.videos.slice(0, 5).map(video => (
                  <div key={video.id} className="recent-video-card" onClick={() => navigate(`/video/${video.id}`)}>
                    <h3>{video.title}</h3>
                    <div className="recent-video-stats">
                      <span>👁 {formatNumber(video.views)} views</span>
                      <span>👍 {formatNumber(video.likes)} likes</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-data">No videos yet. Upload your first video!</p>
            )}
          </div>
        </div>
      )}

      {activeTab === 'videos' && (
        <div className="videos-tab">
          {videos.length === 0 ? (
            <div className="empty-state">
              <svg width="120" height="120" viewBox="0 0 24 24" fill="none">
                <path d="M23 7L16 12L23 17V7Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M14 5H3C1.89543 5 1 5.89543 1 7V17C1 18.1046 1.89543 19 3 19H14C15.1046 19 16 18.1046 16 17V7C16 5.89543 15.1046 5 14 5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <h3>No videos yet</h3>
              <p>Upload your first video to get started</p>
              <button className="btn-primary" onClick={() => navigate('/upload')}>Upload Video</button>
            </div>
          ) : (
            <div className="videos-list">
              {videos.map(video => {
                const statusBadge = getStatusBadge(video.status);
                return (
                  <div key={video.id} className="video-row">
                    <div className="video-row-thumbnail" onClick={() => navigate(`/video/${video.id}`)}>
                      {getThumbnailUrl(video) ? (
                        <img src={getThumbnailUrl(video)} alt={video.title} />
                      ) : (
                        <div className="placeholder-thumb">
                          <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                            <path d="M14.7519 11.1679L11.5547 9.03647C10.8901 8.59343 10 9.06982 10 9.86852V14.1315C10 14.9302 10.8901 15.4066 11.5547 14.9635L14.7519 12.8321C15.3457 12.4362 15.3457 11.5638 14.7519 11.1679Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                            <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="1.5"/>
                          </svg>
                        </div>
                      )}
                    </div>

                    <div className="video-row-details">
                      <h3 onClick={() => navigate(`/video/${video.id}`)}>{video.title}</h3>
                      <p className="video-description">{video.description || 'No description'}</p>
                      <div className="video-row-meta">
                        <span className={`status-badge ${statusBadge.className}`}>{statusBadge.label}</span>
                        <span>{new Date(video.created_at).toLocaleDateString()}</span>
                        <span>•</span>
                        <span>{video.visibility}</span>
                      </div>
                    </div>

                    <div className="video-row-stats">
                      <div className="stat-item">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path d="M1 12C1 12 5 4 12 4C19 4 23 12 23 12C23 12 19 20 12 20C5 20 1 12 1 12Z" stroke="currentColor" strokeWidth="2"/>
                          <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2"/>
                        </svg>
                        <span>{formatNumber(video.views_count)}</span>
                      </div>
                      <div className="stat-item">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path d="M14 9V5C14 3.89543 13.1046 3 12 3C10.8954 3 10 3.89543 10 5V9L6 13V21H18.28C18.7623 21.0055 19.2304 20.8364 19.5979 20.524C19.9654 20.2116 20.2077 19.7769 20.28 19.3L21.66 11.3C21.7035 11.0134 21.6842 10.7207 21.6033 10.4423C21.5225 10.1638 21.3821 9.90629 21.1919 9.68751C21.0016 9.46873 20.7661 9.29393 20.5016 9.17522C20.2371 9.0565 19.9499 8.99672 19.66 9H14Z" stroke="currentColor" strokeWidth="2"/>
                        </svg>
                        <span>{formatNumber(video.likes_count)}</span>
                      </div>
                      <div className="stat-item">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" strokeWidth="2"/>
                        </svg>
                        <span>{formatNumber(video.comments_count)}</span>
                      </div>
                    </div>

                    <div className="video-row-actions">
                      <button className="action-btn" onClick={() => navigate(`/video/${video.id}`)}>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                          <path d="M1 12C1 12 5 4 12 4C19 4 23 12 23 12C23 12 19 20 12 20C5 20 1 12 1 12Z" stroke="currentColor" strokeWidth="2"/>
                          <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CreatorDashboard;

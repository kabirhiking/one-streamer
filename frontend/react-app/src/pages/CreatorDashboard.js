import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { videoApi } from '../api/axios';

const CreatorDashboard = () => {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user && user.is_creator) {
      fetchAnalytics();
    }
  }, [user]);

  const fetchAnalytics = async () => {
    try {
      const response = await videoApi.get('/api/analytics/creator');
      setAnalytics(response.data);
    } catch (err) {
      console.error('Failed to fetch analytics', err);
    } finally {
      setLoading(false);
    }
  };

  if (!user || !user.is_creator) {
    return (
      <div className="container">
        <p>Only creators can access the dashboard.</p>
      </div>
    );
  }

  if (loading) {
    return <div className="loading">Loading analytics...</div>;
  }

  return (
    <div className="container">
      <h2 className="page-title">Creator Dashboard</h2>

      {analytics && (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total Videos</h3>
              <p className="stat-value">{analytics.total_videos}</p>
            </div>
            <div className="stat-card">
              <h3>Total Views</h3>
              <p className="stat-value">{analytics.total_views.toLocaleString()}</p>
            </div>
            <div className="stat-card">
              <h3>Total Likes</h3>
              <p className="stat-value">{analytics.total_likes.toLocaleString()}</p>
            </div>
            <div className="stat-card">
              <h3>Total Comments</h3>
              <p className="stat-value">{analytics.total_comments.toLocaleString()}</p>
            </div>
          </div>

          <h3 style={{ marginTop: '40px', marginBottom: '20px' }}>Your Videos</h3>
          <div className="video-list">
            {analytics.videos.map(video => (
              <div key={video.id} className="video-list-item">
                <h4>{video.title}</h4>
                <div className="video-list-stats">
                  <span>{video.views} views</span>
                  <span>{video.likes} likes</span>
                  <span>{new Date(video.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default CreatorDashboard;

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { videoApi } from '../api/axios';

const Home = () => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      const response = await videoApi.get('/api/videos/');
      setVideos(response.data.videos);
    } catch (err) {
      setError('Failed to load videos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading videos...</div>;
  }

  if (error) {
    return <div className="container"><p className="error-message">{error}</p></div>;
  }

  return (
    <div className="container">
      <h2 className="page-title">Explore Videos</h2>
      
      {videos.length === 0 ? (
        <p>No videos available yet.</p>
      ) : (
        <div className="video-grid">
          {videos.map((video) => (
            <Link to={`/video/${video.id}`} key={video.id} className="video-card">
              <img
                src={video.thumbnail || '/placeholder.jpg'}
                alt={video.title}
                className="video-thumbnail"
              />
              <div className="video-info">
                <h3 className="video-title">{video.title}</h3>
                <div className="video-meta">
                  <span>{video.views_count} views</span>
                  <span> • </span>
                  <span>{new Date(video.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default Home;

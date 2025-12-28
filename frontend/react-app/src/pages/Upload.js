import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { videoApi } from '../api/axios';

const Upload = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    visibility: 'public'
  });
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  if (!user) {
    return (
      <div className="container">
        <p>Please login to upload videos.</p>
      </div>
    );
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a video file');
      return;
    }

    setUploading(true);
    setError('');
    setSuccess('');

    const uploadData = new FormData();
    uploadData.append('file', file);
    uploadData.append('title', formData.title);
    uploadData.append('description', formData.description);
    uploadData.append('visibility', formData.visibility);

    try {
      const response = await videoApi.post('/api/upload/', uploadData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setProgress(percentCompleted);
        },
      });

      setSuccess('Video uploaded successfully! Processing...');
      setTimeout(() => {
        navigate(`/video/${response.data.video_id}`);
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="form-container">
      <h2 className="page-title">Upload Video</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Video File</label>
          <input
            type="file"
            accept="video/*"
            onChange={handleFileChange}
            required
            disabled={uploading}
          />
        </div>

        <div className="form-group">
          <label>Title</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            disabled={uploading}
          />
        </div>

        <div className="form-group">
          <label>Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            disabled={uploading}
          />
        </div>

        <div className="form-group">
          <label>Visibility</label>
          <select
            name="visibility"
            value={formData.visibility}
            onChange={handleChange}
            disabled={uploading}
          >
            <option value="public">Public</option>
            <option value="unlisted">Unlisted</option>
            <option value="private">Private</option>
          </select>
        </div>

        {uploading && (
          <div className="progress-bar">
            <div className="progress" style={{ width: `${progress}%` }}>
              {progress}%
            </div>
          </div>
        )}

        {error && <p className="error-message">{error}</p>}
        {success && <p className="success-message">{success}</p>}

        <button 
          type="submit" 
          className="btn btn-primary btn-full" 
          disabled={uploading}
        >
          {uploading ? `Uploading... ${progress}%` : 'Upload Video'}
        </button>
      </form>
    </div>
  );
};

export default Upload;

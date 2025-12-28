import React from 'react';
import { useAuth } from '../context/AuthContext';

const Profile = () => {
  const { user } = useAuth();

  if (!user) {
    return <div className="container">Please login to view profile.</div>;
  }

  return (
    <div className="container">
      <div className="form-container">
        <h2 className="page-title">Profile</h2>
        
        <div className="profile-info">
          <div className="form-group">
            <label>Email</label>
            <p>{user.email}</p>
          </div>

          <div className="form-group">
            <label>Display Name</label>
            <p>{user.display_name || 'Not set'}</p>
          </div>

          <div className="form-group">
            <label>Account Type</label>
            <p>{user.is_creator ? 'Creator' : 'Viewer'}</p>
          </div>

          {user.is_creator && (
            <>
              <div className="form-group">
                <label>Channel Name</label>
                <p>{user.channel_name}</p>
              </div>

              <div className="form-group">
                <label>Subscribers</label>
                <p>{user.subscribers_count}</p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;

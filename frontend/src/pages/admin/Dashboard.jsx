import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalLeads: 0,
    newLeads: 0,
    contacted: 0,
    closed: 0
  });

  useEffect(() => {
    // Fetch stats from API
    fetch('http://localhost:8000/api/leads/statistics')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const s = data.statistics;
          setStats({
            totalLeads: s.total || 0,
            newLeads: s.by_status?.NEW || 0,
            contacted: s.by_status?.CONTACTED || 0,
            closed: s.by_status?.CLOSED || 0
          });
        }
      })
      .catch(err => console.error('Error fetching stats:', err));
  }, []);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
      {/* Navigation */}
      <nav style={{ backgroundColor: '#ffffff', borderBottom: '1px solid #e2e8f0', padding: '0 24px' }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '64px' }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none' }}>
            <div style={{ width: '40px', height: '40px', background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ffffff', fontWeight: '700', fontSize: '16px' }}>
              IL
            </div>
            <div>
              <div style={{ fontSize: '18px', fontWeight: '700', color: '#0f172a' }}>InstaLogic</div>
              <div style={{ fontSize: '12px', color: '#64748b' }}>Admin Dashboard</div>
            </div>
          </Link>
          
          <div style={{ display: 'flex', gap: '16px' }}>
            <Link to="/admin/dashboard" style={{ padding: '8px 16px', backgroundColor: '#eff6ff', color: '#1e40af', borderRadius: '6px', textDecoration: 'none', fontSize: '14px', fontWeight: '600' }}>
              Dashboard
            </Link>
            <Link to="/admin/leads" style={{ padding: '8px 16px', color: '#475569', borderRadius: '6px', textDecoration: 'none', fontSize: '14px', fontWeight: '600' }}>
              Leads
            </Link>
            <Link to="/" style={{ padding: '8px 16px', backgroundColor: '#f1f5f9', color: '#475569', borderRadius: '6px', textDecoration: 'none', fontSize: '14px', fontWeight: '600' }}>
              ← Back to Site
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '32px 24px' }}>
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '32px', fontWeight: '800', color: '#0f172a', marginBottom: '8px' }}>
            Admin Dashboard
          </h1>
          <p style={{ fontSize: '16px', color: '#64748b' }}>
            Overview of your leads and customer interactions
          </p>
        </div>

        {/* Stats Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '32px' }}>
          <div style={{ backgroundColor: '#ffffff', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '16px' }}>
              <div style={{ width: '48px', height: '48px', backgroundColor: '#dbeafe', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px' }}>
                📊
              </div>
              <span style={{ padding: '4px 12px', backgroundColor: '#d1fae5', color: '#065f46', fontSize: '12px', fontWeight: '600', borderRadius: '6px' }}>
                Total
              </span>
            </div>
            <h3 style={{ fontSize: '36px', fontWeight: '700', color: '#0f172a', marginBottom: '8px' }}>
              {stats.totalLeads}
            </h3>
            <p style={{ fontSize: '14px', color: '#64748b' }}>Total Leads</p>
          </div>

          <div style={{ backgroundColor: '#ffffff', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '16px' }}>
              <div style={{ width: '48px', height: '48px', backgroundColor: '#fef3c7', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px' }}>
                ⭐
              </div>
              <span style={{ padding: '4px 12px', backgroundColor: '#fef3c7', color: '#92400e', fontSize: '12px', fontWeight: '600', borderRadius: '6px' }}>
                New
              </span>
            </div>
            <h3 style={{ fontSize: '36px', fontWeight: '700', color: '#0f172a', marginBottom: '8px' }}>
              {stats.newLeads}
            </h3>
            <p style={{ fontSize: '14px', color: '#64748b' }}>New Leads</p>
          </div>

          <div style={{ backgroundColor: '#ffffff', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '16px' }}>
              <div style={{ width: '48px', height: '48px', backgroundColor: '#e9d5ff', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px' }}>
                💬
              </div>
              <span style={{ padding: '4px 12px', backgroundColor: '#e9d5ff', color: '#6b21a8', fontSize: '12px', fontWeight: '600', borderRadius: '6px' }}>
                Active
              </span>
            </div>
            <h3 style={{ fontSize: '36px', fontWeight: '700', color: '#0f172a', marginBottom: '8px' }}>
              {stats.contacted}
            </h3>
            <p style={{ fontSize: '14px', color: '#64748b' }}>Contacted</p>
          </div>

          <div style={{ backgroundColor: '#ffffff', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '16px' }}>
              <div style={{ width: '48px', height: '48px', backgroundColor: '#d1fae5', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px' }}>
                ✅
              </div>
              <span style={{ padding: '4px 12px', backgroundColor: '#d1fae5', color: '#065f46', fontSize: '12px', fontWeight: '600', borderRadius: '6px' }}>
                Closed
              </span>
            </div>
            <h3 style={{ fontSize: '36px', fontWeight: '700', color: '#0f172a', marginBottom: '8px' }}>
              {stats.closed}
            </h3>
            <p style={{ fontSize: '14px', color: '#64748b' }}>Deals Closed</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div style={{ backgroundColor: '#ffffff', padding: '32px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#0f172a', marginBottom: '20px' }}>
            Quick Actions
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <Link to="/admin/leads" style={{ padding: '20px', backgroundColor: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0', textDecoration: 'none', textAlign: 'center', transition: 'all 0.2s' }}>
              <div style={{ fontSize: '32px', marginBottom: '12px' }}>👥</div>
              <div style={{ fontSize: '16px', fontWeight: '600', color: '#0f172a' }}>View All Leads</div>
            </Link>
            
            <div style={{ padding: '20px', backgroundColor: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0', textAlign: 'center', cursor: 'pointer' }}>
              <div style={{ fontSize: '32px', marginBottom: '12px' }}>📊</div>
              <div style={{ fontSize: '16px', fontWeight: '600', color: '#0f172a' }}>Generate Report</div>
            </div>
            
            <div style={{ padding: '20px', backgroundColor: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0', textAlign: 'center', cursor: 'pointer' }}>
              <div style={{ fontSize: '32px', marginBottom: '12px' }}>⚙️</div>
              <div style={{ fontSize: '16px', fontWeight: '600', color: '#0f172a' }}>Settings</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;


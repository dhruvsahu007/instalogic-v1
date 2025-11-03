import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const Leads = () => {
  const [leads, setLeads] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [adminNotes, setAdminNotes] = useState('');
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });

  const showToast = (message, type = 'success') => {
    setToast({ show: true, message, type });
    setTimeout(() => {
      setToast({ show: false, message: '', type: 'success' });
    }, 3000);
  };

  useEffect(() => {
    fetchLeads();
  }, [filterStatus]);

  useEffect(() => {
    if (selectedLead) {
      setAdminNotes(selectedLead.adminNotes || '');
    }
  }, [selectedLead]);

  const fetchLeads = () => {
    const url = filterStatus === 'ALL' 
      ? 'http://localhost:8000/api/leads'
      : `http://localhost:8000/api/leads?status=${filterStatus}`;
    
    fetch(url)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setLeads(data.leads);
          if (data.leads.length > 0 && !selectedLead) {
            setSelectedLead(data.leads[0]);
          }
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching leads:', err);
        setLoading(false);
      });
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'NEW': return { bg: '#dbeafe', text: '#1e40af', border: '#93c5fd' };
      case 'CONTACTED': return { bg: '#e9d5ff', text: '#7e22ce', border: '#c084fc' };
      case 'IN_PROGRESS': return { bg: '#fef3c7', text: '#92400e', border: '#fcd34d' };
      case 'CLOSED': return { bg: '#d1fae5', text: '#065f46', border: '#6ee7b7' };
      default: return { bg: '#f3f4f6', text: '#374151', border: '#d1d5db' };
    }
  };

  const getTypeIcon = (type) => {
    switch(type) {
      case 'DEMO_REQUEST': return '🎯';
      case 'HUMAN_HANDOFF': return '🆘';
      case 'RFP_UPLOAD': return '📄';
      case 'CAREER_APPLICATION': return '💼';
      default: return '📋';
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return 'N/A';
    }
  };

  const handleSaveNotes = async () => {
    if (!selectedLead) return;
    
    setSaving(true);
    try {
      const response = await fetch(`http://localhost:8000/api/leads/${selectedLead.id}/notes?notes=${encodeURIComponent(adminNotes)}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const data = await response.json();
      
      if (data.success) {
        // Update local state
        setLeads(leads.map(lead => 
          lead.id === selectedLead.id 
            ? { ...lead, adminNotes: adminNotes }
            : lead
        ));
        setSelectedLead({ ...selectedLead, adminNotes: adminNotes });
        showToast('Notes saved successfully!', 'success');
      } else {
        showToast('Failed to save notes', 'error');
      }
    } catch (error) {
      console.error('Error saving notes:', error);
      showToast('Error saving notes', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateStatus = async (newStatus) => {
    if (!selectedLead) return;
    
    try {
      const response = await fetch(`http://localhost:8000/api/leads/${selectedLead.id}/status?status=${newStatus}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const data = await response.json();
      
      if (data.success) {
        // Update local state
        setLeads(leads.map(lead => 
          lead.id === selectedLead.id 
            ? { ...lead, status: newStatus }
            : lead
        ));
        setSelectedLead({ ...selectedLead, status: newStatus });
        showToast(`Lead marked as ${newStatus}!`, 'success');
        
        // Refresh leads if filter is active
        if (filterStatus !== 'ALL') {
          fetchLeads();
        }
      } else {
        showToast('Failed to update status', 'error');
      }
    } catch (error) {
      console.error('Error updating status:', error);
      showToast('Error updating status', 'error');
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ width: '48px', height: '48px', border: '4px solid #e2e8f0', borderTopColor: '#3b82f6', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 16px' }} />
          <p style={{ fontSize: '16px', color: '#64748b' }}>Loading leads...</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
      {/* Navigation */}
      <nav style={{ backgroundColor: '#ffffff', borderBottom: '1px solid #e2e8f0', padding: '0 24px' }}>
        <div style={{ maxWidth: '1600px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '64px' }}>
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
            <Link to="/admin/dashboard" style={{ padding: '8px 16px', color: '#475569', borderRadius: '6px', textDecoration: 'none', fontSize: '14px', fontWeight: '600' }}>
              Dashboard
            </Link>
            <Link to="/admin/leads" style={{ padding: '8px 16px', backgroundColor: '#eff6ff', color: '#1e40af', borderRadius: '6px', textDecoration: 'none', fontSize: '14px', fontWeight: '600' }}>
              Leads
            </Link>
            <Link to="/" style={{ padding: '8px 16px', backgroundColor: '#f1f5f9', color: '#475569', borderRadius: '6px', textDecoration: 'none', fontSize: '14px', fontWeight: '600' }}>
              ← Back to Site
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div style={{ display: 'flex', height: 'calc(100vh - 64px)' }}>
        
        {/* Left Sidebar - Filters */}
        <div style={{ width: '280px', backgroundColor: '#ffffff', borderRight: '1px solid #e2e8f0', padding: '24px', overflowY: 'auto' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#0f172a', marginBottom: '20px' }}>
            Filter Leads
          </h2>
          
          <div style={{ marginBottom: '16px' }}>
            <label style={{ fontSize: '14px', fontWeight: '600', color: '#475569', marginBottom: '8px', display: 'block' }}>
              Status
            </label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              style={{ width: '100%', padding: '10px 12px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', fontSize: '14px', cursor: 'pointer', outline: 'none' }}
            >
              <option value="ALL">All Leads ({leads.length})</option>
              <option value="NEW">New</option>
              <option value="CONTACTED">Contacted</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="CLOSED">Closed</option>
            </select>
          </div>

          <div style={{ padding: '16px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <p style={{ fontSize: '12px', color: '#64748b', marginBottom: '8px' }}>Total Leads</p>
            <p style={{ fontSize: '32px', fontWeight: '700', color: '#0f172a' }}>{leads.length}</p>
          </div>
        </div>

        {/* Middle - Leads List */}
        <div style={{ flex: 1, padding: '24px', overflowY: 'auto', backgroundColor: '#f8fafc' }}>
          <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#0f172a', marginBottom: '20px' }}>
            Leads Management
          </h1>

          {leads.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '60px 20px', backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
              <div style={{ fontSize: '64px', marginBottom: '16px' }}>📭</div>
              <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#0f172a', marginBottom: '8px' }}>No leads found</h3>
              <p style={{ fontSize: '14px', color: '#64748b' }}>No leads match your current filter</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {leads.map(lead => {
                const isSelected = selectedLead?.id === lead.id;
                const statusColor = getStatusColor(lead.status);
                
                return (
                  <div
                    key={lead.id}
                    onClick={() => setSelectedLead(lead)}
                    style={{
                      padding: '20px',
                      backgroundColor: '#ffffff',
                      borderRadius: '12px',
                      border: isSelected ? '2px solid #3b82f6' : '1px solid #e2e8f0',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      boxShadow: isSelected ? '0 4px 6px -1px rgba(59, 130, 246, 0.1)' : 'none'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'start', justifyContent: 'space-between', marginBottom: '12px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ fontSize: '32px' }}>{getTypeIcon(lead.type)}</div>
                        <div>
                          <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#0f172a', marginBottom: '4px' }}>
                            {lead.name}
                          </h3>
                          <p style={{ fontSize: '14px', color: '#64748b' }}>{lead.contact}</p>
                        </div>
                      </div>
                      <span style={{
                        padding: '6px 12px',
                        fontSize: '12px',
                        fontWeight: '700',
                        borderRadius: '6px',
                        backgroundColor: statusColor.bg,
                        color: statusColor.text,
                        border: `1px solid ${statusColor.border}`
                      }}>
                        {lead.status}
                      </span>
                    </div>
                    
                    <p style={{ fontSize: '14px', color: '#475569', marginBottom: '12px' }}>
                      {lead.info || 'No details available'}
                    </p>
                    
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '12px', color: '#94a3b8' }}>
                      <span>{lead.type.replace(/_/g, ' ')}</span>
                      <span>{formatDate(lead.requestedDate)}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Panel - Lead Details */}
        {selectedLead && (
          <div style={{ width: '400px', backgroundColor: '#ffffff', borderLeft: '1px solid #e2e8f0', padding: '24px', overflowY: 'auto' }}>
            <div style={{ marginBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <div style={{ fontSize: '48px' }}>{getTypeIcon(selectedLead.type)}</div>
                <div>
                  <h2 style={{ fontSize: '20px', fontWeight: '700', color: '#0f172a', marginBottom: '4px' }}>
                    {selectedLead.name}
                  </h2>
                  <span style={{
                    ...getStatusColor(selectedLead.status),
                    padding: '4px 12px',
                    fontSize: '12px',
                    fontWeight: '700',
                    borderRadius: '6px',
                    display: 'inline-block',
                    border: `1px solid ${getStatusColor(selectedLead.status).border}`
                  }}>
                    {selectedLead.status}
                  </span>
                </div>
              </div>
            </div>

            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0f172a', marginBottom: '12px' }}>
                Contact Information
              </h3>
              <div style={{ padding: '16px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <p style={{ fontSize: '14px', color: '#475569', wordBreak: 'break-all' }}>
                  {selectedLead.contact}
                </p>
              </div>
            </div>

            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0f172a', marginBottom: '12px' }}>
                Details
              </h3>
              <div style={{ padding: '16px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <p style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6' }}>
                  {selectedLead.info || 'No additional information provided'}
                </p>
              </div>
            </div>

            {selectedLead.ticketId && (
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0f172a', marginBottom: '12px' }}>
                  Ticket ID
                </h3>
                <div style={{ padding: '12px 16px', backgroundColor: '#eff6ff', borderRadius: '8px', border: '1px solid #93c5fd' }}>
                  <p style={{ fontSize: '16px', color: '#1e40af', fontWeight: '600', fontFamily: 'monospace' }}>
                    {selectedLead.ticketId}
                  </p>
                </div>
              </div>
            )}

            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0f172a', marginBottom: '12px' }}>
                Admin Notes
              </h3>
              <textarea
                value={adminNotes}
                onChange={(e) => setAdminNotes(e.target.value)}
                placeholder="Add notes about this lead..."
                style={{
                  width: '100%',
                  minHeight: '100px',
                  padding: '12px',
                  backgroundColor: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '14px',
                  color: '#475569',
                  resize: 'vertical',
                  outline: 'none'
                }}
              />
              <button 
                onClick={handleSaveNotes}
                disabled={saving}
                style={{
                  marginTop: '12px',
                  width: '100%',
                  padding: '10px',
                  backgroundColor: saving ? '#94a3b8' : '#3b82f6',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: saving ? 'not-allowed' : 'pointer',
                  opacity: saving ? 0.7 : 1
                }}
              >
                {saving ? 'Saving...' : 'Save Notes'}
              </button>
            </div>

            <div>
              <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0f172a', marginBottom: '12px' }}>
                Actions
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <button 
                  onClick={() => handleUpdateStatus('CONTACTED')}
                  style={{ 
                    padding: '10px', 
                    backgroundColor: '#10b981', 
                    color: '#ffffff', 
                    border: 'none', 
                    borderRadius: '8px', 
                    fontSize: '14px', 
                    fontWeight: '600', 
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => e.target.style.backgroundColor = '#059669'}
                  onMouseOut={(e) => e.target.style.backgroundColor = '#10b981'}
                >
                  ✓ Mark as Contacted
                </button>
                <button 
                  onClick={() => handleUpdateStatus('IN_PROGRESS')}
                  style={{ 
                    padding: '10px', 
                    backgroundColor: '#f59e0b', 
                    color: '#ffffff', 
                    border: 'none', 
                    borderRadius: '8px', 
                    fontSize: '14px', 
                    fontWeight: '600', 
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => e.target.style.backgroundColor = '#d97706'}
                  onMouseOut={(e) => e.target.style.backgroundColor = '#f59e0b'}
                >
                  ⏳ Mark In Progress
                </button>
                <button 
                  onClick={() => handleUpdateStatus('CLOSED')}
                  style={{ 
                    padding: '10px', 
                    backgroundColor: '#6366f1', 
                    color: '#ffffff', 
                    border: 'none', 
                    borderRadius: '8px', 
                    fontSize: '14px', 
                    fontWeight: '600', 
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => e.target.style.backgroundColor = '#4f46e5'}
                  onMouseOut={(e) => e.target.style.backgroundColor = '#6366f1'}
                >
                  ✅ Mark as Closed
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Toast Notification */}
      {toast.show && (
        <div style={{
          position: 'fixed',
          top: '24px',
          right: '24px',
          padding: '16px 24px',
          backgroundColor: toast.type === 'success' ? '#10b981' : '#ef4444',
          color: '#ffffff',
          borderRadius: '12px',
          boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)',
          zIndex: 9999,
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          animation: 'slideIn 0.3s ease-out',
          fontSize: '14px',
          fontWeight: '600',
          maxWidth: '400px'
        }}>
          <span style={{ fontSize: '20px' }}>
            {toast.type === 'success' ? '✅' : '❌'}
          </span>
          {toast.message}
        </div>
      )}
    </div>
  );
};

export default Leads;


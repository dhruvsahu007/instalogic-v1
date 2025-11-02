import React, { useState, useEffect } from 'react';
import AdminNav from './AdminNav';

const API_BASE_URL = 'http://localhost:8000/api';

const LeadsDashboard = () => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [statistics, setStatistics] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLead, setSelectedLead] = useState(null);
  const [showModal, setShowModal] = useState(false);

  // Fetch leads from API
  const fetchLeads = async (status = null) => {
    try {
      setLoading(true);
      const url = status && status !== 'ALL' 
        ? `${API_BASE_URL}/leads?status=${status}`
        : `${API_BASE_URL}/leads`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.success) {
        setLeads(data.leads);
      } else {
        setError('Failed to fetch leads');
      }
    } catch (err) {
      setError(`Error fetching leads: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Fetch statistics
  const fetchStatistics = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/leads/statistics`);
      const data = await response.json();
      
      if (data.success) {
        setStatistics(data.statistics);
      }
    } catch (err) {
      console.error('Error fetching statistics:', err);
    }
  };

  // Update lead status
  const updateLeadStatus = async (leadId, newStatus) => {
    try {
      const response = await fetch(`${API_BASE_URL}/leads/${leadId}/status?status=${newStatus}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        fetchLeads(filterStatus === 'ALL' ? null : filterStatus);
        fetchStatistics();
      } else {
        alert('Failed to update status');
      }
    } catch (err) {
      alert(`Error updating status: ${err.message}`);
    }
  };

  // Delete lead
  const deleteLead = async (leadId) => {
    if (!window.confirm('Are you sure you want to delete this lead?')) {
      return;
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/leads/${leadId}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        fetchLeads(filterStatus === 'ALL' ? null : filterStatus);
        fetchStatistics();
        setShowModal(false);
      } else {
        alert('Failed to delete lead');
      }
    } catch (err) {
      alert(`Error deleting lead: ${err.message}`);
    }
  };

  // Initial load
  useEffect(() => {
    fetchLeads();
    fetchStatistics();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchLeads(filterStatus === 'ALL' ? null : filterStatus);
      fetchStatistics();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Filter change
  useEffect(() => {
    fetchLeads(filterStatus === 'ALL' ? null : filterStatus);
  }, [filterStatus]);

  // Filter leads by search query
  const filteredLeads = leads.filter(lead => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      lead.name.toLowerCase().includes(query) ||
      lead.contact.toLowerCase().includes(query) ||
      lead.info?.toLowerCase().includes(query) ||
      lead.ticketId?.toLowerCase().includes(query)
    );
  });

  // Get status badge style
  const getStatusBadge = (status) => {
    const styles = {
      'NEW': 'bg-green-100 text-green-800 border-green-200',
      'CONTACTED': 'bg-blue-100 text-blue-800 border-blue-200',
      'IN_PROGRESS': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'CLOSED': 'bg-gray-100 text-gray-800 border-gray-200'
    };
    return styles[status] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  // Get lead type badge style
  const getLeadTypeBadge = (type) => {
    const styles = {
      'DEMO_REQUEST': 'bg-blue-50 text-blue-700 border-blue-200',
      'HUMAN_HANDOFF': 'bg-red-50 text-red-700 border-red-200',
      'RFP_UPLOAD': 'bg-purple-50 text-purple-700 border-purple-200',
      'CAREER_APPLICATION': 'bg-green-50 text-green-700 border-green-200'
    };
    return styles[type] || 'bg-gray-50 text-gray-700 border-gray-200';
  };

  // Format lead type for display
  const formatLeadType = (type) => {
    return type.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  };

  // Get channel icon
  const getChannelIcon = (type) => {
    if (type === 'DEMO_REQUEST') return '💼';
    if (type === 'HUMAN_HANDOFF') return '🆘';
    if (type === 'RFP_UPLOAD') return '📄';
    if (type === 'CAREER_APPLICATION') return '👔';
    return '📧';
  };

  // View lead details
  const viewDetails = (lead) => {
    setSelectedLead(lead);
    setShowModal(true);
  };

  if (loading && leads.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <AdminNav />
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading leads...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <AdminNav />
        <div className="flex items-center justify-center h-96">
          <div className="text-center max-w-md">
            <div className="text-red-600 text-5xl mb-4">⚠️</div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Leads</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <button 
              onClick={() => fetchLeads()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <AdminNav />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="text-sm text-gray-600 mb-1">Total Leads</div>
              <div className="text-3xl font-bold text-gray-900">{statistics.total}</div>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="text-sm text-gray-600 mb-1">New</div>
              <div className="text-3xl font-bold text-green-600">{statistics.by_status?.NEW || 0}</div>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="text-sm text-gray-600 mb-1">In Progress</div>
              <div className="text-3xl font-bold text-yellow-600">{statistics.by_status?.IN_PROGRESS || 0}</div>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="text-sm text-gray-600 mb-1">Closed</div>
              <div className="text-3xl font-bold text-gray-600">{statistics.by_status?.CLOSED || 0}</div>
            </div>
          </div>
        )}

        {/* Search and Filters */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4 items-stretch md:items-center justify-between">
            {/* Search */}
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search leads..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Status Filters */}
            <div className="flex gap-2 flex-wrap">
              {['ALL', 'NEW', 'CONTACTED', 'IN_PROGRESS', 'CLOSED'].map((status) => (
                <button
                  key={status}
                  onClick={() => setFilterStatus(status)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filterStatus === status
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {status.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          {filteredLeads.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 text-5xl mb-4">📭</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No leads found</h3>
              <p className="text-gray-600">
                {searchQuery ? 'Try adjusting your search' : 'Leads will appear here when users interact with the chatbot'}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Customer
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Channel
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredLeads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-gray-50 transition-colors">
                      {/* Customer */}
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 font-semibold">
                              {lead.name.substring(0, 2).toUpperCase()}
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{lead.name}</div>
                            <div className="text-sm text-gray-500">ID: {lead.ticketId || lead.id}</div>
                          </div>
                        </div>
                      </td>

                      {/* Channel */}
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-2xl">{getChannelIcon(lead.type)}</span>
                      </td>

                      {/* Type */}
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getLeadTypeBadge(lead.type)}`}>
                          {formatLeadType(lead.type)}
                        </span>
                      </td>

                      {/* Status */}
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getStatusBadge(lead.status)}`}>
                          {lead.status.toLowerCase()}
                        </span>
                      </td>

                      {/* Contact */}
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{lead.contact}</div>
                      </td>

                      {/* Last Contact */}
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(lead.requestedDate).toLocaleDateString('en-US', { 
                          month: 'short', 
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </td>

                      {/* Actions */}
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => viewDetails(lead)}
                          className="text-blue-600 hover:text-blue-900 border border-blue-300 px-4 py-1 rounded-lg hover:bg-blue-50 transition-colors"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Results count */}
        <div className="mt-4 text-sm text-gray-600">
          Showing {filteredLeads.length} of {leads.length} leads
        </div>
      </div>

      {/* Details Modal */}
      {showModal && selectedLead && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Lead Details</h2>
                <button
                  onClick={() => setShowModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Name</label>
                  <p className="mt-1 text-gray-900">{selectedLead.name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Contact</label>
                  <p className="mt-1 text-gray-900">{selectedLead.contact}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Type</label>
                  <p className="mt-1">
                    <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getLeadTypeBadge(selectedLead.type)}`}>
                      {formatLeadType(selectedLead.type)}
                    </span>
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Status</label>
                  <p className="mt-1">
                    <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full border ${getStatusBadge(selectedLead.status)}`}>
                      {selectedLead.status}
                    </span>
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Ticket ID</label>
                  <p className="mt-1 text-gray-900">{selectedLead.ticketId || selectedLead.id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Requested Date</label>
                  <p className="mt-1 text-gray-900">{new Date(selectedLead.requestedDate).toLocaleString()}</p>
                </div>
              </div>

              {/* Details */}
              {selectedLead.info && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Details</label>
                  <div className="mt-1 p-4 bg-gray-50 rounded-lg">
                    <p className="text-gray-900">{selectedLead.info}</p>
                  </div>
                </div>
              )}

              {/* Admin Notes */}
              <div>
                <label className="text-sm font-medium text-gray-500">Admin Notes</label>
                <div className="mt-1 p-4 bg-gray-50 rounded-lg">
                  <p className="text-gray-900">{selectedLead.adminNotes || 'No notes yet'}</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t">
                <select
                  value={selectedLead.status}
                  onChange={(e) => {
                    updateLeadStatus(selectedLead.id, e.target.value);
                    setSelectedLead({...selectedLead, status: e.target.value});
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="NEW">New</option>
                  <option value="CONTACTED">Contacted</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="CLOSED">Closed</option>
                </select>
                <button
                  onClick={() => deleteLead(selectedLead.id)}
                  className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Delete
                </button>
                <button
                  onClick={() => setShowModal(false)}
                  className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LeadsDashboard;

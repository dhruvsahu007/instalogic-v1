import React, { useState, useEffect } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInWithCustomToken, signInAnonymously, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, collection, onSnapshot, doc, updateDoc, query, orderBy } from 'firebase/firestore';

const ChatResponsesDashboard = () => {
  const [leads, setLeads] = useState([]);
  const [filteredLeads, setFilteredLeads] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [authInitialized, setAuthInitialized] = useState(false);
  const [editingNotes, setEditingNotes] = useState({});
  const [db, setDb] = useState(null);

  // Firebase configuration (from global variables)
  const firebaseConfig = window.__firebase_config || {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_AUTH_DOMAIN",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: window.__app_id || "YOUR_APP_ID"
  };

  const appId = window.__app_id || 'instalogic-chatbot';
  const initialAuthToken = window.__initial_auth_token || null;

  useEffect(() => {
    let unsubscribeAuth;
    let unsubscribeLeads;

    const initializeFirebase = async () => {
      try {
        // Initialize Firebase
        const app = initializeApp(firebaseConfig);
        const auth = getAuth(app);
        const firestore = getFirestore(app);
        setDb(firestore);

        // Set up auth state listener
        unsubscribeAuth = onAuthStateChanged(auth, async (user) => {
          if (user) {
            console.log('✅ User authenticated:', user.uid);
            setAuthInitialized(true);
            
            // Set up real-time listener for leads
            const leadsPath = `artifacts/${appId}/public/data/chatbot_leads`;
            const leadsRef = collection(firestore, leadsPath);
            const q = query(leadsRef, orderBy('requestedDate', 'desc'));

            unsubscribeLeads = onSnapshot(
              q,
              (snapshot) => {
                const leadsData = snapshot.docs.map(doc => ({
                  id: doc.id,
                  ...doc.data(),
                  requestedDate: doc.data().requestedDate?.toDate?.() || new Date()
                }));
                setLeads(leadsData);
                setFilteredLeads(leadsData);
                setLoading(false);
                console.log(`✅ Loaded ${leadsData.length} leads`);
              },
              (error) => {
                console.error('❌ Error fetching leads:', error);
                setLoading(false);
              }
            );
          } else {
            console.log('⚠️  No user authenticated, attempting sign in...');
            
            // Try to sign in
            try {
              if (initialAuthToken) {
                await signInWithCustomToken(auth, initialAuthToken);
                console.log('✅ Signed in with custom token');
              } else {
                await signInAnonymously(auth);
                console.log('✅ Signed in anonymously');
              }
            } catch (error) {
              console.error('❌ Authentication failed:', error);
              setLoading(false);
            }
          }
        });

      } catch (error) {
        console.error('❌ Firebase initialization error:', error);
        setLoading(false);
      }
    };

    initializeFirebase();

    // Cleanup
    return () => {
      if (unsubscribeAuth) unsubscribeAuth();
      if (unsubscribeLeads) unsubscribeLeads();
    };
  }, []);

  // Filter leads based on status
  useEffect(() => {
    if (filter === 'ALL') {
      setFilteredLeads(leads);
    } else {
      setFilteredLeads(leads.filter(lead => lead.status === filter));
    }
  }, [filter, leads]);

  const handleUpdateStatus = async (id, newStatus) => {
    if (!db) return;

    try {
      const leadsPath = `artifacts/${appId}/public/data/chatbot_leads`;
      const docRef = doc(db, leadsPath, id);
      await updateDoc(docRef, { status: newStatus });
      console.log(`✅ Updated lead ${id} status to ${newStatus}`);
    } catch (error) {
      console.error('❌ Error updating status:', error);
      alert('Failed to update status. Please try again.');
    }
  };

  const handleSaveNote = async (id, newNote) => {
    if (!db) return;

    try {
      const leadsPath = `artifacts/${appId}/public/data/chatbot_leads`;
      const docRef = doc(db, leadsPath, id);
      await updateDoc(docRef, { adminNotes: newNote });
      console.log(`✅ Saved note for lead ${id}`);
      setEditingNotes(prev => ({ ...prev, [id]: '' }));
    } catch (error) {
      console.error('❌ Error saving note:', error);
      alert('Failed to save note. Please try again.');
    }
  };

  const getTypeColor = (type) => {
    const colors = {
      'DEMO_REQUEST': 'bg-blue-100 text-blue-800 border-blue-300',
      'HUMAN_HANDOFF': 'bg-red-100 text-red-800 border-red-300',
      'RFP_UPLOAD': 'bg-purple-100 text-purple-800 border-purple-300',
      'CAREER_APPLICATION': 'bg-green-100 text-green-800 border-green-300'
    };
    return colors[type] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getStatusColor = (status) => {
    const colors = {
      'NEW': 'bg-yellow-500 text-white',
      'CONTACTED': 'bg-green-500 text-white',
      'IN_PROGRESS': 'bg-blue-500 text-white',
      'CLOSED': 'bg-gray-500 text-white'
    };
    return colors[status] || 'bg-gray-400 text-white';
  };

  const formatDate = (date) => {
    if (!date) return 'N/A';
    try {
      return new Date(date).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Invalid Date';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-700 font-semibold">Loading Chat Leads...</p>
          <p className="text-sm text-gray-500 mt-2">Connecting to Firebase</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-white rounded-2xl shadow-xl p-6 border-t-4 border-blue-600">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-800 flex items-center">
                <span className="text-blue-600 mr-3">💬</span>
                Chat Lead Dashboard
              </h1>
              <p className="text-gray-600 mt-2">
                Manage chatbot-generated leads in real-time
              </p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-blue-600">{leads.length}</div>
              <div className="text-sm text-gray-500">Total Leads</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="bg-white rounded-xl shadow-md p-4 flex flex-wrap gap-3">
          {['ALL', 'NEW', 'CONTACTED', 'IN_PROGRESS', 'CLOSED'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-6 py-2 rounded-lg font-semibold transition-all duration-200 ${
                filter === status
                  ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status.replace('_', ' ')}
              {status !== 'ALL' && (
                <span className="ml-2 bg-white text-blue-600 rounded-full px-2 py-0.5 text-xs">
                  {leads.filter(l => l.status === status).length}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Leads Grid */}
      <div className="max-w-7xl mx-auto">
        {filteredLeads.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-md p-12 text-center">
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-2xl font-semibold text-gray-700 mb-2">No Leads Found</h3>
            <p className="text-gray-500">
              {filter === 'ALL' 
                ? 'No leads have been generated yet.'
                : `No leads with status "${filter.replace('_', ' ')}".`}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredLeads.map((lead) => (
              <div
                key={lead.id}
                className="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 border-l-4 border-blue-600 overflow-hidden"
              >
                {/* Card Header */}
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4 text-white">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">
                        {lead.type === 'DEMO_REQUEST' && '🎯'}
                        {lead.type === 'HUMAN_HANDOFF' && '🆘'}
                        {lead.type === 'RFP_UPLOAD' && '📤'}
                        {lead.type === 'CAREER_APPLICATION' && '💼'}
                      </span>
                      <div>
                        <h3 className="font-bold text-lg">{lead.name}</h3>
                        <p className="text-blue-100 text-sm">{lead.contact}</p>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(lead.status)}`}>
                      {lead.status}
                    </span>
                  </div>
                </div>

                {/* Card Body */}
                <div className="p-6 space-y-4">
                  {/* Type Badge */}
                  <div className="flex items-center justify-between">
                    <span className={`px-3 py-1 rounded-lg text-xs font-semibold border ${getTypeColor(lead.type)}`}>
                      {lead.type.replace('_', ' ')}
                    </span>
                    {lead.ticketId && (
                      <span className="text-xs text-gray-500 font-mono bg-gray-100 px-2 py-1 rounded">
                        #{lead.ticketId}
                      </span>
                    )}
                  </div>

                  {/* Info */}
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <p className="text-sm text-gray-700 leading-relaxed">{lead.info}</p>
                  </div>

                  {/* Date */}
                  <div className="flex items-center text-xs text-gray-500">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {formatDate(lead.requestedDate)}
                  </div>

                  {/* Admin Notes */}
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">
                      Admin Notes:
                    </label>
                    <textarea
                      value={editingNotes[lead.id] !== undefined ? editingNotes[lead.id] : lead.adminNotes || ''}
                      onChange={(e) => setEditingNotes(prev => ({ ...prev, [lead.id]: e.target.value }))}
                      placeholder="Add internal notes..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm resize-none"
                      rows="2"
                    />
                    <button
                      onClick={() => handleSaveNote(lead.id, editingNotes[lead.id] || lead.adminNotes || '')}
                      className="w-full bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors duration-200"
                    >
                      💾 Save Note
                    </button>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2 pt-2">
                    {lead.status === 'NEW' && (
                      <button
                        onClick={() => handleUpdateStatus(lead.id, 'CONTACTED')}
                        className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors duration-200"
                      >
                        ✓ Mark as Contacted
                      </button>
                    )}
                    {lead.status === 'CONTACTED' && (
                      <button
                        onClick={() => handleUpdateStatus(lead.id, 'IN_PROGRESS')}
                        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors duration-200"
                      >
                        ⟳ In Progress
                      </button>
                    )}
                    {lead.status === 'IN_PROGRESS' && (
                      <button
                        onClick={() => handleUpdateStatus(lead.id, 'CLOSED')}
                        className="flex-1 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors duration-200"
                      >
                        ✖ Close
                      </button>
                    )}
                    {lead.status === 'CLOSED' && (
                      <button
                        onClick={() => handleUpdateStatus(lead.id, 'NEW')}
                        className="flex-1 bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors duration-200"
                      >
                        ↺ Reopen
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="max-w-7xl mx-auto mt-8 text-center text-gray-600 text-sm">
        <p>🔄 Real-time updates via Firebase Firestore</p>
        <p className="mt-1">Powered by InstaLogic AI Chatbot</p>
      </div>
    </div>
  );
};

export default ChatResponsesDashboard;

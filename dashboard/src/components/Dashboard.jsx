// src/components/Dashboard.jsx
// Main dashboard component for AI-IDS

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';
import Statistics from './Statistics';
import PerformanceMetrics from './PerformanceMetrics';
import DetectionTable from './DetectionTable';
import api from '../services/api';

// Helper to resolve components that may be wrapped as { default: Component }
const _resolveComp = (c) => (c && c.default) ? c.default : c;

const Dashboard = () => {
  // State management
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [detectionResults, setDetectionResults] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [filter, setFilter] = useState('all');

  // Runtime validation: ensure imported components are valid React components
  useEffect(() => {
    try {
      // Helpful console output for debugging component import issues
      console.log('Dashboard imports:', {
        Statistics,
        PerformanceMetrics,
        DetectionTable,
      });

      const invalid = [];
      const isComponent = (c) => typeof c === 'function' || (c && typeof c === 'object');
      const S = _resolveComp(Statistics);
      const P = _resolveComp(PerformanceMetrics);
      const D = _resolveComp(DetectionTable);

      if (!isComponent(S)) invalid.push('Statistics');
      if (!isComponent(P)) invalid.push('PerformanceMetrics');
      if (!isComponent(D)) invalid.push('DetectionTable');

      if (invalid.length) {
        setError(`Invalid component imports: ${invalid.join(', ')}. Check exports/imports and restart dev server.`);
        setLoading(false);
      }
    } catch (e) {
      console.error('Component validation failed:', e);
    }
  }, []);

  // Note: we use the imported components directly (they are validated above)

  const fetchDetectionResults = useCallback(async () => {
    try {
      const results = await api.getDetectionResults(currentPage, 20, filter);
      setDetectionResults(results);
    } catch (err) {
      console.error('Detection results fetch error:', err);
    }
  }, [currentPage, filter]);

  // Fetch dashboard data on component mount
  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Fetch detection results when page or filter changes (stable callback)
  useEffect(() => {
    fetchDetectionResults();
  }, [fetchDetectionResults]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch summary data
      const summary = await api.getDashboardSummary();
      setDashboardData(summary);

      setLoading(false);
    } catch (err) {
      console.error('Dashboard data fetch error:', err);
      
      // Create default data structure to at least show something
      const defaultData = {
        detection: {
          total_events: 0,
          normal_events: 0,
          anomalous_events: 0,
          anomaly_rate: 0
        },
        performance: {
          accuracy: 0,
          precision: 0,
          recall: 0,
          f1_score: 0,
          detection_rate: 0,
          false_positive_rate: 0
        }
      };
      
      setDashboardData(defaultData);
      setError('Unable to connect to backend. Make sure the Flask server is running on http://localhost:5000');
      setLoading(false);
    }
  };


  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const handleFilterChange = (newFilter) => {
    setFilter(newFilter);
    setCurrentPage(1); // Reset to first page when filter changes
  };

  const handleRefresh = () => {
    fetchDashboardData();
    fetchDetectionResults();
  };

  // Loading state
  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading Dashboard...
        </Typography>
      </Box>
    );
  }

  // Error state
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom>Fallback Data</Typography>
          <Typography variant="body2" color="text.secondary">
            Using cached data from the last training run...
          </Typography>
          {dashboardData && (
            <Box sx={{ mt: 3 }}>
              <Statistics data={dashboardData} onRefresh={handleRefresh} />
            </Box>
          )}
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          AI-IDS Dashboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Autonomous Intrusion Detection System - Iteration 1
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Statistics data={dashboardData} onRefresh={handleRefresh} />

      {/* Performance Metrics */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <PerformanceMetrics data={dashboardData} />
        </Grid>
      </Grid>

      {/* Detection Results Table */}
      <Box sx={{ mt: 4 }}>
        <DetectionTable
          results={detectionResults}
          currentPage={currentPage}
          filter={filter}
          onPageChange={handlePageChange}
          onFilterChange={handleFilterChange}
        />
      </Box>

      {/* Model Info Footer */}
      {dashboardData?.model && (
        <Paper sx={{ p: 2, mt: 4, bgcolor: 'background.default' }}>
          <Typography variant="body2" color="text.secondary">
            <strong>Model:</strong> {dashboardData.model.algorithm} |{' '}
            <strong>Status:</strong> {dashboardData.model.is_trained ? 'Trained' : 'Not Trained'} |{' '}
            <strong>Last Training:</strong> {new Date(dashboardData.model.training_date).toLocaleString()}
          </Typography>
        </Paper>
      )}
    </Container>
  );
};

export default Dashboard;
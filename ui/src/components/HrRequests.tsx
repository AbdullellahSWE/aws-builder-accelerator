import React, { useState } from 'react';
import { api } from '../services/api';
import type { AsyncRequestResponse } from '../types';

export const HrRequests: React.FC = () => {
  const [requestType, setRequestType] = useState<'time-off' | 'prompt'>('time-off');

  // Time off state
  const [userId, setUserId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Free-form prompt state
  const [promptUserId, setPromptUserId] = useState('');
  const [promptText, setPromptText] = useState('');

  // Execution state
  const [submitting, setSubmitting] = useState(false);
  const [response, setResponse] = useState<AsyncRequestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTimeOffSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId || !startDate || !endDate) return;

    setSubmitting(true);
    setError(null);
    setResponse(null);
    try {
      const result = await api.submitTimeOffRequest({
        user_id: userId,
        start_date: startDate,
        end_date: endDate,
      });
      setResponse(result);
    } catch (err: any) {
      setError(err.message || 'Failed to submit time-off request');
    } finally {
      setSubmitting(false);
    }
  };

  const handlePromptSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!promptUserId || !promptText) return;

    setSubmitting(true);
    setError(null);
    setResponse(null);
    try {
      const result = await api.submitHrPromptRequest({
        user_id: promptUserId,
        prompt: promptText,
      });
      setResponse(result);
    } catch (err: any) {
      setError(err.message || 'Failed to submit HR inquiry');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page-content">
      <div className="page-header-actions">
        <div>
          <h2 className="page-heading">Asynchronous HR Workflows</h2>
          <p className="page-subheading">
            Submit requests that trigger the AWS Step Functions event-driven architecture.
            Replies are computed and delivered via Amazon SNS email notifications.
          </p>
        </div>
      </div>

      <div className="type-toggle-bar">
        <button
          type="button"
          className={`toggle-btn ${requestType === 'time-off' ? 'active' : ''}`}
          onClick={() => {
            setRequestType('time-off');
            setResponse(null);
          }}
        >
          🏖️ Structured Time-Off Request
        </button>
        <button
          type="button"
          className={`toggle-btn ${requestType === 'prompt' ? 'active' : ''}`}
          onClick={() => {
            setRequestType('prompt');
            setResponse(null);
          }}
        >
          💬 Free-Form HR / Benefits Inquiry
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {response && (
        <div className="alert alert-success">
          <strong>✅ Workflow Execution Accepted (202):</strong>
          <p>Your request has been queued into the Step Functions state machine.</p>
          {response.executionArn && (
            <p>
              Execution ARN: <code>{response.executionArn}</code>
            </p>
          )}
          <p className="text-muted">
            Check your registered email inbox for the processed notification.
          </p>
        </div>
      )}

      <div className="card">
        {requestType === 'time-off' ? (
          <form onSubmit={handleTimeOffSubmit} className="form-grid">
            <h3 className="section-title">Submit Formal Time-Off Request</h3>
            <div className="form-group">
              <label htmlFor="user-id">Employee / User ID</label>
              <input
                id="user-id"
                type="text"
                placeholder="e.g. bce1bc5c"
                className="input-field"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                required
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="req-start-date">First Day of Absence</label>
                <input
                  id="req-start-date"
                  type="date"
                  className="input-field"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="req-end-date">Last Day of Absence</label>
                <input
                  id="req-end-date"
                  type="date"
                  className="input-field"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  required
                />
              </div>
            </div>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Triggering Workflow...' : 'Submit to Step Functions'}
            </button>
          </form>
        ) : (
          <form onSubmit={handlePromptSubmit} className="form-grid">
            <h3 className="section-title">Ask a General Benefits or HR Policy Question</h3>
            <div className="form-group">
              <label htmlFor="prompt-user-id">Employee / User ID</label>
              <input
                id="prompt-user-id"
                type="text"
                placeholder="e.g. bce1bc5c"
                className="input-field"
                value={promptUserId}
                onChange={(e) => setPromptUserId(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="prompt-text">Your Question or Request</label>
              <textarea
                id="prompt-text"
                rows={4}
                placeholder="e.g. What is the policy for parental leave roll-over into next quarter?"
                className="input-field"
                value={promptText}
                onChange={(e) => setPromptText(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Triggering Workflow...' : 'Submit to Step Functions'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};


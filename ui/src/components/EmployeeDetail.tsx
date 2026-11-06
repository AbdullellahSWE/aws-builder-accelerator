import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { Employee, LeaveRecord } from '../types';

interface EmployeeDetailProps {
  employee: Employee;
  onClose: () => void;
}

export const EmployeeDetail: React.FC<EmployeeDetailProps> = ({ employee, onClose }) => {
  const [leaveRecords, setLeaveRecords] = useState<LeaveRecord[]>([]);
  const [monthFilter, setMonthFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Booking leave form state
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [note, setNote] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [formSuccess, setFormSuccess] = useState<string | null>(null);

  const fetchLeave = async () => {
    setLoading(true);
    setError(null);
    try {
      const records = await api.listLeave(employee.employeeId, monthFilter || undefined);
      setLeaveRecords(records);
    } catch (err: any) {
      setError(err.message || 'Failed to load leave records');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeave();
  }, [employee.employeeId, monthFilter]);

  const handleBookLeave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!startDate || !endDate) return;

    setSubmitting(true);
    setError(null);
    setFormSuccess(null);
    try {
      await api.createLeave(employee.employeeId, {
        startDate,
        endDate,
        note,
      });
      setFormSuccess('Leave booked successfully!');
      setStartDate('');
      setEndDate('');
      setNote('');
      fetchLeave();
    } catch (err: any) {
      setError(err.message || 'Failed to book leave');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <h2 className="modal-title">{employee.name}</h2>
            <p className="modal-subtitle">
              ID: <code>{employee.employeeId}</code> • {employee.department} • Started {employee.startDate}
            </p>
          </div>
          <button type="button" className="close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
        {formSuccess && <div className="alert alert-success">{formSuccess}</div>}

        <div className="modal-body">
          {/* Leave booking form */}
          <section className="detail-section">
            <h3 className="section-title">📅 Book Time Off</h3>
            <form onSubmit={handleBookLeave} className="leave-form">
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="leave-start-date">Start Date</label>
                  <input
                    id="leave-start-date"
                    type="date"
                    className="input-field"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="leave-end-date">End Date</label>
                  <input
                    id="leave-end-date"
                    type="date"
                    className="input-field"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    required
                  />
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="leave-note">Note / Reason (optional)</label>
                <input
                  id="leave-note"
                  type="text"
                  placeholder="e.g. Annual leave, doctor appointment"
                  className="input-field"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                />
              </div>
              <button type="submit" className="btn-primary" disabled={submitting}>
                {submitting ? 'Booking...' : 'Submit Leave'}
              </button>
            </form>
          </section>

          {/* Leave History */}
          <section className="detail-section">
            <div className="section-header-split">
              <h3 className="section-title">📋 Leave Records</h3>
              <div className="filter-group">
                <label htmlFor="month-filter">Filter by Month:</label>
                <input
                  id="month-filter"
                  type="month"
                  className="input-field input-sm"
                  value={monthFilter}
                  onChange={(e) => setMonthFilter(e.target.value)}
                />
                {monthFilter && (
                  <button type="button" className="btn-text" onClick={() => setMonthFilter('')}>
                    Clear
                  </button>
                )}
              </div>
            </div>

            {loading ? (
              <p className="loading-state">Loading leave history...</p>
            ) : leaveRecords.length === 0 ? (
              <p className="empty-state">No leave records recorded for this period.</p>
            ) : (
              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Start Date</th>
                      <th>End Date</th>
                      <th>Note</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaveRecords.map((r, i) => (
                      <tr key={`${r.startDate}-${i}`}>
                        <td><strong>{r.startDate}</strong></td>
                        <td>{r.endDate}</td>
                        <td>{r.note || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
};


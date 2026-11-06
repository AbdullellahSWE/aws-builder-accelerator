import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { Employee, EmployeeCreatePayload } from '../types';
import { EmployeeDetail } from './EmployeeDetail';

export const EmployeeList: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Hire date filter
  const [hiredFrom, setHiredFrom] = useState('');
  const [hiredTo, setHiredTo] = useState('');

  // Selected employee for detail view
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);

  // Create modal state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newEmployee, setNewEmployee] = useState<EmployeeCreatePayload>({
    name: '',
    department: 'Engineering',
    startDate: new Date().toISOString().split('T')[0],
    role: 'employee',
  });
  const [creating, setCreating] = useState(false);

  const fetchEmployees = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listEmployees(
        hiredFrom && hiredTo ? hiredFrom : undefined,
        hiredFrom && hiredTo ? hiredTo : undefined
      );
      setEmployees(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load employees');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleApplyFilter = (e: React.FormEvent) => {
    e.preventDefault();
    fetchEmployees();
  };

  const handleClearFilter = () => {
    setHiredFrom('');
    setHiredTo('');
    setTimeout(fetchEmployees, 0);
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmployee.name || !newEmployee.department || !newEmployee.startDate) return;

    setCreating(true);
    setError(null);
    try {
      await api.createEmployee(newEmployee);
      setShowCreateModal(false);
      setNewEmployee({
        name: '',
        department: 'Engineering',
        startDate: new Date().toISOString().split('T')[0],
        role: 'employee',
      });
      fetchEmployees();
    } catch (err: any) {
      setError(err.message || 'Failed to create employee');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="page-content">
      <div className="page-header-actions">
        <div>
          <h2 className="page-heading">Employee Directory</h2>
          <p className="page-subheading">
            Browse corporate personnel, view leave records, and manage hiring dates.
          </p>
        </div>
        <button
          type="button"
          className="btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          ➕ Add Employee
        </button>
      </div>

      {/* Hire Date Filter Bar */}
      <div className="filter-card">
        <form onSubmit={handleApplyFilter} className="filter-bar">
          <span className="filter-title">🔍 Secondary Index Filter:</span>
          <div className="filter-inputs">
            <div className="input-with-label">
              <label htmlFor="hired-from">Hired From</label>
              <input
                id="hired-from"
                type="date"
                className="input-field input-sm"
                value={hiredFrom}
                onChange={(e) => setHiredFrom(e.target.value)}
              />
            </div>
            <div className="input-with-label">
              <label htmlFor="hired-to">Hired To</label>
              <input
                id="hired-to"
                type="date"
                className="input-field input-sm"
                value={hiredTo}
                onChange={(e) => setHiredTo(e.target.value)}
              />
            </div>
            <button type="submit" className="btn-secondary btn-sm" disabled={!hiredFrom || !hiredTo}>
              Filter by Date
            </button>
            {(hiredFrom || hiredTo) && (
              <button type="button" className="btn-text btn-sm" onClick={handleClearFilter}>
                Clear
              </button>
            )}
          </div>
        </form>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Directory Table */}
      {loading ? (
        <div className="card loading-card">
          <div className="spinner"></div>
          <p>Loading directory data from DynamoDB...</p>
        </div>
      ) : employees.length === 0 ? (
        <div className="card empty-card">
          <p>No employees match your search criteria.</p>
          {(hiredFrom || hiredTo) && (
            <button type="button" className="btn-secondary" onClick={handleClearFilter}>
              Reset Filters
            </button>
          )}
        </div>
      ) : (
        <div className="table-card">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Employee Name</th>
                <th>Department</th>
                <th>Role</th>
                <th>Start Date</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {employees.map((emp) => (
                <tr
                  key={emp.employeeId}
                  className="interactive-row"
                  onClick={() => setSelectedEmployee(emp)}
                >
                  <td>
                    <code className="id-badge">{emp.employeeId}</code>
                  </td>
                  <td>
                    <strong>{emp.name}</strong>
                  </td>
                  <td>
                    <span className="badge badge-dept">{emp.department}</span>
                  </td>
                  <td>
                    <span className="badge badge-role">{emp.role}</span>
                  </td>
                  <td>{emp.startDate}</td>
                  <td style={{ textAlign: 'right' }}>
                    <button
                      type="button"
                      className="btn-link"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedEmployee(emp);
                      }}
                    >
                      View & Book Leave →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Employee Detail Modal */}
      {selectedEmployee && (
        <EmployeeDetail
          employee={selectedEmployee}
          onClose={() => setSelectedEmployee(null)}
        />
      )}

      {/* Create Employee Modal */}
      {showCreateModal && (
        <div className="modal-backdrop" onClick={() => setShowCreateModal(false)}>
          <div className="modal-card modal-sm" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Add New Employee</h2>
              <button
                type="button"
                className="close-btn"
                onClick={() => setShowCreateModal(false)}
              >
                ✕
              </button>
            </div>
            <form onSubmit={handleCreateSubmit} className="modal-body form-grid">
              <div className="form-group">
                <label htmlFor="create-emp-name">Full Name</label>
                <input
                  id="create-emp-name"
                  type="text"
                  placeholder="e.g. Katherine Johnson"
                  className="input-field"
                  value={newEmployee.name}
                  onChange={(e) =>
                    setNewEmployee({ ...newEmployee, name: e.target.value })
                  }
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="create-emp-dept">Department</label>
                <select
                  id="create-emp-dept"
                  className="input-field"
                  value={newEmployee.department}
                  onChange={(e) =>
                    setNewEmployee({ ...newEmployee, department: e.target.value })
                  }
                >
                  <option value="Engineering">Engineering</option>
                  <option value="Finance">Finance</option>
                  <option value="Human Resources">Human Resources</option>
                  <option value="Marketing">Marketing</option>
                  <option value="Operations">Operations</option>
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="create-emp-start">Start Date</label>
                <input
                  id="create-emp-start"
                  type="date"
                  className="input-field"
                  value={newEmployee.startDate}
                  onChange={(e) =>
                    setNewEmployee({ ...newEmployee, startDate: e.target.value })
                  }
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="create-emp-role">Role</label>
                <select
                  id="create-emp-role"
                  className="input-field"
                  value={newEmployee.role}
                  onChange={(e) =>
                    setNewEmployee({ ...newEmployee, role: e.target.value })
                  }
                >
                  <option value="employee">Employee</option>
                  <option value="admin">Admin</option>
                  <option value="manager">Manager</option>
                </select>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={creating}>
                  {creating ? 'Saving...' : 'Create Employee'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};


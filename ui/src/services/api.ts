import { fetchAuthSession } from 'aws-amplify/auth';
import { config } from '../config';
import type {
  Employee,
  EmployeeCreatePayload,
  LeaveRecord,
  LeaveCreatePayload,
  TimeOffRequestPayload,
  HrRequestPayload,
  AsyncRequestResponse,
} from '../types';

async function getAuthHeaders(): Promise<Record<string, string>> {
  const session = await fetchAuthSession();
  const token = session.tokens?.idToken?.toString();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: token } : {}),
  };
}

export const api = {
  // Employee endpoints
  async listEmployees(hiredFrom?: string, hiredTo?: string): Promise<Employee[]> {
    const url = new URL(`${config.apiBaseUrl}/employees`);
    if (hiredFrom && hiredTo) {
      url.searchParams.append('hiredFrom', hiredFrom);
      url.searchParams.append('hiredTo', hiredTo);
    }

    const headers = await getAuthHeaders();
    const res = await fetch(url.toString(), { headers });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(`Failed to list employees: ${res.status} ${err}`);
    }
    const data = await res.json();
    return data.employees || [];
  },

  async getEmployee(employeeId: string): Promise<Employee> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${config.apiBaseUrl}/employees/${encodeURIComponent(employeeId)}`, {
      headers,
    });
    if (!res.ok) {
      throw new Error(`Employee not found (${res.status})`);
    }
    return res.json();
  },

  async createEmployee(payload: EmployeeCreatePayload): Promise<Employee> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${config.apiBaseUrl}/employees`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(`Failed to create employee: ${err}`);
    }
    return res.json();
  },

  // Leave endpoints
  async listLeave(employeeId: string, month?: string): Promise<LeaveRecord[]> {
    const url = new URL(`${config.apiBaseUrl}/employees/${encodeURIComponent(employeeId)}/leave`);
    if (month) {
      url.searchParams.append('month', month);
    }

    const headers = await getAuthHeaders();
    const res = await fetch(url.toString(), { headers });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(`Failed to list leave: ${err}`);
    }
    const data = await res.json();
    return data.leave || [];
  },

  async createLeave(employeeId: string, payload: LeaveCreatePayload): Promise<LeaveRecord> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${config.apiBaseUrl}/employees/${encodeURIComponent(employeeId)}/leave`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(`Failed to create leave request: ${err}`);
    }
    return res.json();
  },

  // Asynchronous Step Functions HR Requests
  async submitTimeOffRequest(payload: TimeOffRequestPayload): Promise<AsyncRequestResponse> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${config.apiBaseUrl}/hr-requests/time-off`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });
    if (!res.ok && res.status !== 202) {
      const err = await res.text();
      throw new Error(`Failed to submit time-off request: ${err}`);
    }
    return res.json();
  },

  async submitHrPromptRequest(payload: HrRequestPayload): Promise<AsyncRequestResponse> {
    const headers = await getAuthHeaders();
    const res = await fetch(`${config.apiBaseUrl}/hr-requests`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });
    if (!res.ok && res.status !== 202) {
      const err = await res.text();
      throw new Error(`Failed to submit HR prompt request: ${err}`);
    }
    return res.json();
  },
};


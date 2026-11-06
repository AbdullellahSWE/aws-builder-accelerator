export interface Employee {
  employeeId: string;
  name: string;
  department: string;
  startDate: string;
  role: string;
}

export interface EmployeeCreatePayload {
  name: string;
  department: string;
  startDate: string;
  role?: string;
}

export interface LeaveRecord {
  employeeId: string;
  startDate: string;
  endDate: string;
  note?: string;
}

export interface LeaveCreatePayload {
  startDate: string;
  endDate: string;
  note?: string;
}

export interface TimeOffRequestPayload {
  user_id: string;
  start_date: string;
  end_date: string;
}

export interface HrRequestPayload {
  user_id: string;
  prompt: string;
}

export interface AsyncRequestResponse {
  status: string;
  executionArn?: string;
  message?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  toolCalls?: string[];
  timestamp: string;
}


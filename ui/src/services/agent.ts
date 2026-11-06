import { fetchAuthSession } from 'aws-amplify/auth';
import { config } from '../config';

export function getOrCreateSessionId(): string {
  let sessionId = sessionStorage.getItem('hr_agent_session_id');
  if (!sessionId) {
    sessionId = `hr-session-${crypto.randomUUID()}`;
    sessionStorage.setItem('hr_agent_session_id', sessionId);
  }
  return sessionId;
}

export function resetAgentSession(): string {
  const newSessionId = `hr-session-${crypto.randomUUID()}`;
  sessionStorage.setItem('hr_agent_session_id', newSessionId);
  return newSessionId;
}

export interface StreamEventCallbacks {
  onToken: (text: string) => void;
  onToolCall?: (toolName: string) => void;
  onError?: (err: Error) => void;
  onDone?: () => void;
}

export async function invokeAgentStream(
  prompt: string,
  callbacks: StreamEventCallbacks,
  sessionId = getOrCreateSessionId()
): Promise<void> {
  const session = await fetchAuthSession();
  const token = session.tokens?.accessToken?.toString();
  if (!token) {
    throw new Error('Not authenticated with Cognito');
  }

  const encodedArn = encodeURIComponent(config.agentRuntimeArn);
  const agentUrl = `${config.agentEndpoint}/runtimes/${encodedArn}/invocations?qualifier=DEFAULT`;

  const response = await fetch(agentUrl, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      'X-Amzn-Bedrock-AgentCore-Runtime-Session-Id': sessionId,
    },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`AgentCore error (${response.status}): ${errorText}`);
  }

  if (!response.body) {
    throw new Error('No readable response body from agent');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith('data:')) continue;

        const jsonStr = trimmed.replace(/^data:\s*/, '');
        try {
          const parsed = JSON.parse(jsonStr);

          // Check for errors
          if (parsed.error) {
            throw new Error(parsed.error);
          }

          const event = parsed.event;
          if (!event) continue;

          // Handle text token delta
          const textDelta = event.contentBlockDelta?.delta?.text;
          if (textDelta) {
            callbacks.onToken(textDelta);
          }

          // Handle tool call start
          const toolStart = event.contentBlockStart?.start?.toolUse?.name;
          if (toolStart && callbacks.onToolCall) {
            callbacks.onToolCall(toolStart);
          }
        } catch (e) {
          // If JSON parse fails for a line, ignore or log
        }
      }
    }
  } catch (err: any) {
    callbacks.onError?.(err);
    throw err;
  } finally {
    callbacks.onDone?.();
  }
}


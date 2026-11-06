import { Amplify } from 'aws-amplify';

export const config = {
  apiBaseUrl: (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, ''),
  region: import.meta.env.VITE_AWS_REGION || 'us-east-1',
  userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID || '',
  userPoolClientId: import.meta.env.VITE_COGNITO_USER_POOL_CLIENT_ID || '',
  agentRuntimeArn: import.meta.env.VITE_AGENT_RUNTIME_ARN || '',
  agentEndpoint: (import.meta.env.VITE_AGENT_ENDPOINT || 'https://bedrock-agentcore.us-east-1.amazonaws.com').replace(/\/+$/, ''),
};

// Configure AWS Amplify with Cognito
Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: config.userPoolId,
      userPoolClientId: config.userPoolClientId,
    },
  },
});


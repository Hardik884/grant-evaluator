import type { Evaluation, Settings } from '../types/evaluation';

// Backend API base URL (normalize value so it always ends with '/api' and has no trailing slash)
const rawApiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
let API_BASE_URL = String(rawApiBase ?? '').replace(/\/+$/g, '');
if (!API_BASE_URL.endsWith('/api')) {
  API_BASE_URL = API_BASE_URL + '/api';
}

// Helper function for retrying failed requests
async function fetchWithRetry(url: string, options?: RequestInit, maxRetries = 2): Promise<Response> {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);
      return response;
    } catch (error) {
      lastError = error as Error;
      // Only retry on network errors, not on HTTP errors
      if (attempt < maxRetries && error instanceof TypeError) {
        // Wait before retrying (exponential backoff)
        await new Promise(resolve => setTimeout(resolve, 500 * Math.pow(2, attempt)));
        continue;
      }
      throw error;
    }
  }
  
  throw lastError || new Error('Request failed');
}

export const evaluationService = {
  async saveEvaluation(
    file: File,
    domain?: string,
    checkPlagiarism: boolean = false,
    sessionId?: string,
  ): Promise<Evaluation> {
    const formData = new FormData();
    formData.append('file', file);
    if (domain) {
      formData.append('domain', domain);
    }
    formData.append('check_plagiarism', checkPlagiarism.toString());
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    // Increased timeout for first-time model downloads (10 minutes)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 min timeout

    try {
      const response = await fetch(`${API_BASE_URL}/evaluations`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
        throw new Error(error.detail || 'Failed to evaluate grant');
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timeout: Backend took >10 min. First deployment may need time to download models (~500MB). Try again in a few minutes or check Render logs for memory/build issues.');
      }
      throw error;
    }
  },

  async getDomains(): Promise<string[]> {
    try {
      const response = await fetchWithRetry(`${API_BASE_URL}/domains`);

      if (!response.ok) {
        throw new Error('Failed to fetch domains');
      }

      const data = await response.json();
      return data.domains;
    } catch (error) {
      console.error('Error fetching domains:', error);
      // Return empty array instead of throwing to prevent blocking the UI
      return [];
    }
  },

  async getEvaluations(): Promise<Evaluation[]> {
    const response = await fetch(`${API_BASE_URL}/evaluations`);

    if (!response.ok) {
      throw new Error('Failed to fetch evaluations');
    }

    return await response.json();
  },

  async getEvaluationById(id: string): Promise<Evaluation | null> {
    const response = await fetch(`${API_BASE_URL}/evaluations/${id}`);

    if (!response.ok) {
      if (response.status === 404) {
        return null;
      }
      throw new Error('Failed to fetch evaluation');
    }

    return await response.json();
  },

  async getSettings(): Promise<Settings | null> {
    const response = await fetch(`${API_BASE_URL}/settings`);

    if (!response.ok) {
      throw new Error('Failed to fetch settings');
    }

    return await response.json();
  },

  async updateSettings(settings: Partial<Omit<Settings, 'id' | 'created_at' | 'updated_at'>>): Promise<Settings> {
    const response = await fetch(`${API_BASE_URL}/settings`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(settings),
    });

    if (!response.ok) {
      throw new Error('Failed to update settings');
    }

    return await response.json();
  },
};

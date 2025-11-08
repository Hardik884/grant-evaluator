import type { Evaluation, Settings } from '../types/evaluation';

// Backend API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

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

    const response = await fetch(`${API_BASE_URL}/evaluations`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to evaluate grant');
    }

    return await response.json();
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

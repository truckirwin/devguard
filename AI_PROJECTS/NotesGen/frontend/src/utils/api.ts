import axios from 'axios';
import { SlideContent, PPTFile, NoteVersion } from '../types/ppt';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getPPTContent = async (pptId: string): Promise<SlideContent[]> => {
  const response = await api.get(`/api/v1/ppt-files/content/${pptId}`);
  return response.data;
};

export const getNotes = async (pptId: string): Promise<NoteVersion[]> => {
  const response = await api.get(`/api/v1/notes/${pptId}`);
  return response.data;
};

export const updateNote = async (noteId: string, content: string): Promise<NoteVersion> => {
  const response = await api.put(`/api/v1/notes/${noteId}`, { content });
  return response.data;
};

export const generateNotes = async (pptId: string, slideNumber: number, content: string): Promise<string> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/v1/ai/notes`, {
      pptId,
      slideNumber,
      content,
    });
    return response.data;
  } catch (error) {
    throw new Error('Failed to generate notes');
  }
};

export const analyzeImage = async (file: File): Promise<string> => {
  try {
    const formData = new FormData();
    formData.append('image', file);
    
    const response = await axios.post(`${API_BASE_URL}/api/v1/ai/image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw new Error('Failed to analyze image');
  }
};

export const uploadPPTFile = async (file: File): Promise<PPTFile> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/api/v1/ppt-files/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};
